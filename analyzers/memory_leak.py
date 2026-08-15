from typing import Dict, Any, List
from database.telemetry_db import get_process_memory_trend

class MemoryLeakDetector:
    def analyze_process(self, pid: int, name: str) -> Dict[str, Any]:
        trend = get_process_memory_trend(pid, minutes_back=15)
        if len(trend) < 5:
            return {"suspicious": False, "reason": "Insufficient data"}
            
        mem_values = [t["memory_mb"] for t in trend]
        
        # Check monotonic or near-monotonic increase
        increases = 0
        total_growth = mem_values[-1] - mem_values[0]
        
        for i in range(1, len(mem_values)):
            if mem_values[i] >= mem_values[i-1]:
                increases += 1
                
        ratio = increases / (len(mem_values) - 1)
        
        # If memory consistently increases (>80% of samples) and total growth is significant (>150MB)
        if ratio >= 0.8 and total_growth > 150.0:
            return {
                "suspicious": True,
                "pid": pid,
                "name": name,
                "start_memory_mb": mem_values[0],
                "current_memory_mb": mem_values[-1],
                "growth_mb": round(total_growth, 1),
                "samples": len(mem_values),
                "growth_rate_mb_per_min": round(total_growth / (len(mem_values) * 0.5), 1),
                "reason": f"Process memory steadily increased by {round(total_growth, 1)}MB over the last 15 minutes without garbage collection drop."
            }
            
        return {"suspicious": False, "growth_mb": round(total_growth, 1)}
