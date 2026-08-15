from typing import Dict, Any
from core.permissions import check_permission, requires_user_approval, PermissionLevel
from security.audit import audit_action
from actions.process_actions import terminate_process, change_process_priority
from actions.system_actions import clear_temp_cache, disable_startup_item

class ActionExecutor:
    def execute_action(self, tool_name: str, params: Dict[str, Any], user_approved: bool = False, user_query: str = "") -> Dict[str, Any]:
        perm = check_permission(tool_name)
        
        if perm == PermissionLevel.BLOCKED:
            audit_action(user_query, tool_name, perm.value, False, "Prohibited action", "Blocked by security policy")
            return {"success": False, "message": f"Action '{tool_name}' is permanently blocked by LocalOS security policy."}
            
        if requires_user_approval(perm) and not user_approved:
            audit_action(user_query, tool_name, perm.value, False, "Requires user approval", "Awaiting user approval")
            return {
                "success": False,
                "requires_approval": True,
                "permission_level": perm.value,
                "tool": tool_name,
                "params": params,
                "message": f"Action '{tool_name}' requires explicit user approval."
            }
            
        # Execute approved action
        res = {"success": False, "message": "Unknown tool"}
        if tool_name == "terminate_process":
            res = terminate_process(pid=params.get("pid", 0))
        elif tool_name == "change_process_priority":
            res = change_process_priority(pid=params.get("pid", 0), priority_level=params.get("priority_level", "normal"))
        elif tool_name in ["clear_temp_cache", "smart_clean_cache"]:
            from actions.smart_cleaner import smart_clean_cache
            res = smart_clean_cache()
        elif tool_name == "disable_startup_item":
            res = disable_startup_item(name=params.get("name", ""))
            
        audit_action(
            user_query=user_query,
            tool_name=tool_name,
            permission_level=perm.value,
            approved=user_approved,
            reason="User confirmed approval" if user_approved else "Auto-approved read",
            result_summary=res.get("message", str(res))
        )
        
        return res

action_executor = ActionExecutor()
