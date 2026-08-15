from typing import Dict, Any
from collectors.base import BaseCollector

class GPUCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        utilization = 0.0
        vram_used_mb = 0.0
        vram_total_mb = 0.0
        name = "Integrated / Software Render"
        temp_c = 0.0
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0]
                utilization = round(g.load * 100.0, 1)
                vram_used_mb = round(g.memoryUsed, 1)
                vram_total_mb = round(g.memoryTotal, 1)
                name = g.name
                temp_c = g.temperature
        except Exception:
            pass
            
        return {
            "name": name,
            "utilization": utilization,
            "vram_used_mb": vram_used_mb,
            "vram_total_mb": vram_total_mb,
            "temperature_c": temp_c
        }
