import sqlite3
import time
import json
from typing import Dict, Any, List
from core.config import config

def log_event(event_type: str, severity: str, title: str, description: str, details: Dict[str, Any] = None):
    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()
    
    ts = time.time()
    details_str = json.dumps(details) if details else "{}"
    
    cursor.execute("""
    INSERT INTO events (timestamp, event_type, severity, title, description, details_json)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (ts, event_type, severity, title, description, details_str))
    
    conn.commit()
    conn.close()

def get_recent_events(limit: int = 50, event_type: str = None) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if event_type:
        cursor.execute("SELECT * FROM events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?", (event_type, limit))
    else:
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        
    rows = cursor.fetchall()
    conn.close()
    
    res = []
    for r in rows:
        item = dict(r)
        try:
            item["details"] = json.loads(item.get("details_json", "{}"))
        except Exception:
            item["details"] = {}
        res.append(item)
    return res
