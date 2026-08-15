import os
from pydantic import BaseModel

class SystemConfig(BaseModel):
    app_name: str = "LocalOS AI"
    version: str = "1.0.0"
    
    # Telemetry settings
    telemetry_interval_sec: float = 1.5
    history_retention_days: int = 7
    
    # Database
    db_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "localos.db")
    
    # Ollama settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_default_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5")
    ollama_request_timeout: float = 30.0
    
    # Thresholds for Layer 1 Rule Engine
    cpu_high_threshold: float = 90.0  # %
    ram_high_threshold: float = 85.0  # %
    disk_high_threshold: float = 90.0  # %
    disk_io_high_mbps: float = 100.0   # MB/s
    temp_high_threshold: float = 80.0  # °C
    
    # Security
    require_action_approval: bool = True

config = SystemConfig()
