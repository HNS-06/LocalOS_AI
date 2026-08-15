import os
import sys
import time
import asyncio
from typing import Dict, Any, List, Optional

# Force UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from core.orchestrator import orchestrator
from ai.llm_adapter import ollama_adapter
from ai.context_engine import context_engine
from database.events_db import get_recent_events
from database.telemetry_db import get_what_changed_telemetry
from actions.executor import action_executor
from analyzers.startup import StartupAnalyzer

console = Console(force_terminal=True)

class LocalOSTerminalApp:
    def __init__(self):
        self.running = True
        self.active_view = "dashboard"  # dashboard, processes, security, reports
        self.startup_analyzer = StartupAnalyzer()

    def generate_header(self) -> Panel:
        is_ollama = ollama_adapter.is_ollama_available()
        ollama_status = f"[bold green]Ollama Online ({ollama_adapter.default_model})[/bold green]" if is_ollama else "[bold yellow]Local Rules Fallback[/bold yellow]"
        
        title_text = Text()
        title_text.append("[LocalOS AI] ", style="bold cyan")
        title_text.append("--- Intelligent OS Copilot Terminal ", style="bold white")
        title_text.append(f" | Real-Time Telemetry Stream | {ollama_status}", style="dim")
        
        return Panel(
            title_text,
            border_style="cyan",
            subtitle="Keys: [1] Dashboard  [2] Processes  [3] AI Copilot  [4] What Changed?  [5] Security  [6] Reports  [C] Clean Cache  [K] Kill  [Q] Quit",
            subtitle_align="center"
        )

    def generate_dashboard_view(self, snapshot: Dict[str, Any]) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="top_metrics", size=11),
            Layout(name="bottom_info", size=14)
        )

        layout["header"].update(self.generate_header())

        cpu = snapshot.get("cpu", {})
        mem = snapshot.get("memory", {})
        disk = snapshot.get("disk", {})
        net = snapshot.get("network", {})
        proc = snapshot.get("processes", {})

        # Top Metrics Grid Table
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)

        # CPU Card
        cpu_val = cpu.get("total_percent", 0.0)
        cpu_color = "bold red" if cpu_val > 85 else ("bold yellow" if cpu_val > 60 else "bold cyan")
        cpu_panel = Panel(
            f"[{cpu_color}]{cpu_val}%[/{cpu_color}]\n[dim]Freq: {cpu.get('frequency_mhz', 0)}MHz\nTop: {proc.get('top_cpu_process', 'None')}[/dim]",
            title="[CPU] Utilization",
            border_style="cyan"
        )

        # RAM Card
        ram_val = mem.get("percent", 0.0)
        ram_used = mem.get("used_gb", 0.0)
        ram_color = "bold red" if ram_val > 85 else "bold blue"
        ram_panel = Panel(
            f"[{ram_color}]{ram_val}%[/{ram_color}]\n[dim]{ram_used} GB used\nTop: {proc.get('top_ram_process', 'None')}[/dim]",
            title="[RAM] Memory",
            border_style="blue"
        )

        # Disk Card
        disk_val = disk.get("percent", 0.0)
        disk_panel = Panel(
            f"[bold green]{disk_val}%[/bold green]\n[dim]Read: {disk.get('read_mbs', 0)}MB/s\nWrite: {disk.get('write_mbs', 0)}MB/s[/dim]",
            title="[DISK] Storage",
            border_style="green"
        )

        # Network Card
        sent = net.get("sent_kbps", 0.0)
        recv = net.get("recv_kbps", 0.0)
        net_panel = Panel(
            f"[bold yellow]{round(sent+recv, 1)} Kbps[/bold yellow]\n[dim]Sent: {sent} Kbps\nRecv: {recv} Kbps[/dim]",
            title="[NET] Traffic",
            border_style="yellow"
        )

        grid.add_row(cpu_panel, ram_panel, disk_panel, net_panel)
        layout["top_metrics"].update(grid)

        # Bottom Info Split (Top Processes & Active Alerts)
        layout["bottom_info"].split_row(
            Layout(name="processes_summary", ratio=2),
            Layout(name="alerts_summary", ratio=1)
        )

        # Process Table Summary
        p_table = Table(title="Top Real-Time Resource Consumers", expand=True, border_style="dim")
        p_table.add_column("PID", style="dim", width=8)
        p_table.add_column("Process Name", style="bold white")
        p_table.add_column("CPU %", justify="right")
        p_table.add_column("RAM MB", justify="right")

        top_by_ram = proc.get("top_by_ram", [])[:6]
        for p in top_by_ram:
            cpu_style = "bold red" if p.get("cpu_percent", 0) > 20 else "white"
            ram_style = "bold yellow" if p.get("memory_mb", 0) > 1000 else "white"
            p_table.add_row(
                str(p.get("pid")),
                p.get("name", "unknown"),
                f"[{cpu_style}]{p.get('cpu_percent')}%[/{cpu_style}]",
                f"[{ram_style}]{p.get('memory_mb')} MB[/{ram_style}]"
            )
        layout["bottom_info"]["processes_summary"].update(Panel(p_table, border_style="dim"))

        # Alerts Box
        alerts_text = Text()
        if orchestrator.active_alerts:
            for a in orchestrator.active_alerts:
                alerts_text.append(f"[!] {a['title']}\n{a['description']}\n\n", style="bold yellow")
        else:
            alerts_text.append("[OK] All deterministic rule checks nominal.\nNo critical threshold breaches.", style="green")

        if orchestrator.active_anomalies:
            for anom in orchestrator.active_anomalies[-2:]:
                alerts_text.append(f"[*] {anom['title']} ({anom['confidence']}% conf)\n{anom['description']}\n\n", style="bold magenta")

        layout["bottom_info"]["alerts_summary"].update(Panel(alerts_text, title="Alerts & Anomaly Monitor", border_style="magenta"))

        return layout

    def generate_processes_view(self, snapshot: Dict[str, Any]) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="table", size=24)
        )
        layout["header"].update(self.generate_header())

        procs = snapshot.get("processes", {}).get("processes_sample", [])
        table = Table(title="Live Process Intelligence Manager", expand=True, border_style="cyan")
        table.add_column("PID", style="dim", width=8)
        table.add_column("Process Name", style="bold white")
        table.add_column("CPU %", justify="right")
        table.add_column("Memory (MB)", justify="right")
        table.add_column("Status", style="dim")
        table.add_column("Executable Path", style="dim", overflow="fold")

        for p in procs[:20]:
            cpu_style = "bold red" if p.get("cpu_percent", 0) > 15 else "white"
            ram_style = "bold yellow" if p.get("memory_mb", 0) > 1000 else "white"
            table.add_row(
                str(p.get("pid")),
                p.get("name", "unknown"),
                f"[{cpu_style}]{p.get('cpu_percent')}%[/{cpu_style}]",
                f"[{ram_style}]{p.get('memory_mb')} MB[/{ram_style}]",
                p.get("status", "running"),
                p.get("exe") or "System / Protected"
            )
        layout["table"].update(table)
        return layout

    def run_ai_chat_interactive(self):
        console.clear()
        console.print(Panel(
            "[bold cyan]LocalOS AI Copilot --- Natural Language OS Terminal[/bold cyan]\n"
            "Ask questions like: 'Why is my PC slow?', 'What changed?', 'Clear temporary files', or type 'back' to return.",
            border_style="cyan"
        ))
        
        while True:
            query = Prompt.ask("\n[bold cyan]User Ask[/bold cyan]")
            if not query or query.lower() in ["back", "exit", "quit"]:
                break
                
            console.print("[dim]Analyzing real-time telemetry and generating response...[/dim]")
            
            snapshot = orchestrator.collect_all()
            events = get_recent_events(limit=5)
            context = context_engine.build_system_context(
                latest_telemetry=snapshot,
                recent_events=events,
                anomalies=orchestrator.active_anomalies,
                security_warnings=orchestrator.security_warnings
            )
            
            res = ollama_adapter.generate_response(
                user_query=query,
                system_context=context
            )
            
            console.print(Panel(
                Markdown(res.get("content", "")),
                title=f"LocalOS AI Response ({res.get('provider')} - {res.get('model')})",
                border_style="green"
            ))

    def run_process_action_interactive(self):
        pid_str = Prompt.ask("\n[bold yellow]Enter PID to terminate (or 'cancel')[/bold yellow]")
        if not pid_str or pid_str.lower() in ["cancel", "back", "q"]:
            return
            
        try:
            pid = int(pid_str)
        except ValueError:
            console.print("[bold red]Invalid PID integer.[/bold red]")
            return

        confirmed = Confirm.ask(f"[bold red]Are you sure you want to terminate PID {pid}?[/bold red]")
        if confirmed:
            res = action_executor.execute_action(
                tool_name="terminate_process",
                params={"pid": pid},
                user_approved=True,
                user_query=f"User requested termination of PID {pid} via TUI"
            )
            style = "bold green" if res.get("success") else "bold red"
            console.print(f"[{style}]{res.get('message')}[/{style}]")
            time.sleep(2)

    def run_what_changed_interactive(self):
        console.clear()
        console.print("[bold cyan]Analyzing real-time baseline telemetry diffs...[/bold cyan]\n")
        diff_data = get_what_changed_telemetry(hours_back=24)
        events = get_recent_events(limit=15)

        t = Table(title="What Changed? System Baseline Comparison", expand=True)
        t.add_column("Metric", style="bold white")
        t.add_column("Baseline Avg", justify="right")
        t.add_column("Recent Avg", justify="right")
        t.add_column("Variation", justify="right")

        b = diff_data.get("baseline", {})
        r = diff_data.get("recent", {})

        t.add_row(
            "CPU Utilization",
            f"{round(b.get('avg_cpu') or 0, 1)}%",
            f"{round(r.get('avg_cpu') or 0, 1)}%",
            f"{diff_data.get('cpu_diff')}%"
        )
        t.add_row(
            "RAM Footprint",
            f"{round(b.get('avg_ram') or 0, 1)}%",
            f"{round(r.get('avg_ram') or 0, 1)}%",
            f"{diff_data.get('ram_diff')}%"
        )
        console.print(t)

        console.print("\n[bold cyan]Recent Chronological System Events:[/bold cyan]")
        for evt in events:
            t_str = time.strftime('%H:%M:%S', time.localtime(evt.get('timestamp', time.time())))
            console.print(f" * [{t_str}] [bold]{evt['title']}[/bold] - {evt['description']}")
        
        Prompt.ask("\nPress Enter to return...")

    def start_cli(self):
        # Non-blocking keyboard import for Windows
        has_msvcrt = False
        try:
            import msvcrt
            has_msvcrt = True
        except ImportError:
            pass

        # Initial collection
        snapshot = orchestrator.collect_all()

        with Live(self.generate_dashboard_view(snapshot), refresh_per_second=2, console=console, auto_refresh=True) as live:
            while self.running:
                # Real-time telemetry snapshot update every loop iteration
                snapshot = orchestrator.collect_all()

                if self.active_view == "dashboard":
                    live.update(self.generate_dashboard_view(snapshot))
                elif self.active_view == "processes":
                    live.update(self.generate_processes_view(snapshot))

                # Check non-blocking keypresses on Windows
                if has_msvcrt and msvcrt.kbhit():
                    ch = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if ch == '1':
                        self.active_view = "dashboard"
                    elif ch == '2':
                        self.active_view = "processes"
                    elif ch == '3':
                        live.stop()
                        self.run_ai_chat_interactive()
                        live.start()
                    elif ch == '4':
                        live.stop()
                        self.run_what_changed_interactive()
                        live.start()
                    elif ch in ['c', 'C']:
                        live.stop()
                        from actions.smart_cleaner import smart_clean_cache
                        c_res = smart_clean_cache()
                        console.print(f"[bold green]{c_res['message']}[/bold green]")
                        time.sleep(2)
                        live.start()
                    elif ch in ['k', 'K']:
                        live.stop()
                        self.run_process_action_interactive()
                        live.start()
                    elif ch in ['q', 'Q']:
                        self.running = False
                        break

                time.sleep(0.5)

if __name__ == "__main__":
    app = LocalOSTerminalApp()
    app.start_cli()
