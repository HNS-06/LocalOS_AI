import os
import tempfile
from typing import Dict, Any

def smart_clean_cache() -> Dict[str, Any]:
    target_dirs = [
        tempfile.gettempdir(),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp")
    ]
    
    total_files_removed = 0
    total_bytes_reclaimed = 0
    
    for d in target_dirs:
        if not d or not os.path.exists(d):
            continue
        for root, dirs, files in os.walk(d):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    sz = os.path.getsize(fp)
                    os.remove(fp)
                    total_files_removed += 1
                    total_bytes_reclaimed += sz
                except Exception:
                    continue
                    
    freed_mb = round(total_bytes_reclaimed / (1024 * 1024), 2)
    return {
        "success": True,
        "files_removed": total_files_removed,
        "freed_mb": freed_mb,
        "message": f"Smart Cleaner purged {total_files_removed} temporary cache files, reclaiming {freed_mb} MB of disk space."
    }
