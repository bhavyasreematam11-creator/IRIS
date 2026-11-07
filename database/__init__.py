"""Database package for IRIS."""
from database.db import (
    init_db,
    create_incident,
    update_incident,
    get_incident,
    list_incidents,
    log_memory_audit,
    list_memory_audit,
    get_analytics_summary,
    reset_db,
    create_user,
    authenticate_user,
    get_user_by_id,
    get_user_by_email,
    update_user_profile,
    update_user_password,
    hash_password,
    verify_password
)

__all__ = [
    "init_db",
    "create_incident",
    "update_incident",
    "get_incident",
    "list_incidents",
    "log_memory_audit",
    "list_memory_audit",
    "get_analytics_summary",
    "reset_db",
    "create_user",
    "authenticate_user",
    "get_user_by_id",
    "get_user_by_email",
    "update_user_profile",
    "update_user_password",
    "hash_password",
    "verify_password"
]
