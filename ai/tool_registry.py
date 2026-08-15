from typing import Dict, Any, List, Callable
from core.permissions import check_permission, PermissionLevel

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, category: str, func: Callable):
        perm = check_permission(name)
        self._tools[name] = {
            "name": name,
            "description": description,
            "category": category,
            "permission": perm.value,
            "requires_approval": perm in (PermissionLevel.LOW_RISK, PermissionLevel.HIGH_RISK, PermissionLevel.ADMIN),
            "func": func
        }

    def get_tools_list(self) -> List[Dict[str, Any]]:
        res = []
        for t in self._tools.values():
            res.append({
                "name": t["name"],
                "description": t["description"],
                "category": t["category"],
                "permission": t["permission"],
                "requires_approval": t["requires_approval"]
            })
        return res

    def execute_tool(self, name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if name not in self._tools:
            return {"success": False, "error": f"Tool '{name}' not found in registry."}
            
        tool = self._tools[name]
        try:
            params = params or {}
            result = tool["func"](**params)
            return {"success": True, "tool": name, "result": result}
        except Exception as e:
            return {"success": False, "tool": name, "error": str(e)}

tool_registry = ToolRegistry()
