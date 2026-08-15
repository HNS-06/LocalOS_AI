from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ai.llm_adapter import ollama_adapter
from ai.context_engine import context_engine
from core.orchestrator import orchestrator
from database.events_db import get_recent_events

router = APIRouter(prefix="/api/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "qwen2.5"

@router.get("/models")
def get_available_models():
    models = ollama_adapter.list_available_models()
    is_online = ollama_adapter.is_ollama_available()
    return {
        "models": models,
        "ollama_online": is_online,
        "default": ollama_adapter.default_model
    }

@router.post("/chat")
def chat_with_copilot(req: ChatRequest):
    # Collect real-time snapshot
    snapshot = orchestrator.latest_snapshot or orchestrator.collect_all()
    events = get_recent_events(limit=5)
    
    # Build minimal token-efficient system context
    context = context_engine.build_system_context(
        latest_telemetry=snapshot,
        recent_events=events,
        anomalies=orchestrator.active_anomalies,
        security_warnings=orchestrator.security_warnings
    )
    
    # Generate LLM or Fallback response
    res = ollama_adapter.generate_response(
        user_query=req.message,
        system_context=context,
        model_name=req.model
    )
    
    return res
