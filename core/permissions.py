from enum import Enum, auto
from typing import Dict, Any

class PermissionLevel(str, Enum):
    READ = "READ"
    LOW_RISK = "LOW_RISK"
    HIGH_RISK = "HIGH_RISK"
    ADMIN = "ADMIN"
    BLOCKED = "BLOCKED"

# Tool permission mapping
TOOL_PERMISSIONS: Dict[str, PermissionLevel] = {
    # Read-only diagnostic tools
    "get_system_info": PermissionLevel.READ,
    "get_cpu_usage": PermissionLevel.READ,
    "get_memory_usage": PermissionLevel.READ,
    "get_disk_usage": PermissionLevel.READ,
    "get_network_connections": PermissionLevel.READ,
    "get_gpu_usage": PermissionLevel.READ,
    "get_processes": PermissionLevel.READ,
    "get_top_cpu_processes": PermissionLevel.READ,
    "get_top_memory_processes": PermissionLevel.READ,
    "get_process_details": PermissionLevel.READ,
    "get_startup_programs": PermissionLevel.READ,
    "get_services": PermissionLevel.READ,
    "get_recent_events": PermissionLevel.READ,
    "get_what_changed": PermissionLevel.READ,
    "get_why_pc_slow": PermissionLevel.READ,
    "get_event_viewer_logs": PermissionLevel.READ,
    "check_canary_sentinel": PermissionLevel.READ,
    
    # Controlled action tools
    "change_process_priority": PermissionLevel.LOW_RISK,
    "clear_temp_cache": PermissionLevel.LOW_RISK,
    "smart_clean_cache": PermissionLevel.LOW_RISK,
    "terminate_process": PermissionLevel.HIGH_RISK,
    "disable_startup_item": PermissionLevel.HIGH_RISK,
    "restart_service": PermissionLevel.HIGH_RISK,
    
    # Strictly prohibited / restricted actions
    "execute_arbitrary_shell": PermissionLevel.BLOCKED,
    "delete_system_files": PermissionLevel.BLOCKED,
}

def check_permission(tool_name: str) -> PermissionLevel:
    return TOOL_PERMISSIONS.get(tool_name, PermissionLevel.HIGH_RISK)

def requires_user_approval(level: PermissionLevel) -> bool:
    return level in (PermissionLevel.LOW_RISK, PermissionLevel.HIGH_RISK, PermissionLevel.ADMIN)
