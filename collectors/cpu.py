import psutil
from typing import Dict, Any
from collectors.base import BaseCollector

class CPUCollector(BaseCollector):
    def __init__(self):
        # Warmup psutil cpu percent call
        psutil.cpu_percent(interval=None)

    def collect(self) -> Dict[str, Any]:
        total_percent = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        freq = psutil.cpu_freq()
        count_logical = psutil.cpu_count(logical=True) or 1
        count_physical = psutil.cpu_count(logical=False) or 1
        
        # Load average (fallback on Windows)
        try:
            load_avg = list(psutil.getloadavg())
        except (AttributeError, OSError):
            load_avg = [round(total_percent / 100.0 * count_logical, 2), 0.0, 0.0]
            
        stats = psutil.cpu_stats()
        
        return {
            "total_percent": total_percent,
            "per_core_percent": per_core,
            "frequency_mhz": round(freq.current, 1) if freq else 0.0,
            "logical_cores": count_logical,
            "physical_cores": count_physical,
            "load_avg": load_avg,
            "ctx_switches": stats.ctx_switches,
            "interrupts": stats.interrupts
        }
