## agentlab/llm/ollama_client.py

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import httpx

OLLAMA_URL = "http://localhost:11434"


async def acomplete(
    prompt: str,
    model: str = "qwen3:8b",
    stream: bool = False,
    client: Optional[httpx.AsyncClient] = None,
    on_token: Optional[Callable[[str], None]] = None,
    **kwargs: Any,
) -> str:
    payload: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": bool(stream)}
    payload.update(kwargs)
    _client = client or httpx.AsyncClient(timeout=60)
    try:
        if stream:
            async with _client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                full = []
                async for chunk in resp.aiter_text():
                    if not chunk:
                        continue
                    # Each line is a JSON object from Ollama when streaming
                    for line in chunk.splitlines():
                        if not line.strip():
                            continue
                        try:
                            obj = httpx.Response(200, text=line).json()
                        except Exception:
                            # Fallback if parsing fails; emit raw
                            if on_token:
                                on_token(line)
                            full.append(line)
                            continue
                        token = obj.get("response", "")
                        if token and on_token:
                            on_token(token)
                        if token:
                            full.append(token)
                return "".join(full)
        else:
            resp = await _client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
    finally:
        if client is None:
            await _client.aclose()
