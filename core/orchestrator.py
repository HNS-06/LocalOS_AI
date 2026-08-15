import asyncio
import time
import logging
from typing import Dict, Any, List

from collectors.cpu import CPUCollector
from collectors.memory import MemoryCollector
from collectors.disk import DiskCollector
from collectors.network import NetworkCollector
from collectors.processes import ProcessCollector
from collectors.gpu import GPUCollector
from collectors.battery import BatteryCollector

from database.telemetry_db import save_telemetry_snapshot
from database.events_db import get_recent_events
from analyzers.rule_engine import RuleEngine
from analyzers.anomaly import AnomalyDetector
from analyzers.security import SecurityAnalyzer
from core.event_bus import event_bus

logger = logging.getLogger("LocalOS.Orchestrator")

class Orchestrator:
    def __init__(self):
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.disk_collector = DiskCollector()
        self.network_collector = NetworkCollector()
        self.process_collector = ProcessCollector()
        self.gpu_collector = GPUCollector()
        self.battery_collector = BatteryCollector()

        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()
        self.security_analyzer = SecurityAnalyzer()

        self.latest_snapshot: Dict[str, Any] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.active_anomalies: List[Dict[str, Any]] = []
        self.security_warnings: List[Dict[str, Any]] = []
        self.is_running = False

    def collect_all(self) -> Dict[str, Any]:
        snapshot = {
            "timestamp": time.time(),
            "cpu": self.cpu_collector.collect(),
            "memory": self.memory_collector.collect(),
            "disk": self.disk_collector.collect(),
            "network": self.network_collector.collect(),
            "processes": self.process_collector.collect(),
            "gpu": self.gpu_collector.collect(),
            "battery": self.battery_collector.collect()
        }
        
        snapshot["top_cpu_process"] = snapshot["processes"].get("top_cpu_process", "")
        snapshot["top_ram_process"] = snapshot["processes"].get("top_ram_process", "")
        
        self.latest_snapshot = snapshot
        
        # Save to time-series DB
        try:
            save_telemetry_snapshot(snapshot)
        except Exception as e:
            logger.error(f"Error persisting telemetry snapshot: {e}")

        # Layer 1: Rule Engine
        self.active_alerts = self.rule_engine.evaluate(snapshot)

        # Layer 2: ML Anomaly Detector
        self.anomaly_detector.add_observation(snapshot)
        anom = self.anomaly_detector.detect(snapshot)
        if anom:
            self.active_anomalies.append(anom)
            if len(self.active_anomalies) > 20:
                self.active_anomalies.pop(0)

        # Security process risk analyzer
        procs = snapshot["processes"].get("processes_sample", [])
        self.security_warnings = self.security_analyzer.analyze_processes(procs)

        # Broadcast via EventBus
        event_bus.publish("telemetry", snapshot)
        if self.active_alerts:
            event_bus.publish("alerts", {"alerts": self.active_alerts})

        return snapshot

    async def start_loop(self, interval_sec: float = 1.5):
        self.is_running = True
        logger.info(f"Started LocalOS Telemetry Orchestrator loop ({interval_sec}s interval)...")
        while self.is_running:
            try:
                self.collect_all()
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")
            await asyncio.sleep(interval_sec)

    def stop(self):
        self.is_running = False

orchestrator = Orchestrator()
