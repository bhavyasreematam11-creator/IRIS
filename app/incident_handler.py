"""Incident Handler: Orchestrates incident submission, memory recall, AI investigation, and retention."""

import datetime
from typing import Any, Dict, Optional, Tuple

from app.agent import IncidentAgent, InvestigationReport, incident_agent
from database.db import create_incident, get_incident, update_incident
from memory.recall import RecallOutput, recall_memories
from memory.retain import RetainResult, retain_incident
from utils.helpers import generate_incident_id


class IncidentHandler:
    """Orchestrates end-to-end incident analysis, memory lookup, and knowledge retention."""

    def __init__(self, agent: Optional[IncidentAgent] = None):
        self.agent = agent or incident_agent

    def validate_input(
        self,
        title: str,
        category: str,
        severity: str,
        affected_system: str,
        description: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate required fields before initiating investigation."""
        if not title or not title.strip():
            return False, "Incident Title is required."
        if not description or not description.strip():
            return False, "Technical Description is required."
        if not affected_system or not affected_system.strip():
            return False, "Affected System is required."
        if not category or category not in [
            "Database", "Network", "Infrastructure", "Application", "Security", "Storage", "Third-Party API", "Other"
        ]:
            return False, "Please select a valid incident category."
        if not severity or severity not in ["Low", "Medium", "High", "Critical"]:
            return False, "Please select a valid severity level."
        return True, None

    def process_new_incident(
        self,
        title: str,
        category: str,
        severity: str,
        affected_system: str,
        description: str,
        error_logs: str = "",
        custom_id: Optional[str] = None
    ) -> Tuple[str, InvestigationReport, RecallOutput]:
        """Execute end-to-end incident investigation workflow:
        1. Generate unique incident ID
        2. Save to SQLite database
        3. Recall semantically similar past incidents from persistent memory
        4. Run AI Agent investigation using historical precedents as grounding context
        """
        incident_id = custom_id or generate_incident_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Store incident in SQLite
        incident_record = {
            "id": incident_id,
            "title": title.strip(),
            "category": category,
            "severity": severity,
            "affected_system": affected_system.strip(),
            "description": description.strip(),
            "error_logs": error_logs.strip() if error_logs else "",
            "status": "Investigating",
            "retained_in_memory": False,
            "is_sample": False,
            "created_at": now_iso
        }
        create_incident(incident_record)

        # 2. Recall historical memories from Hindsight / Demo Store
        recalled_memories = recall_memories(
            query=f"{title} {description}",
            title=title,
            category=category,
            affected_system=affected_system,
            error_logs=error_logs,
            limit=4
        )

        # 3. Generate structured AI investigation report
        report = self.agent.investigate(
            incident_id=incident_id,
            title=title,
            category=category,
            severity=severity,
            affected_system=affected_system,
            description=description,
            error_logs=error_logs,
            recalled_memories=recalled_memories
        )

        return incident_id, report, recalled_memories

    def resolve_and_retain(
        self,
        incident_id: str,
        root_cause: str,
        steps_taken: str,
        resolution: str,
        technical_context: Optional[str] = None
    ) -> RetainResult:
        """Mark incident resolved in SQLite and preserve the verified knowledge into Hindsight."""
        record = get_incident(incident_id)
        if not record:
            raise ValueError(f"Incident with ID {incident_id} not found in database.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Update SQLite record
        update_incident(incident_id, {
            "status": "Resolved",
            "root_cause": root_cause,
            "steps_taken": steps_taken,
            "resolution": resolution,
            "resolved_at": now_iso
        })

        # Store in persistent memory
        retain_res = retain_incident(
            incident_id=incident_id,
            title=record["title"],
            category=record["category"],
            severity=record["severity"],
            affected_system=record["affected_system"],
            description=record["description"],
            error_logs=record.get("error_logs", ""),
            root_cause=root_cause,
            steps_taken=steps_taken,
            resolution=resolution,
            technical_context=technical_context,
            timestamp=record["created_at"]
        )

        return retain_res


# Global handler instance
incident_handler = IncidentHandler()
