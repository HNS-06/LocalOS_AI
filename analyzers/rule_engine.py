from typing import Dict, Any, List
from core.config import config
from database.events_db import log_event

class RuleEngine:
    def __init__(self):
        self.cpu_high_count = 0

    def evaluate(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        
        cpu = snapshot.get("cpu", {}).get("total_percent", 0.0)
        ram = snapshot.get("memory", {}).get("percent", 0.0)
        ram_avail_gb = snapshot.get("memory", {}).get("available_gb", 10.0)
        disk = snapshot.get("disk", {}).get("percent", 0.0)
        disk_write = snapshot.get("disk", {}).get("write_mbs", 0.0)
        top_cpu = snapshot.get("top_cpu_process", "unknown")
        top_ram = snapshot.get("top_ram_process", "unknown")
        
        # Rule 1: High CPU Utilization
        if cpu >= config.cpu_high_threshold:
            self.cpu_high_count += 1
            if self.cpu_high_count >= 2:  # Sustained high CPU over ~3 seconds
                alert = {
                    "type": "high_cpu",
                    "severity": "warning" if cpu < 95 else "critical",
                    "title": f"High CPU Utilization ({cpu}%)",
                    "description": f"Sustained high CPU usage detected. Primary contributor: {top_cpu}",
                    "details": {"cpu": cpu, "top_process": top_cpu}
                }
                alerts.append(alert)
                log_event("rule_alert", alert["severity"], alert["title"], alert["description"], alert["details"])
        else:
            self.cpu_high_count = 0

        # Rule 2: Low Available RAM
        if ram >= config.ram_high_threshold or ram_avail_gb < 1.5:
            alert = {
                "type": "high_ram",
                "severity": "warning" if ram_avail_gb > 0.8 else "critical",
                "title": f"Low Available Memory ({ram}% used, {ram_avail_gb}GB free)",
                "description": f"Memory pressure detected. Primary consumer: {top_ram}",
                "details": {"ram_percent": ram, "ram_avail_gb": ram_avail_gb, "top_process": top_ram}
            }
            alerts.append(alert)
            log_event("rule_alert", alert["severity"], alert["title"], alert["description"], alert["details"])

        # Rule 3: High Disk Write I/O
        if disk_write >= config.disk_io_high_mbps:
            alert = {
                "type": "high_disk_io",
                "severity": "warning",
                "title": f"High Disk Write Rate ({disk_write} MB/s)",
                "description": f"Extremely heavy disk write activity detected.",
                "details": {"disk_write_mbs": disk_write}
            }
            alerts.append(alert)
            log_event("rule_alert", alert["severity"], alert["title"], alert["description"], alert["details"])

        return alerts
