import psutil
from typing import Dict, Any
from collectors.base import BaseCollector

class BatteryCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        battery = psutil.sensors_battery()
        if not battery:
            return {
                "has_battery": False,
                "percent": 100.0,
                "power_plugged": True,
                "sec_left": -1
            }
            
        return {
            "has_battery": True,
            "percent": round(battery.percent, 1),
            "power_plugged": battery.power_plugged,
            "sec_left": battery.secsleft
        }
