from typing import Dict, Any, List

class ContextEngine:
    def build_system_context(
        self,
        latest_telemetry: Dict[str, Any],
        recent_events: List[Dict[str, Any]] = None,
        anomalies: List[Dict[str, Any]] = None,
        security_warnings: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        cpu_data = latest_telemetry.get("cpu", {})
        mem_data = latest_telemetry.get("memory", {})
        disk_data = latest_telemetry.get("disk", {})
        net_data = latest_telemetry.get("network", {})
        proc_data = latest_telemetry.get("processes", {})
        
        top_cpu = proc_data.get("top_by_cpu", [])[:5]
        top_ram = proc_data.get("top_by_ram", [])[:5]
        
        context = {
            "timestamp": latest_telemetry.get("timestamp"),
            "cpu": {
                "total_percent": cpu_data.get("total_percent", 0.0),
                "frequency_mhz": cpu_data.get("frequency_mhz", 0.0),
                "logical_cores": cpu_data.get("logical_cores", 1),
                "top_process": proc_data.get("top_cpu_process", "None"),
                "top_consumers": [{"name": p.get("name"), "cpu": p.get("cpu_percent"), "pid": p.get("pid")} for p in top_cpu]
            },
            "memory": {
                "percent": mem_data.get("percent", 0.0),
                "used_gb": mem_data.get("used_gb", 0.0),
                "available_gb": mem_data.get("available_gb", 0.0),
                "top_process": proc_data.get("top_ram_process", "None"),
                "top_consumers": [{"name": p.get("name"), "memory_mb": p.get("memory_mb"), "pid": p.get("pid")} for p in top_ram]
            },
            "disk": {
                "percent": disk_data.get("percent", 0.0),
                "read_mbs": disk_data.get("read_mbs", 0.0),
                "write_mbs": disk_data.get("write_mbs", 0.0)
            },
            "network": {
                "sent_kbps": net_data.get("sent_kbps", 0.0),
                "recv_kbps": net_data.get("recv_kbps", 0.0),
                "active_connections": net_data.get("active_connections_count", 0)
            },
            "recent_events": [
                {"title": e.get("title"), "severity": e.get("severity"), "description": e.get("description")}
                for e in (recent_events or [])[:5]
            ],
            "anomalies": anomalies or [],
            "security_warnings": security_warnings or []
        }
        
        return context

context_engine = ContextEngine()
