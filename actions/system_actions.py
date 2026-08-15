import os
import shutil
import tempfile
import winreg
from typing import Dict, Any

def clear_temp_cache() -> Dict[str, Any]:
    temp_dir = tempfile.gettempdir()
    cleared_files = 0
    freed_bytes = 0
    
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            try:
                fp = os.path.join(root, f)
                size = os.path.getsize(fp)
                os.remove(fp)
                cleared_files += 1
                freed_bytes += size
            except Exception:
                continue
                
    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    return {
        "success": True,
        "cleared_files": cleared_files,
        "freed_mb": freed_mb,
        "message": f"Successfully cleaned system temp directory. Cleared {cleared_files} temporary files and reclaimed {freed_mb} MB of disk space."
    }

def disable_startup_item(name: str) -> Dict[str, Any]:
    registry_locations = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    ]
    
    for root_key, subkey_path in registry_locations:
        try:
            key = winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_ALL_ACCESS)
            try:
                winreg.DeleteValue(key, name)
                winreg.CloseKey(key)
                return {"success": True, "message": f"Disabled startup item '{name}' from Windows registry."}
            except FileNotFoundError:
                winreg.CloseKey(key)
        except Exception:
            pass
            
    return {"success": False, "message": f"Startup item '{name}' not found in Windows Run registry entries."}
