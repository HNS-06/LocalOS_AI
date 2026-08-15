import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("LocalOS.ML.Anomaly")

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.fitted = False
        self.history_vectors: List[List[float]] = []

    def add_observation(self, snapshot: Dict[str, Any]):
        cpu = snapshot.get("cpu", {}).get("total_percent", 0.0)
        ram = snapshot.get("memory", {}).get("percent", 0.0)
        disk_io = snapshot.get("disk", {}).get("read_mbs", 0.0) + snapshot.get("disk", {}).get("write_mbs", 0.0)
        net_io = snapshot.get("network", {}).get("sent_kbps", 0.0) + snapshot.get("network", {}).get("recv_kbps", 0.0)
        
        vec = [cpu, ram, disk_io, net_io]
        self.history_vectors.append(vec)
        
        # Keep sliding window of up to 1000 observations
        if len(self.history_vectors) > 1000:
            self.history_vectors.pop(0)
            
        # Fit or refit model once we have at least 30 observations
        if len(self.history_vectors) >= 30 and (len(self.history_vectors) % 20 == 0 or not self.fitted):
            try:
                X = np.array(self.history_vectors)
                self.model.fit(X)
                self.fitted = True
            except Exception as e:
                logger.error(f"Error fitting IsolationForest model: {e}")

    def detect(self, snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.fitted:
            return None
            
        cpu = snapshot.get("cpu", {}).get("total_percent", 0.0)
        ram = snapshot.get("memory", {}).get("percent", 0.0)
        disk_io = snapshot.get("disk", {}).get("read_mbs", 0.0) + snapshot.get("disk", {}).get("write_mbs", 0.0)
        net_io = snapshot.get("network", {}).get("sent_kbps", 0.0) + snapshot.get("network", {}).get("recv_kbps", 0.0)
        
        vec = np.array([[cpu, ram, disk_io, net_io]])
        score = float(self.model.decision_function(vec)[0])  # Negative = more anomalous
        prediction = self.model.predict(vec)[0]  # -1 = anomaly, 1 = normal
        
        if prediction == -1:
            confidence = min(round(abs(score) * 200, 1), 99.0)
            return {
                "is_anomaly": True,
                "confidence": confidence,
                "score": score,
                "title": "Machine Learning Anomaly Detected",
                "description": f"Multivariate resource vector [CPU: {cpu}%, RAM: {ram}%, Disk IO: {round(disk_io, 1)}MB/s, Net IO: {round(net_io, 1)}Kbps] deviates significantly from historical baseline.",
                "metrics": {"cpu": cpu, "ram": ram, "disk_io": disk_io, "net_io": net_io}
            }
        return None
