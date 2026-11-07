"""Hindsight Persistent Memory Client integration for IRIS."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import urllib.request
import json

from utils.config import settings

logger = logging.getLogger("iris.memory")


@dataclass
class ConnectionStatus:
    """Represents the live state of the Hindsight memory connection."""
    is_live: bool
    mode: str  # "HINDSIGHT" or "DEMO MODE"
    base_url: str
    bank_id: str
    version: Optional[str] = None
    message: str = ""
    error_details: Optional[str] = None


class HindsightManager:
    """Manages connection, bank verification, and operations with Hindsight."""

    def __init__(self):
        self.base_url = settings.HINDSIGHT_BASE_URL
        self.api_key = settings.HINDSIGHT_API_KEY
        self.bank_id = settings.HINDSIGHT_BANK_ID
        self._client = None
        self._demo_store: List[Dict[str, Any]] = []
        self._init_demo_store()

    def _init_demo_store(self):
        """Initialize the local demo store from sample incidents for safe offline development."""
        if settings.SAMPLE_INCIDENTS_PATH.exists():
            try:
                with open(settings.SAMPLE_INCIDENTS_PATH, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                    for item in samples:
                        if item.get("retained_in_memory"):
                            self._demo_store.append({
                                "id": f"demo-{item['id']}",
                                "incident_id": item["id"],
                                "title": item["title"],
                                "category": item["category"],
                                "affected_system": item["affected_system"],
                                "description": item["description"],
                                "error_logs": item.get("error_logs", ""),
                                "root_cause": item.get("root_cause", ""),
                                "steps_taken": item.get("steps_taken", ""),
                                "resolution": item.get("resolution", ""),
                                "timestamp": item.get("created_at"),
                                "source": "DEMO SAMPLE RECORD"
                            })
            except Exception as e:
                logger.warning(f"Could not initialize demo store: {e}")

    def get_client(self):
        """Lazy loader for the official Hindsight SDK client."""
        if self._client is None and not settings.HINDSIGHT_DEMO_MODE:
            try:
                from hindsight_client import Hindsight
                self._client = Hindsight(
                    base_url=self.base_url,
                    api_key=self.api_key if self.api_key else None,
                    timeout=5.0
                )
            except Exception as e:
                logger.warning(f"Hindsight client creation failed: {e}")
                self._client = None
        return self._client

    def check_connection(self) -> ConnectionStatus:
        """Probe the Hindsight service to determine if real Hindsight is reachable."""
        if settings.HINDSIGHT_DEMO_MODE:
            return ConnectionStatus(
                is_live=False,
                mode="DEMO MODE",
                base_url=self.base_url,
                bank_id=self.bank_id,
                version=None,
                message="DEMO MODE active (Configured via HINDSIGHT_DEMO_MODE=true). Using isolated local memory.",
                error_details=None
            )

        client = self.get_client()
        if not client:
            return ConnectionStatus(
                is_live=False,
                mode="DEMO MODE",
                base_url=self.base_url,
                bank_id=self.bank_id,
                version=None,
                message=f"DEMO MODE active. Hindsight SDK could not initialize.",
                error_details="Client initialization failed."
            )

        try:
            # Check version endpoint using SDK
            version_resp = client.get_version()
            version_str = getattr(version_resp, "api_version", "1.2.0")
            
            # Ensure the IRIS memory bank exists
            try:
                client.create_bank(
                    bank_id=self.bank_id,
                    name="IRIS Incident Memory Bank",
                    mission="Retain and recall historical technical incident investigations, root causes, and resolutions to assist SREs in resolving recurring incidents."
                )
            except Exception:
                # Bank may already exist; this is expected
                pass

            return ConnectionStatus(
                is_live=True,
                mode="HINDSIGHT",
                base_url=self.base_url,
                bank_id=self.bank_id,
                version=str(version_str),
                message=f"Connected to Hindsight Engine at {self.base_url} (API Version: {version_str})",
                error_details=None
            )
        except Exception as exc:
            # Service is not reachable at the configured URL
            return ConnectionStatus(
                is_live=False,
                mode="DEMO MODE",
                base_url=self.base_url,
                bank_id=self.bank_id,
                version=None,
                message=f"DEMO MODE active. Hindsight daemon not reachable at {self.base_url}. Using local demo memory.",
                error_details=str(exc)
            )

    @property
    def demo_store(self) -> List[Dict[str, Any]]:
        """Access the demo fallback memory store."""
        return self._demo_store


# Global singleton instance
hindsight_manager = HindsightManager()
