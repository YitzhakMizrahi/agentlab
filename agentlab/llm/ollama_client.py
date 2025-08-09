## agentlab/llm/ollama_client.py

from __future__ import annotations
import httpx
from typing import Optional, Dict, Any

OLLAMA_URL = "http://localhost:11434"


async def acomplete(
    prompt: str,
    model: str = "qwen3:8b",
    stream: bool = False,
    client: Optional[httpx.AsyncClient] = None,
    **kwargs: Any,
) -> str:
    payload: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
    payload.update(kwargs)
    _client = client or httpx.AsyncClient(timeout=60)
    try:
        resp = await _client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    finally:
        if client is None:
            await _client.aclose()