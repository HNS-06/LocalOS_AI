from typing import Dict, Any
from database.telemetry_db import get_telemetry_history

class ResourcePredictor:
    def predict_disk_exhaustion(self) -> Dict[str, Any]:
        # Query 24h history or available data
        history = get_telemetry_history(seconds_back=86400)
        if len(history) < 10:
            return {
                "predictable": False,
                "reason": "Collecting telemetry baseline metrics..."
            }
            
        disk_points = [h["disk_percent"] for h in history]
        start_percent = disk_points[0]
        curr_percent = disk_points[-1]
        
        diff = curr_percent - start_percent
        time_elapsed_hours = (history[-1]["timestamp"] - history[0]["timestamp"]) / 3600.0
        
        if diff <= 0 or time_elapsed_hours <= 0:
            return {
                "predictable": True,
                "trend": "stable_or_decreasing",
                "message": "Disk capacity usage is stable."
            }
            
        growth_rate_per_hour = diff / time_elapsed_hours
        remaining_percent = 100.0 - curr_percent
        hours_to_full = remaining_percent / growth_rate_per_hour if growth_rate_per_hour > 0 else 999
        days_to_full = round(hours_to_full / 24.0, 1)
        
        return {
            "predictable": True,
            "current_disk_percent": curr_percent,
            "growth_rate_percent_per_day": round(growth_rate_per_hour * 24.0, 2),
            "estimated_days_until_full": days_to_full,
            "message": f"At the current growth rate (+{round(growth_rate_per_hour * 24.0, 1)}%/day), primary disk may reach capacity in ~{days_to_full} days."
        }
