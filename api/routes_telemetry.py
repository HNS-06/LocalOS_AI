from fastapi import APIRouter
from core.orchestrator import orchestrator
from database.telemetry_db import get_telemetry_history, get_what_changed_telemetry
from database.events_db import get_recent_events
from analyzers.resource_prediction import ResourcePredictor
from analyzers.startup import StartupAnalyzer

router = APIRouter(prefix="/api", tags=["telemetry"])
predictor = ResourcePredictor()
startup_analyzer = StartupAnalyzer()

@router.get("/system/summary")
def get_system_summary():
    snapshot = orchestrator.latest_snapshot or orchestrator.collect_all()
    return {
        "snapshot": snapshot,
        "active_alerts": orchestrator.active_alerts,
        "active_anomalies": orchestrator.active_anomalies,
        "security_warnings": orchestrator.security_warnings
    }

@router.get("/telemetry/history")
def get_history(seconds: int = 3600):
    return get_telemetry_history(seconds_back=seconds)

@router.get("/events")
def get_events(limit: int = 50):
    return get_recent_events(limit=limit)

@router.get("/what-changed")
def get_what_changed(hours: int = 24):
    telemetry_diff = get_what_changed_telemetry(hours_back=hours)
    recent_events = get_recent_events(limit=20)
    return {
        "telemetry_diff": telemetry_diff,
        "events": recent_events,
        "security_warnings": orchestrator.security_warnings
    }

@router.get("/predictions")
def get_predictions():
    return {
        "storage": predictor.predict_disk_exhaustion()
    }

@router.get("/startup-items")
def get_startup_items():
    return startup_analyzer.get_startup_items()
