import psutil
import time
from typing import Dict, Any, List
from collectors.base import BaseCollector

class NetworkCollector(BaseCollector):
    def __init__(self):
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

    def collect(self) -> Dict[str, Any]:
        curr_net = psutil.net_io_counters()
        curr_time = time.time()
        elapsed = max(curr_time - self.last_time, 0.1)
        
        sent_kbps = 0.0
        recv_kbps = 0.0
        
        if curr_net and self.last_net:
            sent_bytes = curr_net.bytes_sent - self.last_net.bytes_sent
            recv_bytes = curr_net.bytes_recv - self.last_net.bytes_recv
            sent_kbps = round((sent_bytes * 8 / 1024) / elapsed, 1)  # kilobits per second
            recv_kbps = round((recv_bytes * 8 / 1024) / elapsed, 1)
            
        self.last_net = curr_net
        self.last_time = curr_time
        
        # Connections & listening ports summary
        connections = []
        listening_ports = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr:
                    listening_ports.append(conn.laddr.port)
                elif conn.status == 'ESTABLISHED' and conn.raddr:
                    connections.append({
                        "fd": conn.fd,
                        "pid": conn.pid,
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}",
                        "status": conn.status
                    })
        except (psutil.AccessDenied, PermissionError):
            pass
            
        return {
            "sent_kbps": sent_kbps,
            "recv_kbps": recv_kbps,
            "listening_ports_count": len(set(listening_ports)),
            "active_connections_count": len(connections),
            "sample_connections": connections[:10]
        }
