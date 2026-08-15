import psutil
from typing import Dict, Any
from security.sandbox import action_sandbox

def terminate_process(pid: int) -> Dict[str, Any]:
    valid, message = action_sandbox.validate_terminate_process(pid)
    if not valid:
        return {"success": False, "message": message}
        
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        proc.terminate()
        proc.wait(timeout=3)
        return {"success": True, "message": f"Successfully terminated process '{name}' (PID {pid})."}
    except psutil.TimeoutExpired:
        proc.kill()
        return {"success": True, "message": f"Forcefully killed process PID {pid} after timeout."}
    except Exception as e:
        return {"success": False, "message": f"Failed to terminate PID {pid}: {str(e)}"}

def change_process_priority(pid: int, priority_level: str) -> Dict[str, Any]:
    priorities = {
        "idle": psutil.IDLE_PRIORITY_CLASS,
        "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
        "normal": psutil.NORMAL_PRIORITY_CLASS,
        "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
        "high": psutil.HIGH_PRIORITY_CLASS
    }
    
    level = priority_level.lower()
    if level not in priorities:
        return {"success": False, "message": f"Invalid priority level '{priority_level}'. Choose from: idle, below_normal, normal, above_normal, high."}
        
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        proc.nice(priorities[level])
        return {"success": True, "message": f"Changed priority of '{name}' (PID {pid}) to {priority_level}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to change process priority for PID {pid}: {str(e)}"}
