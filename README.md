# 🖥️ LocalOS AI — Intelligent Operating System Copilot

> **A privacy-first, offline-first local AI agent that understands your operating system, monitors telemetry & processes, detects anomalies using machine learning, explains system behavior in natural language via local Ollama LLMs, and performs user-approved system operations under strict safety controls.**

---

## ⚡ Key Architectural Principle

```
OS Telemetry  ──►  Deterministic Rules  ──►  Local ML Models  ──►  Ollama Local LLM  ──►  User-Approved Action
```

Unlike naive agents that pipe raw OS state into LLMs and blindly execute arbitrary shell scripts, **LocalOS AI** enforces a strict safety boundary:

1. **Deterministic Telemetry & Rules**: Fast threshold checks (CPU, RAM, Disk I/O).
2. **Machine Learning Anomaly Engine**: `scikit-learn` `IsolationForest` detecting multi-dimensional resource anomalies.
3. **Local LLM Reasoning (Ollama)**: Structured, token-efficient system context formatted for models like `deepseek-r1`, `qwen2.5-coder`, `llama3.1`, or `gemma3`.
4. **Security Sandbox & Action Approval**: Action executor requiring explicit confirmation for destructive operations (`terminate_process`, `clear_cache`, `disable_startup`) while protecting critical OS binaries (`csrss.exe`, `svchost.exe`, system PIDs).

---

## 🔥 Key Features

- **💻 Interactive Live Terminal UI (TUI)**:
  - Real-time auto-refreshing dashboard powered by `Rich.Live` (0.5s refresh).
  - Single-key non-blocking navigation (`1` Dash, `2` Processes, `3` AI Copilot, `4` What Changed?, `5` Security, `6` Reports).
  - Built-in Slash Commands: `/clean` (purges temp cache), `/kill-hog` (prompts termination for top CPU consumer), `/why` (AI diagnosis), `/events` (Windows Event Viewer errors).
- **🌐 Modern Real-Time Web Dashboard**:
  - Built with **React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts**.
  - Real-time WebSocket (`/ws/telemetry`) streaming live CPU, RAM, Disk, Network, GPU, and Battery metrics.
  - Interactive Action Approval Modal asking confirmation before executing actions.
- **🤖 Ollama Local LLM Integration**:
  - Automatically queries local Ollama models (`deepseek-r1:1.5b`, `qwen2.5-coder:7b`, `llama3.1:latest`, `gemma3:4b`).
  - Zero-latency warm model resolution prioritizing active VRAM models.
  - Includes a fallback deterministic rule engine if Ollama is starting up or offline.
- **🛡️ Cybersecurity & Ransomware Canary Sentinel**:
  - Monitors decoy canary files for mass modifications and file entropy spikes (> 7.5).
  - Flags process tree anomalies, unexpected shell spawns, and suspicious execution paths.
- **📜 Windows Event Viewer RAG Log Analyzer**:
  - Queries native `System` and `Application` logs for error Event IDs (1000, 7034, 1001) and feeds them into AI context for root-cause diagnosis.
- **🧹 Smart Automated Cache Purger**:
  - Reclaims disk space by safely clearing temporary files, app caches, and prefetch items with detailed MB accounting.

---

## 🏗️ Project Architecture

```
localos-ai/
├── core/
│   ├── config.py              # System configuration & thresholds
│   ├── event_bus.py           # Async Pub/Sub event bus for live telemetry
│   ├── permissions.py         # Safety permission levels (READ, LOW_RISK, HIGH_RISK, ADMIN, BLOCKED)
│   ├── notifications.py       # Native Windows Toast Notification manager
│   ├── orchestrator.py        # Central telemetry collector loop & anomaly engine
│   └── logging.py             # Structured logger
│
├── collectors/
│   ├── base.py                # Collector interface
│   ├── cpu.py                 # Per-core utilization, frequency, load avg
│   ├── memory.py              # RAM total/used/avail, swap, page faults
│   ├── processes.py           # Active processes, PID/PPID, memory, CPU, threads
│   ├── disk.py                # IOPS, read/write speed, volume usage
│   ├── network.py             # Upload/Download rates, active connections, listening ports
│   ├── gpu.py                 # GPU utilization, VRAM, temperature
│   └── battery.py             # Battery percentage, charging status, time left
│
├── database/
│   ├── schema.py              # SQLite schema (telemetry, processes, events, audit logs)
│   ├── telemetry_db.py        # Time-series storage & historical queries
│   ├── events_db.py           # Timeline events & anomaly alerts
│   └── audit_db.py            # User action approval audit trail
│
├── analyzers/
│   ├── rule_engine.py         # Layer 1: Threshold alerts (CPU > 90%, Low RAM)
│   ├── anomaly.py             # Layer 2: IsolationForest ML model
│   ├── memory_leak.py         # Process memory growth slope analyzer
│   ├── resource_prediction.py # Storage & memory capacity forecasting
│   ├── event_viewer.py        # Windows Event Viewer RAG log analyzer
│   ├── canary.py              # Ransomware & file entropy sentinel
│   ├── security.py            # Process tree risk scoring
│   └── startup.py             # Startup items analyzer
│
├── ai/
│   ├── llm_adapter.py         # Ollama API adapter (qwen2.5-coder, deepseek-r1, llama3.1)
│   ├── context_engine.py      # Formats telemetry into token-efficient system context
│   └── tool_registry.py       # Controlled diagnostic & action tools
│
├── actions/
│   ├── executor.py            # Controlled execution wrapper with permission checks
│   ├── process_actions.py     # Terminate process, change priority
│   └── smart_cleaner.py       # Smart cache purger
│
├── security/
│   ├── audit.py               # Action audit logger
│   └── sandbox.py             # Protected system process guard
│
├── api/
│   ├── server.py              # FastAPI server & static UI mount
│   ├── routes_telemetry.py    # Telemetry REST endpoints
│   ├── routes_chat.py         # AI Copilot chat endpoints
│   └── websocket_manager.py   # WebSocket streaming manager
│
├── ui/
│   ├── terminal/
│   │   └── dashboard.py       # Rich Live Terminal User Interface (TUI)
│   └── dashboard/             # React + Vite + Tailwind CSS Web Dashboard
│
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (optional, for web dashboard development)
- **Ollama** (optional, for local LLM natural language generation): [Download Ollama](https://ollama.com)

---

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HNS-06/LocalOS_AI.git
   cd LocalOS_AI
   ```

2. **Create Python Virtual Environment & Install Dependencies**:
   ```bash
   # Windows
   py -m venv venv
   venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install & Pull Local Ollama Models (Optional for LLM Copilot)**:
   ```bash
   ollama pull deepseek-r1:1.5b
   # or
   ollama pull qwen2.5-coder:7b
   ```

---

### Running LocalOS AI

#### 💻 Option 1: Live Interactive Terminal UI (TUI Mode - Default)
Run the auto-refreshing TUI directly inside your terminal:
```bash
venv\Scripts\python.exe main.py
```
- **TUI Key Shortcuts**: Press `1` for Dashboard, `2` for Process Manager, `3` for AI Copilot Chat, `4` for Baseline Diffs, `C` to clean temp files, `K` to terminate a process, `Q` to quit.
- **Slash Commands**: Type `/clean`, `/kill-hog`, `/why`, or `/events` inside the command prompt.

---

#### 🌐 Option 2: Web Dashboard Mode
To launch the REST API and live Web Dashboard:
```bash
venv\Scripts\python.exe main.py --web
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

---

## 🔒 Security & Safety Model

- **No Arbitrary Shell Code Execution**: The LLM cannot execute raw PowerShell, CMD, or bash code.
- **Explicit Action Approvals**: Modifying operations (`terminate_process`, `clear_cache`, `disable_startup_item`) require user confirmation via terminal prompt or UI modal.
- **Kernel Process Guard**: Critical Windows system processes (`csrss.exe`, `services.exe`, `svchost.exe`, PIDs 0–4) cannot be killed.
- **Audit Logging**: All executed actions are recorded with timestamps, user query, tool called, and result in `database/localos.db`.

---

## 📜 Requirements (`requirements.txt`)

```text
psutil>=5.9.0
fastapi>=0.100.0
uvicorn>=0.22.0
scikit-learn>=1.2.0
numpy>=1.24.0
pandas>=2.0.0
requests>=2.31.0
websockets>=11.0
pywin32>=306; sys_platform == 'win32'
wmi>=1.5.1; sys_platform == 'win32'
GPUtil>=1.4.0
pydantic>=2.0.0
rich>=13.0.0
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
