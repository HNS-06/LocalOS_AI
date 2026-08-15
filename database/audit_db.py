import sqlite3
import time
from typing import Dict, Any, List
from core.config import config

def log_audit(user_query: str, tool_called: str, permission_level: str, approved: bool, reason: str, result_summary: str):
    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO audit_logs (timestamp, user_query, tool_called, permission_level, approved, reason, result_summary)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (time.time(), user_query, tool_called, permission_level, 1 if approved else 0, reason, result_summary))
    
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
