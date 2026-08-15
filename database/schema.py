import sqlite3
import os
from core.config import config
from core.logging import logger

def init_db():
    db_dir = os.path.dirname(config.db_path)
    os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()
    
    # Telemetry history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        cpu_percent REAL,
        ram_percent REAL,
        ram_used_gb REAL,
        disk_percent REAL,
        disk_read_mbs REAL,
        disk_write_mbs REAL,
        net_sent_kbps REAL,
        net_recv_kbps REAL,
        gpu_percent REAL,
        battery_percent REAL,
        top_cpu_process TEXT,
        top_ram_process TEXT
    )
    """)
    
    # Process snapshots for memory leak tracking & trend prediction
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS process_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        pid INTEGER NOT NULL,
        name TEXT NOT NULL,
        exe_path TEXT,
        cpu_percent REAL,
        memory_mb REAL,
        num_threads INTEGER
    )
    """)
    
    # System events and timeline table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        event_type TEXT NOT NULL,  -- anomaly, rule_alert, security, system_boot, app_launch
        severity TEXT NOT NULL,    -- info, warning, critical
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        details_json TEXT
    )
    """)
    
    # Audit log table for action approvals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        user_query TEXT,
        tool_called TEXT NOT NULL,
        permission_level TEXT NOT NULL,
        approved INTEGER NOT NULL,  -- 0 = denied, 1 = approved
        reason TEXT,
        result_summary TEXT
    )
    """)
    
    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,        -- user, assistant, system
        content TEXT NOT NULL,
        tool_calls_json TEXT
    )
    """)
    
    # Create indexes for fast analytical query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_history(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proc_ts_pid ON process_history(timestamp, pid)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp)")
    
    conn.commit()
    conn.close()
    logger.info(f"Initialized SQLite database schema at {config.db_path}")

if __name__ == "__main__":
    init_db()
