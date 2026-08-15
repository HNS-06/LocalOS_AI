import psutil
from typing import Dict, Any
from collectors.base import BaseCollector

class MemoryCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total_gb": round(vm.total / (1024 ** 3), 2),
            "used_gb": round(vm.used / (1024 ** 3), 2),
            "available_gb": round(vm.available / (1024 ** 3), 2),
            "percent": vm.percent,
            "swap_total_gb": round(swap.total / (1024 ** 3), 2),
            "swap_used_gb": round(swap.used / (1024 ** 3), 2),
            "swap_percent": swap.percent
        }
