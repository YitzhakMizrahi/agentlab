## agentlab/mocks/tool_mocks.py

from __future__ import annotations

from typing import Any, Dict

# Add simple deterministic mocks to keep agent runs testable


def internalSearch(query: str) -> str:
    # In real life, this would hit a vector store. For now, return a canned snippet.
    return f"[mock-internalSearch] top_result: Related info for: {query[:80]}"


def summarize(text: str) -> str:
    # A fake summarizer we can call as a tool (distinct from LLM generate step)
    return "[mock-summarize] " + (text[:160] + ("…" if len(text) > 160 else ""))


MOCK_REGISTRY: Dict[str, Any] = {
    "internalSearch": internalSearch,
    "summarize": summarize,
}
