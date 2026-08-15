from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from actions.executor import action_executor
from database.audit_db import get_audit_logs

router = APIRouter(prefix="/api/actions", tags=["actions"])

class ActionRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = {}
    user_approved: bool = False
    user_query: Optional[str] = ""

@router.post("/execute")
def execute_action(req: ActionRequest):
    result = action_executor.execute_action(
        tool_name=req.tool_name,
        params=req.params,
        user_approved=req.user_approved,
        user_query=req.user_query or ""
    )
    return result

@router.get("/audit-logs")
def get_audits(limit: int = 50):
    return get_audit_logs(limit=limit)
