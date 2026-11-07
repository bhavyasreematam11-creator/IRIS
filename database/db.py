"""Database management, SQLite models, and User Authentication for IRIS."""

import hashlib
import json
import secrets
import sqlite3
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from utils.config import settings


def get_connection() -> sqlite3.Connection:
    """Create or retrieve a connection to the SQLite database."""
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash password securely using PBKDF2 with SHA-256 and unique salt."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )
    return key.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify input password against stored PBKDF2 hash."""
    computed_hash, _ = hash_password(password, salt=salt)
    return secrets.compare_digest(computed_hash, password_hash)


def init_db(seed_samples: bool = True):
    """Initialize database tables and optionally seed realistic sample records."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Site Reliability Engineer',
        department TEXT DEFAULT 'Infrastructure & Operations',
        bio TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    # Incidents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        affected_system TEXT NOT NULL,
        description TEXT NOT NULL,
        error_logs TEXT,
        status TEXT NOT NULL DEFAULT 'Investigating',
        root_cause TEXT,
        steps_taken TEXT,
        resolution TEXT,
        retained_in_memory INTEGER DEFAULT 0,
        is_sample INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        resolved_at TEXT
    );
    """)

    # Memory Audit Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        incident_id TEXT,
        query TEXT,
        content_summary TEXT,
        bank_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        success INTEGER DEFAULT 1,
        timestamp TEXT NOT NULL,
        details TEXT
    );
    """)

    conn.commit()

    # Pre-seed default user if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        p_hash, salt = hash_password("password123")
        cursor.execute("""
        INSERT INTO users (name, email, password_hash, salt, role, department, bio, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Bhavya Sharma",
            "bhavya@iris.ai",
            p_hash,
            salt,
            "Principal SRE",
            "Core Platform & Incident Response",
            "Leading high-severity incident investigations, automated remediation pipelines, and persistent SRE memory architecture.",
            datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        conn.commit()

    # Pre-seed sample incidents if table is empty
    if seed_samples:
        cursor.execute("SELECT COUNT(*) FROM incidents")
        count = cursor.fetchone()[0]
        if count == 0 and settings.SAMPLE_INCIDENTS_PATH.exists():
            try:
                with open(settings.SAMPLE_INCIDENTS_PATH, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                    for item in samples:
                        cursor.execute("""
                        INSERT INTO incidents (
                            id, title, category, severity, affected_system,
                            description, error_logs, status, root_cause,
                            steps_taken, resolution, retained_in_memory, is_sample,
                            created_at, resolved_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item["id"],
                            item["title"],
                            item["category"],
                            item["severity"],
                            item["affected_system"],
                            item["description"],
                            item.get("error_logs", ""),
                            item.get("status", "Resolved"),
                            item.get("root_cause", ""),
                            item.get("steps_taken", ""),
                            item.get("resolution", ""),
                            1 if item.get("retained_in_memory") else 0,
                            1,
                            item.get("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
                            item.get("resolved_at")
                        ))
                conn.commit()
            except Exception as e:
                print(f"[IRIS DB] Error seeding sample incidents: {e}")

    conn.close()


# --- USER AUTHENTICATION & PROFILE FUNCTIONS ---

def create_user(
    name: str,
    email: str,
    password: str,
    role: str = "Site Reliability Engineer",
    department: str = "Infrastructure & Operations",
    bio: str = ""
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Register a new user in the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()

    email_clean = email.strip().lower()
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,))
    if cursor.fetchone():
        conn.close()
        return False, "An account with this email address already exists.", None

    p_hash, salt = hash_password(password)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        cursor.execute("""
        INSERT INTO users (name, email, password_hash, salt, role, department, bio, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), email_clean, p_hash, salt, role.strip(), department.strip(), bio.strip(), now_iso))
        user_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT id, name, email, role, department, bio, created_at FROM users WHERE id = ?", (user_id,))
        new_user = dict(cursor.fetchone())
        conn.close()
        return True, "Account created successfully!", new_user
    except Exception as e:
        conn.close()
        return False, f"Failed to register user: {str(e)}", None


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify user credentials and return user dictionary if valid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    user = dict(row)
    if verify_password(password, user["password_hash"], user["salt"]):
        # Remove hash & salt before returning
        user.pop("password_hash", None)
        user.pop("salt", None)
        return user
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user profile by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, department, bio, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user profile by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, department, bio, created_at FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_user_profile(user_id: int, name: str, role: str, department: str, bio: str) -> bool:
    """Update user personal and role details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET name = ?, role = ?, department = ?, bio = ? WHERE id = ?
    """, (name.strip(), role.strip(), department.strip(), bio.strip(), user_id))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def update_user_password(user_id: int, new_password: str) -> bool:
    """Update user password with freshly computed salt and hash."""
    p_hash, salt = hash_password(new_password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
    """, (p_hash, salt, user_id))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


# --- INCIDENT CRUD FUNCTIONS ---

def create_incident(data: Dict[str, Any]) -> str:
    """Insert a new incident record into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = data.get("created_at") or datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    cursor.execute("""
    INSERT INTO incidents (
        id, title, category, severity, affected_system,
        description, error_logs, status, root_cause,
        steps_taken, resolution, retained_in_memory, is_sample,
        created_at, resolved_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["id"],
        data["title"],
        data["category"],
        data["severity"],
        data["affected_system"],
        data["description"],
        data.get("error_logs", ""),
        data.get("status", "Investigating"),
        data.get("root_cause", ""),
        data.get("steps_taken", ""),
        data.get("resolution", ""),
        1 if data.get("retained_in_memory") else 0,
        1 if data.get("is_sample") else 0,
        created_at,
        data.get("resolved_at")
    ))
    
    conn.commit()
    conn.close()
    return data["id"]


def update_incident(incident_id: str, updates: Dict[str, Any]):
    """Update fields on an existing incident."""
    conn = get_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for k, v in updates.items():
        if k in [
            "title", "category", "severity", "affected_system",
            "description", "error_logs", "status", "root_cause",
            "steps_taken", "resolution", "retained_in_memory", "resolved_at"
        ]:
            fields.append(f"{k} = ?")
            if k == "retained_in_memory":
                values.append(1 if v else 0)
            else:
                values.append(v)
                
    if fields:
        values.append(incident_id)
        query = f"UPDATE incidents SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        
    conn.close()


def get_incident(incident_id: str) -> Optional[Dict[str, Any]]:
    """Fetch single incident by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_incidents(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search_query: Optional[str] = None,
    include_samples: bool = True,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """List incidents matching filters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if not include_samples:
        conditions.append("is_sample = 0")
        
    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)
        
    if severity and severity != "All":
        conditions.append("severity = ?")
        params.append(severity)
        
    if status and status != "All":
        conditions.append("status = ?")
        params.append(status)
        
    if search_query and search_query.strip():
        conditions.append("(title LIKE ? OR id LIKE ? OR description LIKE ? OR affected_system LIKE ?)")
        wildcard = f"%{search_query.strip()}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT * FROM incidents{where_clause} ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_memory_audit(
    action: str,
    incident_id: Optional[str],
    query: Optional[str],
    content_summary: Optional[str],
    bank_id: str,
    mode: str,
    success: bool = True,
    details: Optional[str] = None
):
    """Log retain or recall memory actions for observability."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO memory_audit (
        action, incident_id, query, content_summary, bank_id, mode, success, timestamp, details
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        action,
        incident_id,
        query,
        content_summary,
        bank_id,
        mode,
        1 if success else 0,
        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        details
    ))
    conn.commit()
    conn.close()


def list_memory_audit(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent memory retain/recall operations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memory_audit ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_analytics_summary() -> Dict[str, Any]:
    """Calculate summary statistics for dashboard cards and charts."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM incidents")
    total_incidents = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'Resolved'")
    resolved_incidents = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE retained_in_memory = 1")
    retained_memories = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT affected_system, COUNT(*) as cnt 
            FROM incidents 
            GROUP BY affected_system 
            HAVING cnt > 1
        )
    """)
    recurring_groups = cursor.fetchone()[0]
    
    cursor.execute("SELECT severity, COUNT(*) FROM incidents GROUP BY severity")
    severity_dist = dict(cursor.fetchall())
    
    cursor.execute("SELECT category, COUNT(*) FROM incidents GROUP BY category")
    category_dist = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "retained_memories": retained_memories,
        "recurring_incident_groups": recurring_groups,
        "severity_dist": severity_dist,
        "category_dist": category_dist
    }


def reset_db(seed_samples: bool = True):
    """Reset database tables and optionally re-seed sample data."""
    if settings.DB_PATH.exists():
        try:
            settings.DB_PATH.unlink()
        except Exception:
            pass
    init_db(seed_samples=seed_samples)
