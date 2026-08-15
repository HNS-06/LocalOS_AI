import sys
import os

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        os.system('chcp 65001 >nul 2>&1')
    except Exception:
        pass

if __name__ == "__main__":
    # Ensure current directory is on sys.path
    sys.path.insert(0, os.path.dirname(__file__))

    # If --web flag is passed, launch FastAPI Uvicorn web server
    if "--web" in sys.argv:
        import uvicorn
        print("==========================================================")
        print("   [+] Starting LocalOS AI - Web Server Mode             ")
        print("   REST API & WebSockets running at: http://127.0.0.1:8000 ")
        print("==========================================================")
        uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
    else:
        # Default mode: Launch Interactive Rich Terminal Interface (TUI)
        from database.schema import init_db
        from ui.terminal.dashboard import LocalOSTerminalApp
        
        init_db()
        app = LocalOSTerminalApp()
        app.start_cli()
