"""Retain module: Preserving incident investigation knowledge in persistent memory."""

import datetime
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from database.db import log_memory_audit, update_incident
from memory.hindsight_client import hindsight_manager
from utils.config import settings

logger = logging.getLogger("iris.memory.retain")


@dataclass
class RetainResult:
    """Outcome of a memory retain operation."""
    success: bool
    mode: str  # "HINDSIGHT" or "DEMO MODE"
    memory_id: str
    bank_id: str
    message: str
    stored_content: str
    details: Dict[str, Any]


def format_incident_for_retention(
    incident_id: str,
    title: str,
    category: str,
    severity: str,
    affected_system: str,
    description: str,
    error_logs: str,
    root_cause: str,
    steps_taken: str,
    resolution: str,
    technical_context: Optional[str] = None,
    timestamp: Optional[str] = None
) -> str:
    """Format structured technical incident knowledge for durable memory ingestion."""
    ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
    return f"""=== INCIDENT KNOWLEDGE RECORD ===
Incident ID: {incident_id}
Title: {title}
Category: {category}
Severity: {severity}
Affected System: {affected_system}
Recorded Timestamp: {ts}

INCIDENT SUMMARY & SYMPTOMS:
{description.strip()}

ERROR LOGS & TECHNICAL SIGNATURES:
{error_logs.strip() if error_logs else "None provided"}

CONFIRMED ROOT CAUSE:
{root_cause.strip() if root_cause else "Pending confirmation"}

INVESTIGATION & TROUBLESHOOTING STEPS:
{steps_taken.strip() if steps_taken else "Standard investigation protocol"}

VERIFIED RESOLUTION & REMEDIATION:
{resolution.strip() if resolution else "Pending resolution"}

TECHNICAL CONTEXT:
{technical_context.strip() if technical_context else f"Service: {affected_system}, Category: {category}"}
================================="""


def retain_incident(
    incident_id: str,
    title: str,
    category: str,
    severity: str,
    affected_system: str,
    description: str,
    error_logs: str,
    root_cause: str,
    steps_taken: str,
    resolution: str,
    technical_context: Optional[str] = None,
    timestamp: Optional[str] = None
) -> RetainResult:
    """Store complete incident investigation knowledge into Hindsight or Demo Memory."""
    status = hindsight_manager.check_connection()
    bank_id = hindsight_manager.bank_id
    
    formatted_content = format_incident_for_retention(
        incident_id=incident_id,
        title=title,
        category=category,
        severity=severity,
        affected_system=affected_system,
        description=description,
        error_logs=error_logs,
        root_cause=root_cause,
        steps_taken=steps_taken,
        resolution=resolution,
        technical_context=technical_context,
        timestamp=timestamp
    )
    
    tags = [
        category.lower().replace(" ", "_"),
        affected_system.lower().replace(" ", "_"),
        severity.lower(),
        "incident_resolution"
    ]
    
    metadata = {
        "incident_id": incident_id,
        "title": title,
        "category": category,
        "system": affected_system,
        "severity": severity
    }

    if status.is_live:
        # Genuine Hindsight API Execution
        try:
            client = hindsight_manager.get_client()
            resp = client.retain(
                bank_id=bank_id,
                content=formatted_content,
                context=f"Incident Postmortem for {title} on {affected_system}",
                metadata=metadata,
                tags=tags
            )
            
            operation_id = getattr(resp, "operation_id", None) or f"op-{incident_id}"
            
            # Log audit
            log_memory_audit(
                action="RETAIN",
                incident_id=incident_id,
                query=None,
                content_summary=f"Retained incident {incident_id}: {title}",
                bank_id=bank_id,
                mode="HINDSIGHT",
                success=True,
                details=f"Stored into live Hindsight bank '{bank_id}' with operation_id={operation_id}"
            )
            
            # Update SQLite
            update_incident(incident_id, {"retained_in_memory": True})
            
            return RetainResult(
                success=True,
                mode="HINDSIGHT",
                memory_id=str(operation_id),
                bank_id=bank_id,
                message=f"Successfully retained in live Hindsight memory bank '{bank_id}'.",
                stored_content=formatted_content,
                details={"operation_id": operation_id, "tags": tags, "status": "retained"}
            )
            
        except Exception as e:
            logger.error(f"Hindsight retain call failed: {e}")
            log_memory_audit(
                action="RETAIN",
                incident_id=incident_id,
                query=None,
                content_summary=f"Failed retaining {incident_id}",
                bank_id=bank_id,
                mode="HINDSIGHT",
                success=False,
                details=str(e)
            )
            # Gracefully fall back to demo store with clear notification
            return _retain_in_demo_store(
                incident_id, title, category, severity, affected_system,
                description, error_logs, root_cause, steps_taken, resolution,
                formatted_content, tags, bank_id, fallback_reason=str(e)
            )
    else:
        # Isolated Development Fallback (Clearly labeled DEMO MODE)
        return _retain_in_demo_store(
            incident_id, title, category, severity, affected_system,
            description, error_logs, root_cause, steps_taken, resolution,
            formatted_content, tags, bank_id
        )


def _retain_in_demo_store(
    incident_id: str,
    title: str,
    category: str,
    severity: str,
    affected_system: str,
    description: str,
    error_logs: str,
    root_cause: str,
    steps_taken: str,
    resolution: str,
    formatted_content: str,
    tags: List[str],
    bank_id: str,
    fallback_reason: Optional[str] = None
) -> RetainResult:
    """Store memory in local demo store for offline development and testing."""
    demo_id = f"demo-mem-{incident_id}"
    
    # Check if already in demo store
    existing = [m for m in hindsight_manager.demo_store if m.get("incident_id") == incident_id]
    if existing:
        existing[0].update({
            "title": title,
            "category": category,
            "affected_system": affected_system,
            "description": description,
            "error_logs": error_logs,
            "root_cause": root_cause,
            "steps_taken": steps_taken,
            "resolution": resolution,
            "content": formatted_content,
            "tags": tags,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    else:
        hindsight_manager.demo_store.append({
            "id": demo_id,
            "incident_id": incident_id,
            "title": title,
            "category": category,
            "affected_system": affected_system,
            "description": description,
            "error_logs": error_logs,
            "root_cause": root_cause,
            "steps_taken": steps_taken,
            "resolution": resolution,
            "content": formatted_content,
            "tags": tags,
            "source": "DEMO MODE STORE",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        
    log_memory_audit(
        action="RETAIN",
        incident_id=incident_id,
        query=None,
        content_summary=f"Retained incident {incident_id}: {title} (Demo Store)",
        bank_id=bank_id,
        mode="DEMO MODE",
        success=True,
        details="Saved to local development demo memory store. " + (f"Fallback reason: {fallback_reason}" if fallback_reason else "Hindsight server offline.")
    )
    
    update_incident(incident_id, {"retained_in_memory": True})
    
    return RetainResult(
        success=True,
        mode="DEMO MODE",
        memory_id=demo_id,
        bank_id=bank_id,
        message="Retained in Local Demo Memory Store (Hindsight service is currently offline or unconfigured).",
        stored_content=formatted_content,
        details={"demo_id": demo_id, "mode": "DEMO MODE", "fallback": bool(fallback_reason)}
    )
