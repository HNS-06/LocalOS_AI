from typing import Dict, Any, List
import os

class SecurityAnalyzer:
    SUSPICIOUS_PATHS = ["temp", "appdata\\local\\temp", "downloads", "public"]
    SUSPICIOUS_PARENTS = ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "mshta.exe"]

    def analyze_processes(self, processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        warnings = []
        pid_map = {p["pid"]: p for p in processes}
        
        for p in processes:
            exe = (p.get("exe") or "").lower()
            name = (p.get("name") or "").lower()
            pid = p.get("pid")
            ppid = p.get("ppid")
            parent = pid_map.get(ppid, {})
            parent_name = (parent.get("name") or "").lower()
            
            risk_score = 0
            reasons = []
            
            # Check 1: Execution from temporary or download directories
            for s_path in self.SUSPICIOUS_PATHS:
                if s_path in exe:
                    risk_score += 35
                    reasons.append(f"Executable running from temporary directory ({s_path})")
                    break
                    
            # Check 2: Command shell spawning unexpected subprocesses
            if parent_name in self.SUSPICIOUS_PARENTS and name not in ["conhost.exe", "git.exe", "node.exe"]:
                risk_score += 30
                reasons.append(f"Spawned directly by command shell parent '{parent_name}'")
                
            # Check 3: High CPU/RAM with missing or untrusted executable path
            if not exe and p.get("cpu_percent", 0) > 20:
                risk_score += 25
                reasons.append("High CPU process with unresolvable binary path")
                
            if risk_score >= 40:
                warnings.append({
                    "pid": pid,
                    "name": p.get("name"),
                    "exe": p.get("exe"),
                    "parent_name": parent_name,
                    "risk_score": risk_score,
                    "reasons": reasons,
                    "cpu_percent": p.get("cpu_percent"),
                    "memory_mb": p.get("memory_mb")
                })
                
        return warnings
