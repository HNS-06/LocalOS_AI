import os
import math
import tempfile
from typing import Dict, Any

class RansomwareCanarySentinel:
    def __init__(self):
        self.canary_dir = os.path.join(tempfile.gettempdir(), ".localos_canary")
        os.makedirs(self.canary_dir, exist_ok=True)
        self.canary_file = os.path.join(self.canary_dir, "canary_document.txt")
        self._init_canary()

    def _init_canary(self):
        if not os.path.exists(self.canary_file):
            with open(self.canary_file, "w", encoding="utf-8") as f:
                f.write("LocalOS AI Sentinel Decoy Canary Document.\n" * 50)

    def _calculate_entropy(self, filepath: str) -> float:
        if not os.path.exists(filepath):
            return 0.0
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            if not data:
                return 0.0
            byte_counts = [0] * 256
            for b in data:
                byte_counts[b] += 1
            entropy = 0.0
            for count in byte_counts:
                if count == 0:
                    continue
                p = count / len(data)
                entropy -= p * math.log2(p)
            return round(entropy, 2)
        except Exception:
            return 0.0

    def check_canary_integrity(self) -> Dict[str, Any]:
        if not os.path.exists(self.canary_file):
            self._init_canary()
            return {"status": "restored", "alert": False, "message": "Canary document was re-initialized."}
            
        entropy = self._calculate_entropy(self.canary_file)
        # High entropy (> 7.5) indicates encrypted / compressed binary payload
        is_encrypted = entropy > 7.5
        
        return {
            "canary_file": self.canary_file,
            "entropy": entropy,
            "is_encrypted": is_encrypted,
            "alert": is_encrypted,
            "message": "⚠️ Ransomware / Mass Encryption Sentinel Triggered!" if is_encrypted else "Decoy canary file integrity verified. System files uncompromised."
        }

canary_sentinel = RansomwareCanarySentinel()
