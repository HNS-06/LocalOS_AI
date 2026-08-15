import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.schema import init_db
from core.orchestrator import orchestrator
from core.event_bus import event_bus
from api.websocket_manager import ws_manager
from api.routes_telemetry import router as telemetry_router
from api.routes_chat import router as chat_router
from api.routes_actions import router as actions_router

def create_app() -> FastAPI:
    # Initialize SQLite database
    init_db()

    app = FastAPI(title="LocalOS AI", version="1.0.0")

    # Enable CORS for local Vite development server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(telemetry_router)
    app.include_router(chat_router)
    app.include_router(actions_router)

    # WebSocket Endpoint for real-time telemetry streaming
    @app.websocket("/ws/telemetry")
    async def websocket_telemetry(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                # Keep-alive receive loop
                await websocket.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    # EventBus subscription to broadcast live telemetry over WebSocket
    async def on_telemetry_event(event):
        await ws_manager.broadcast({
            "type": "telemetry_update",
            "data": event.data
        })

    event_bus.subscribe_async("telemetry", on_telemetry_event)

    # Mount UI build directory if present
    ui_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "dashboard", "dist")
    if os.path.exists(ui_dist):
        app.mount("/", StaticFiles(directory=ui_dist, html=True), name="static")

    @app.on_event("startup")
    async def startup_event():
        # Start background telemetry collector loop
        asyncio.create_task(orchestrator.start_loop(interval_sec=1.5))

    @app.on_event("shutdown")
    def shutdown_event():
        orchestrator.stop()

    return app

app = create_app()
