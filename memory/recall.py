"""Recall module: Semantic retrieval of historical incident memories from Hindsight or Demo Store."""

import datetime
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from database.db import log_memory_audit
from memory.hindsight_client import hindsight_manager
from utils.config import settings

logger = logging.getLogger("iris.memory.recall")


@dataclass
class RecallMatch:
    """Represents a retrieved historical incident memory."""
    memory_id: str
    incident_id: Optional[str]
    title: str
    category: str
    affected_system: str
    similarity_score: float  # 0.0 to 1.0
    root_cause: str
    steps_taken: str
    resolution: str
    relevance_explanation: str
    raw_content: str
    timestamp: Optional[str]
    source: str  # "HINDSIGHT" or "DEMO MODE"
    tags: List[str] = field(default_factory=list)


@dataclass
class RecallOutput:
    """Container for memory recall results."""
    mode: str  # "HINDSIGHT" or "DEMO MODE"
    bank_id: str
    query_used: str
    matches: List[RecallMatch]
    total_found: int
    message: str


def generate_relevance_explanation(
    current_title: str,
    current_system: str,
    current_logs: str,
    match_title: str,
    match_system: str,
    match_root_cause: str,
    match_error_logs: str = ""
) -> str:
    """Generate a coherent technical explanation of why a retrieved memory is relevant."""
    reasons = []
    
    # Check system similarity
    if current_system and match_system and (
        current_system.lower() in match_system.lower() or match_system.lower() in current_system.lower()
    ):
        reasons.append(f"Both incidents affect the same infrastructure component: **{match_system}**.")
    
    # Check database/error code keywords
    common_signatures = [
        ("connection pool", "connection pool exhaustion or database client starvation"),
        ("timeout", "timeout limits reached under peak throughput"),
        ("53300", "PostgreSQL error code SQLSTATE 53300 (connection slots reserved/exhausted)"),
        ("oom", "Out of Memory (OOM) eviction constraint"),
        ("cert", "TLS / SSL certificate expiration or challenge renewal fault"),
        ("404", "routing rule misconfiguration blocking ingress"),
        ("idle in transaction", "leaking database connection handles in unhandled code paths"),
        ("redis", "Redis cache cluster storage saturation"),
    ]
    
    text_corpus = f"{current_title} {current_logs}".lower()
    match_corpus = f"{match_title} {match_root_cause} {match_error_logs}".lower()
    
    matched_signatures = [
        desc for kw, desc in common_signatures 
        if kw in text_corpus and kw in match_corpus
    ]
    
    if matched_signatures:
        reasons.append(f"Matching technical symptoms identified: {', '.join(matched_signatures)}.")
    else:
        reasons.append(f"Semantic similarity in problem pattern and failure domain between past incident '{match_title}' and current symptoms.")
        
    reasons.append(f"Past investigation confirmed root cause was: *{match_root_cause[:180]}...*")
    
    return " ".join(reasons)


def compute_demo_similarity(
    query_tokens: set,
    item_tokens: set,
    system_match: bool,
    category_match: bool
) -> float:
    """Calculate normalized similarity score for demo fallback search."""
    if not query_tokens or not item_tokens:
        return 0.0
    
    intersection = query_tokens.intersection(item_tokens)
    jaccard = len(intersection) / len(query_tokens.union(item_tokens))
    
    score = jaccard * 1.5
    if system_match:
        score += 0.35
    if category_match:
        score += 0.15
        
    return min(max(round(score, 3), 0.10), 0.98)


def recall_memories(
    query: str,
    title: str = "",
    category: str = "",
    affected_system: str = "",
    error_logs: str = "",
    limit: int = 4
) -> RecallOutput:
    """Query persistent memory for relevant past incidents."""
    status = hindsight_manager.check_connection()
    bank_id = hindsight_manager.bank_id
    
    # Construct an enriched search query for multi-strategy retrieval
    query_parts = [query.strip()]
    if title:
        query_parts.append(title.strip())
    if affected_system:
        query_parts.append(f"system:{affected_system.strip()}")
    if error_logs:
        # Extract first 200 chars of logs for signature matching
        clean_logs = " ".join(error_logs.split())[:200]
        query_parts.append(clean_logs)
        
    search_query = " | ".join(filter(None, query_parts))
    
    matches: List[RecallMatch] = []

    if status.is_live:
        # Real Hindsight API Query
        try:
            client = hindsight_manager.get_client()
            resp = client.recall(
                bank_id=bank_id,
                query=search_query,
                max_tokens=4096,
                budget="mid"
            )
            
            raw_results = getattr(resp, "results", [])
            for r in raw_results:
                text = getattr(r, "text", "")
                r_id = getattr(r, "id", "")
                metadata = getattr(r, "metadata", {}) or {}
                scores = getattr(r, "scores", {}) or {}
                
                # Extract score if available
                score = 0.85
                if isinstance(scores, dict) and scores:
                    score = float(list(scores.values())[0])
                
                # Parse structured sections if stored in IRIS format
                extracted_root_cause = "Refer to memory document content"
                extracted_steps = "Follow historical investigation procedure"
                extracted_resolution = "See historical resolution details"
                
                if "CONFIRMED ROOT CAUSE:" in text:
                    parts = text.split("CONFIRMED ROOT CAUSE:")
                    if len(parts) > 1:
                        rc_part = parts[1].split("INVESTIGATION & TROUBLESHOOTING STEPS:")[0]
                        extracted_root_cause = rc_part.strip()
                        
                if "VERIFIED RESOLUTION & REMEDIATION:" in text:
                    res_parts = text.split("VERIFIED RESOLUTION & REMEDIATION:")
                    if len(res_parts) > 1:
                        extracted_resolution = res_parts[1].split("TECHNICAL CONTEXT:")[0].strip()

                inc_id = metadata.get("incident_id")
                inc_title = metadata.get("title", f"Historical Incident {inc_id or r_id}")
                inc_sys = metadata.get("system", affected_system or "Unknown System")
                inc_cat = metadata.get("category", category or "Technical Incident")
                
                explanation = generate_relevance_explanation(
                    current_title=title or query,
                    current_system=affected_system,
                    current_logs=error_logs,
                    match_title=inc_title,
                    match_system=inc_sys,
                    match_root_cause=extracted_root_cause,
                    match_error_logs=text
                )
                
                matches.append(RecallMatch(
                    memory_id=str(r_id),
                    incident_id=inc_id,
                    title=inc_title,
                    category=inc_cat,
                    affected_system=inc_sys,
                    similarity_score=min(round(score, 2), 1.0),
                    root_cause=extracted_root_cause,
                    steps_taken=extracted_steps,
                    resolution=extracted_resolution,
                    relevance_explanation=explanation,
                    raw_content=text,
                    timestamp=getattr(r, "occurred_start", None),
                    source="HINDSIGHT",
                    tags=getattr(r, "tags", []) or []
                ))
                
            log_memory_audit(
                action="RECALL",
                incident_id=None,
                query=search_query,
                content_summary=f"Recalled {len(matches)} memories from Hindsight",
                bank_id=bank_id,
                mode="HINDSIGHT",
                success=True,
                details=f"Live query executed with query='{search_query[:80]}...'"
            )
            
            return RecallOutput(
                mode="HINDSIGHT",
                bank_id=bank_id,
                query_used=search_query,
                matches=matches[:limit],
                total_found=len(matches),
                message=f"Retrieved {len(matches)} relevant memories from live Hindsight bank '{bank_id}'."
            )
            
        except Exception as e:
            logger.error(f"Hindsight recall failed: {e}")
            log_memory_audit(
                action="RECALL",
                incident_id=None,
                query=search_query,
                content_summary="Hindsight recall exception; falling back to demo store",
                bank_id=bank_id,
                mode="HINDSIGHT",
                success=False,
                details=str(e)
            )
            # Fall through to demo store

    # Isolated Development Fallback (DEMO MODE)
    return _recall_from_demo_store(
        search_query=search_query,
        title=title,
        category=category,
        affected_system=affected_system,
        error_logs=error_logs,
        bank_id=bank_id,
        limit=limit
    )


def _recall_from_demo_store(
    search_query: str,
    title: str,
    category: str,
    affected_system: str,
    error_logs: str,
    bank_id: str,
    limit: int
) -> RecallOutput:
    """Retrieve matching memories from the local demo store."""
    demo_records = hindsight_manager.demo_store
    
    # Tokenize input query and current symptoms
    def tokenize(text: str) -> set:
        clean = re.sub(r"[^a-zA-Z0-9_\-]", " ", (text or "").lower())
        return {w for w in clean.split() if len(w) > 2 and w not in {
            "the", "and", "for", "with", "from", "that", "this", "during", "error", "failed", "when"
        }}
    
    query_tokens = tokenize(f"{search_query} {title} {affected_system} {error_logs}")
    
    scored_candidates = []
    
    for item in demo_records:
        item_text = f"{item['title']} {item['category']} {item['affected_system']} {item['description']} {item.get('error_logs', '')} {item.get('root_cause', '')}"
        item_tokens = tokenize(item_text)
        
        system_match = bool(
            affected_system and (
                affected_system.lower() in item['affected_system'].lower() or
                item['affected_system'].lower() in affected_system.lower()
            )
        )
        
        category_match = bool(category and category.lower() == item['category'].lower())
        
        sim_score = compute_demo_similarity(query_tokens, item_tokens, system_match, category_match)
        
        # Only include if there is some meaningful overlap or same system/category
        if sim_score > 0.15 or system_match:
            explanation = generate_relevance_explanation(
                current_title=title or search_query,
                current_system=affected_system,
                current_logs=error_logs,
                match_title=item['title'],
                match_system=item['affected_system'],
                match_root_cause=item.get('root_cause', ''),
                match_error_logs=item.get('error_logs', '')
            )
            
            match = RecallMatch(
                memory_id=item['id'],
                incident_id=item.get('incident_id'),
                title=item['title'],
                category=item['category'],
                affected_system=item['affected_system'],
                similarity_score=sim_score,
                root_cause=item.get('root_cause', 'Root cause recorded in postmortem'),
                steps_taken=item.get('steps_taken', 'Standard troubleshooting protocol'),
                resolution=item.get('resolution', 'Verified mitigation applied'),
                relevance_explanation=explanation,
                raw_content=item.get('content', item_text),
                timestamp=item.get('timestamp'),
                source="DEMO MODE",
                tags=item.get('tags', [item['category'].lower()])
            )
            scored_candidates.append((sim_score, match))
            
    # Sort by descending similarity score
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_matches = [cand[1] for cand in scored_candidates[:limit]]
    
    log_memory_audit(
        action="RECALL",
        incident_id=None,
        query=search_query,
        content_summary=f"Recalled {len(top_matches)} memories from Demo Store",
        bank_id=bank_id,
        mode="DEMO MODE",
        success=True,
        details=f"Demo fallback similarity matching on {len(demo_records)} stored sample records."
    )
    
    return RecallOutput(
        mode="DEMO MODE",
        bank_id=bank_id,
        query_used=search_query,
        matches=top_matches,
        total_found=len(top_matches),
        message=f"Retrieved {len(top_matches)} past incidents from Local Demo Store (Hindsight offline or in demo mode)."
    )
