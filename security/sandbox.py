from typing import Tuple, Optional
import psutil

CRITICAL_SYSTEM_PROCESSES = {
    "system", "system idle process", "csrss.exe", "smss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "winlogon.exe", "explorer.exe"
}

class ActionSandbox:
    def validate_terminate_process(self, pid: int) -> Tuple[bool, str]:
        if pid <= 4:
            return False, f"PID {pid} is a protected Windows Kernel/System process and cannot be terminated."
            
        try:
            proc = psutil.Process(pid)
            name = proc.name().lower()
            if name in CRITICAL_SYSTEM_PROCESSES:
                return False, f"Process '{name}' (PID {pid}) is a critical Windows OS service and is protected from termination."
        except psutil.NoSuchProcess:
            return False, f"Process with PID {pid} does not exist or has already terminated."
        except Exception as e:
            return False, f"Unable to verify process PID {pid}: {str(e)}"
            
        return True, "Process is valid for termination upon user approval."

action_sandbox = ActionSandbox()
