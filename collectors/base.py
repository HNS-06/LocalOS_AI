from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect and return telemetry metrics dict."""
        pass
