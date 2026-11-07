"""Automated integration tests for IRIS."""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import unittest
from database.db import (
    init_db,
    reset_db,
    list_incidents,
    get_incident,
    create_incident,
    update_incident,
    list_memory_audit,
    get_analytics_summary,
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    verify_password
)
from memory.hindsight_client import hindsight_manager
from memory.retain import retain_incident
from memory.recall import recall_memories
from app.incident_handler import incident_handler


class TestIRISCore(unittest.TestCase):
    """End-to-end integration test suite for IRIS."""

    @classmethod
    def setUpClass(cls):
        reset_db(seed_samples=True)

    def test_01_db_initialization_and_samples(self):
        """Verify SQLite database initializes and loads sample incidents."""
        incidents = list_incidents()
        self.assertGreaterEqual(len(incidents), 3)
        sample_ids = [i["id"] for i in incidents]
        self.assertIn("INC-2026-0041", sample_ids)
        self.assertIn("INC-2026-0042", sample_ids)
        self.assertIn("INC-2026-0043", sample_ids)

    def test_02_hindsight_connection_fallback(self):
        """Verify Hindsight manager detects live connection or honest demo mode."""
        status = hindsight_manager.check_connection()
        self.assertIn(status.mode, ["HINDSIGHT", "DEMO MODE"])
        self.assertTrue(len(status.bank_id) > 0)

    def test_03_memory_recall_recurring_incident(self):
        """Test recall of historical PostgreSQL failure when similar symptoms occur."""
        out = recall_memories(
            query="Database connection slots reserved superuser connections",
            title="Postgres connection spike",
            affected_system="PostgreSQL Cluster (pgpool-01)",
            error_logs="FATAL: remaining connection slots are reserved for non-replication superuser connections (SQLSTATE 53300)"
        )
        self.assertGreater(len(out.matches), 0)
        match = out.matches[0]
        self.assertIn("PostgreSQL", match.title)
        self.assertIn("pgpool-01", match.affected_system)
        self.assertTrue(len(match.relevance_explanation) > 10)
        self.assertIn("53300", match.relevance_explanation)

    def test_04_full_investigation_lifecycle(self):
        """Test end-to-end incident submission, investigation, and retention."""
        # 1. Submit incident
        inc_id, report, recalled = incident_handler.process_new_incident(
            title="Redis Cache Cluster Saturation Under Spike",
            category="Infrastructure",
            severity="High",
            affected_system="Redis Cluster (redis-session-prod)",
            description="Users reporting session write failures. Memory at 100%.",
            error_logs="OOM command not allowed when used memory > 'maxmemory'"
        )
        self.assertTrue(inc_id.startswith("INC-"))
        self.assertGreater(len(report.potential_root_causes), 0)
        self.assertGreater(len(report.recommended_steps), 0)
        self.assertGreater(len(recalled.matches), 0)

        # 2. Check incident recorded in DB
        record = get_incident(inc_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["status"], "Investigating")

        # 3. Resolve and Retain in Hindsight
        retain_res = incident_handler.resolve_and_retain(
            incident_id=inc_id,
            root_cause="Unbounded session telemetry keys without TTL saturated 8GB memory.",
            steps_taken="1. Identified unexpired telemetry keys using redis-cli --bigkeys. 2. Flushed telemetry keys.",
            resolution="Set maxmemory-policy to allkeys-lru and enforced 7-day TTL on key generation."
        )
        self.assertTrue(retain_res.success)
        self.assertIn(retain_res.mode, ["HINDSIGHT", "DEMO MODE"])

        # 4. Verify DB updated to Resolved and retained_in_memory=1
        updated = get_incident(inc_id)
        self.assertEqual(updated["status"], "Resolved")
        self.assertEqual(updated["retained_in_memory"], 1)

    def test_05_analytics_summary(self):
        """Verify analytics metrics calculate accurately."""
        stats = get_analytics_summary()
        self.assertGreaterEqual(stats["total_incidents"], 4)
        self.assertGreaterEqual(stats["resolved_incidents"], 4)
        self.assertIn("Critical", stats["severity_dist"])

    def test_06_audit_logging(self):
        """Verify every memory retain and recall action is audited."""
        audits = list_memory_audit(limit=20)
        self.assertGreater(len(audits), 0)
        actions = [a["action"] for a in audits]
        self.assertIn("RECALL", actions)
        self.assertIn("RETAIN", actions)

    def test_07_user_registration_and_auth(self):
        """Verify user signup, password hashing, and authentication."""
        # Default user seeded
        admin = authenticate_user("bhavya@iris.ai", "password123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["name"], "Bhavya Sharma")
        self.assertEqual(admin["role"], "Principal SRE")

        # Invalid password fails
        bad_auth = authenticate_user("bhavya@iris.ai", "wrongpassword")
        self.assertIsNone(bad_auth)

        # Create new user
        success, msg, new_user = create_user(
            name="Alice Smith",
            email="alice@incident-response.com",
            password="securePassword456!",
            role="Incident Commander",
            department="Cloud Operations"
        )
        self.assertTrue(success)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user["name"], "Alice Smith")

        # Duplicate email fails
        dup_success, dup_msg, _ = create_user(
            name="Alice Duplicate",
            email="alice@incident-response.com",
            password="anotherPassword"
        )
        self.assertFalse(dup_success)

        # Authenticate newly created user
        auth_new = authenticate_user("alice@incident-response.com", "securePassword456!")
        self.assertIsNotNone(auth_new)
        self.assertEqual(auth_new["role"], "Incident Commander")

    def test_08_profile_update_and_password_change(self):
        """Verify user profile editing and password updates."""
        user = get_user_by_email("alice@incident-response.com")
        self.assertIsNotNone(user)

        # Update profile
        ok = update_user_profile(
            user_id=user["id"],
            name="Alice W. Smith",
            role="Senior Incident Commander",
            department="Global SRE & Escalation",
            bio="Leading Tier-1 distributed outages."
        )
        self.assertTrue(ok)
        refreshed = get_user_by_id(user["id"])
        self.assertEqual(refreshed["name"], "Alice W. Smith")
        self.assertEqual(refreshed["role"], "Senior Incident Commander")

        # Update password
        pwd_ok = update_user_password(user["id"], "brandNewSecret789!")
        self.assertTrue(pwd_ok)

        # Old password fails, new password succeeds
        self.assertIsNone(authenticate_user("alice@incident-response.com", "securePassword456!"))
        re_auth = authenticate_user("alice@incident-response.com", "brandNewSecret789!")
        self.assertIsNotNone(re_auth)


if __name__ == "__main__":
    unittest.main(verbosity=2)
