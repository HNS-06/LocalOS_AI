import psutil
import time
from typing import Dict, Any
from collectors.base import BaseCollector

class DiskCollector(BaseCollector):
    def __init__(self):
        self.last_io = psutil.disk_io_counters()
        self.last_time = time.time()

    def collect(self) -> Dict[str, Any]:
        partitions = []
        for p in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(p.mountpoint)
                partitions.append({
                    "device": p.device,
                    "mountpoint": p.mountpoint,
                    "fstype": p.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "percent": usage.percent
                })
            except PermissionError:
                continue
                
        # Primary drive usage
        primary_percent = partitions[0]["percent"] if partitions else 0.0
        
        # IO Rate calculation
        curr_io = psutil.disk_io_counters()
        curr_time = time.time()
        elapsed = max(curr_time - self.last_time, 0.1)
        
        read_mbs = 0.0
        write_mbs = 0.0
        read_iops = 0.0
        write_iops = 0.0
        
        if curr_io and self.last_io:
            read_bytes = curr_io.read_bytes - self.last_io.read_bytes
            write_bytes = curr_io.write_bytes - self.last_io.write_bytes
            read_count = curr_io.read_count - self.last_io.read_count
            write_count = curr_io.write_count - self.last_io.write_count
            
            read_mbs = round((read_bytes / (1024 * 1024)) / elapsed, 2)
            write_mbs = round((write_bytes / (1024 * 1024)) / elapsed, 2)
            read_iops = round(read_count / elapsed, 1)
            write_iops = round(write_count / elapsed, 1)
            
        self.last_io = curr_io
        self.last_time = curr_time
        
        return {
            "percent": primary_percent,
            "partitions": partitions,
            "read_mbs": read_mbs,
            "write_mbs": write_mbs,
            "read_iops": read_iops,
            "write_iops": write_iops
        }
