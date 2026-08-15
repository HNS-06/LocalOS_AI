from database.audit_db import log_audit

def audit_action(user_query: str, tool_name: str, permission_level: str, approved: bool, reason: str, result_summary: str):
    log_audit(
        user_query=user_query,
        tool_called=tool_name,
        permission_level=permission_level,
        approved=approved,
        reason=reason,
        result_summary=result_summary
    )
