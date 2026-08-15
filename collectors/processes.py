import psutil
from typing import Dict, Any, List
from collectors.base import BaseCollector

class ProcessCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        processes: List[Dict[str, Any]] = []
        
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'exe', 'cpu_percent', 'memory_info', 'memory_percent', 'num_threads', 'status']):
            try:
                info = proc.info
                mem_mb = round((info['memory_info'].rss if info['memory_info'] else 0) / (1024 * 1024), 1)
                processes.append({
                    "pid": info['pid'],
                    "ppid": info['ppid'],
                    "name": info['name'] or "unknown",
                    "exe": info['exe'] or "",
                    "cpu_percent": round(info['cpu_percent'] or 0.0, 1),
                    "memory_mb": mem_mb,
                    "memory_percent": round(info['memory_percent'] or 0.0, 1),
                    "num_threads": info['num_threads'] or 1,
                    "status": info['status'] or "running"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        # Sort by CPU and RAM
        by_cpu = sorted(processes, key=lambda x: x["cpu_percent"], reverse=True)
        by_ram = sorted(processes, key=lambda x: x["memory_mb"], reverse=True)
        
        top_cpu_process = by_cpu[0]["name"] if by_cpu else "none"
        top_ram_process = by_ram[0]["name"] if by_ram else "none"
        
        return {
            "total_count": len(processes),
            "top_cpu_process": top_cpu_process,
            "top_ram_process": top_ram_process,
            "top_by_cpu": by_cpu[:10],
            "top_by_ram": by_ram[:10],
            "processes_sample": by_ram[:50]
        }
