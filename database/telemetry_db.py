import sqlite3
import time
from typing import Dict, Any, List
from core.config import config

def save_telemetry_snapshot(data: Dict[str, Any]):
    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()
    
    ts = data.get("timestamp", time.time())
    cpu = data.get("cpu", {}).get("total_percent", 0.0)
    ram = data.get("memory", {}).get("percent", 0.0)
    ram_gb = data.get("memory", {}).get("used_gb", 0.0)
    disk = data.get("disk", {}).get("percent", 0.0)
    disk_read = data.get("disk", {}).get("read_mbs", 0.0)
    disk_write = data.get("disk", {}).get("write_mbs", 0.0)
    net_sent = data.get("network", {}).get("sent_kbps", 0.0)
    net_recv = data.get("network", {}).get("recv_kbps", 0.0)
    gpu = data.get("gpu", {}).get("utilization", 0.0)
    battery = data.get("battery", {}).get("percent", 100.0)
    
    top_cpu = data.get("top_cpu_process", "")
    top_ram = data.get("top_ram_process", "")
    
    cursor.execute("""
    INSERT INTO telemetry_history (
        timestamp, cpu_percent, ram_percent, ram_used_gb, disk_percent,
        disk_read_mbs, disk_write_mbs, net_sent_kbps, net_recv_kbps,
        gpu_percent, battery_percent, top_cpu_process, top_ram_process
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ts, cpu, ram, ram_gb, disk, disk_read, disk_write, net_sent, net_recv, gpu, battery, top_cpu, top_ram))
    
    # Save top process snapshots for process trend / memory leak analysis
    processes = data.get("processes", {}).get("processes_sample", [])
    for proc in processes[:15]:  # Top 15 processes
        cursor.execute("""
        INSERT INTO process_history (timestamp, pid, name, exe_path, cpu_percent, memory_mb, num_threads)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ts,
            proc.get("pid", 0),
            proc.get("name", "unknown"),
            proc.get("exe", ""),
            proc.get("cpu_percent", 0.0),
            proc.get("memory_mb", 0.0),
            proc.get("num_threads", 1)
        ))
        
    conn.commit()
    conn.close()

def get_telemetry_history(seconds_back: int = 3600) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cutoff = time.time() - seconds_back
    cursor.execute("""
    SELECT * FROM telemetry_history WHERE timestamp >= ? ORDER BY timestamp ASC
    """, (cutoff,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_process_memory_trend(pid: int, minutes_back: int = 30) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cutoff = time.time() - (minutes_back * 60)
    cursor.execute("""
    SELECT timestamp, pid, name, memory_mb, cpu_percent FROM process_history
    WHERE pid = ? AND timestamp >= ? ORDER BY timestamp ASC
    """, (pid, cutoff))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_what_changed_telemetry(hours_back: int = 24) -> Dict[str, Any]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    now = time.time()
    past_cutoff = now - (hours_back * 3600)
    midpoint = now - ((hours_back / 2) * 3600)
    
    # Yesterday / earlier period avg vs recent avg
    cursor.execute("""
    SELECT 
        AVG(cpu_percent) as avg_cpu,
        AVG(ram_percent) as avg_ram,
        AVG(disk_percent) as avg_disk
    FROM telemetry_history WHERE timestamp >= ? AND timestamp < ?
    """, (past_cutoff, midpoint))
    baseline = dict(cursor.fetchone() or {})
    
    cursor.execute("""
    SELECT 
        AVG(cpu_percent) as avg_cpu,
        AVG(ram_percent) as avg_ram,
        AVG(disk_percent) as avg_disk
    FROM telemetry_history WHERE timestamp >= ?
    """, (midpoint,))
    recent = dict(cursor.fetchone() or {})
    
    conn.close()
    return {
        "baseline": baseline,
        "recent": recent,
        "cpu_diff": round((recent.get("avg_cpu") or 0.0) - (baseline.get("avg_cpu") or 0.0), 1),
        "ram_diff": round((recent.get("avg_ram") or 0.0) - (baseline.get("avg_ram") or 0.0), 1)
    }
