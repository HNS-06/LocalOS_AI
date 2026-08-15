from typing import Dict, Any, List
import winreg

class StartupAnalyzer:
    def get_startup_items(self) -> List[Dict[str, Any]]:
        items = []
        
        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
        ]
        
        for root_key, subkey_path in registry_locations:
            try:
                key = winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_READ)
                count = winreg.QueryInfoKey(key)[1]
                for i in range(count):
                    name, val, _ = winreg.EnumValue(key, i)
                    classification = self._classify_item(name, str(val))
                    items.append({
                        "name": name,
                        "command": str(val),
                        "location": "HKCU Run" if root_key == winreg.HKEY_CURRENT_USER else "HKLM Run",
                        "classification": classification["category"],
                        "impact": classification["impact"],
                        "recommendation": classification["recommendation"]
                    })
                winreg.CloseKey(key)
            except Exception:
                pass
                
        return items

    def _classify_item(self, name: str, command: str) -> Dict[str, str]:
        n = name.lower()
        c = command.lower()
        
        if any(k in n or k in c for k in ["nvidia", "realtek", "windows defender", "intel", "amd", "security"]):
            return {"category": "Essential", "impact": "Low", "recommendation": "Keep enabled for hardware/security features."}
        elif any(k in n or k in c for k in ["onedrive", "dropbox", "steam", "discord", "spotify", "slack"]):
            return {"category": "Optional", "impact": "Medium", "recommendation": "Disable if you prefer faster Windows boot time."}
        elif any(k in c for k in ["temp", "appdata\\local\\temp", "powershell -w hidden", "cmd.exe /c"]):
            return {"category": "Suspicious", "impact": "High", "recommendation": "Investigate immediately; autostarting script or hidden command."}
        else:
            return {"category": "Useful", "impact": "Low", "recommendation": "User application startup entry."}
