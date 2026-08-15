import requests
import json
import logging
import re
from typing import Dict, Any, List, Optional
from core.config import config

logger = logging.getLogger("LocalOS.AI.Ollama")

def sanitize_text(text: str) -> str:
    """Sanitize non-BMP characters / emojis to ensure 100% compatibility on legacy Windows consoles."""
    if not text:
        return ""
    # Strip non-BMP characters
    clean = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # Strip thinking tags if present
    clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL)
    return clean.strip()

class OllamaLLMAdapter:
    def __init__(self):
        self.base_url = config.ollama_base_url
        self.default_model = "qwen2.5-coder:7b"

    def list_available_models(self) -> List[str]:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", []) if "embed" not in m["name"]]
                if models:
                    priority = ["qwen2.5-coder:7b", "deepseek-r1:1.5b", "gemma3:4b", "llama3.1:latest", "mistral:latest"]
                    sorted_models = []
                    for pref in priority:
                        for m in models:
                            if pref in m and m not in sorted_models:
                                sorted_models.append(m)
                    for m in models:
                        if m not in sorted_models:
                            sorted_models.append(m)
                    return sorted_models
        except Exception:
            pass
        return ["qwen2.5-coder:7b", "deepseek-r1:1.5b", "llama3.1:latest"]

    def is_ollama_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    def _resolve_model(self, requested: Optional[str]) -> str:
        available = self.list_available_models()
        if not available:
            return self.default_model

        if requested:
            if requested in available:
                return requested
            req_lower = requested.lower()
            for m in available:
                if req_lower in m.lower():
                    return m

        return available[0]

    def _format_context_summary(self, ctx: Dict[str, Any]) -> str:
        cpu = ctx.get("cpu", {}).get("total_percent", 0.0)
        ram = ctx.get("memory", {}).get("percent", 0.0)
        ram_used = ctx.get("memory", {}).get("used_gb", 0.0)
        top_cpu = ctx.get("cpu", {}).get("top_process", "None")
        top_ram = ctx.get("memory", {}).get("top_process", "None")
        disk = ctx.get("disk", {}).get("percent", 0.0)
        
        return (
            f"- CPU Usage: {cpu}% (Top CPU Process: {top_cpu})\n"
            f"- RAM Usage: {ram}% ({ram_used} GB used, Top RAM Process: {top_ram})\n"
            f"- Primary Disk Usage: {disk}%\n"
        )

    def generate_response(self, user_query: str, system_context: Dict[str, Any], model_name: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_ollama_available():
            return self._fallback_deterministic_response(user_query, system_context)

        target_model = self._resolve_model(model_name)
        ctx_summary = self._format_context_summary(system_context)

        system_prompt = (
            "You are LocalOS AI, an intelligent local OS Copilot. "
            "Analyze the real-time system metrics summary and answer the user's question concisely in clear Markdown."
        )

        prompt_payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Real-time System Metrics:\n{ctx_summary}\nUser Question: {user_query}"}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 350
            }
        }

        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=prompt_payload, timeout=60.0)
            if resp.status_code == 200:
                result = resp.json()
                msg = result.get("message", {})
                
                # Extract text from content or thinking or reasoning_content
                content = msg.get("content") or msg.get("thinking") or msg.get("reasoning_content") or result.get("response") or ""
                clean_content = sanitize_text(content)
                
                if clean_content:
                    return {
                        "provider": "ollama",
                        "model": target_model,
                        "content": clean_content,
                        "context_used": system_context
                    }
        except Exception as e:
            logger.error(f"Error querying Ollama API ({target_model}): {e}")

        return self._fallback_deterministic_response(user_query, system_context)

    def _fallback_deterministic_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        q = query.lower()
        cpu = context.get("cpu", {}).get("total_percent", 0.0)
        ram = context.get("memory", {}).get("percent", 0.0)
        ram_used = context.get("memory", {}).get("used_gb", 0.0)
        top_cpu = context.get("cpu", {}).get("top_process", "None")
        top_ram = context.get("memory", {}).get("top_process", "None")
        disk = context.get("disk", {}).get("percent", 0.0)
        
        answer = (
            f"### System Diagnostic Summary\n\n"
            f"I analyzed your system telemetry:\n"
            f"- **CPU Usage:** {cpu}% (Top: `{top_cpu}`)\n"
            f"- **RAM Usage:** {ram}% ({ram_used} GB used, Top: `{top_ram}`)\n"
            f"- **Disk Usage:** {disk}%\n\n"
            f"**Primary Observations:**\n"
            f"• Storage is at {disk}% capacity.\n"
            f"• Primary memory consumer is `{top_ram}`."
        )

        return {
            "provider": "localos_rules",
            "model": "rule_engine_v1",
            "content": answer,
            "context_used": context
        }

ollama_adapter = OllamaLLMAdapter()
