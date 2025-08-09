## agentlab/runner.py

from __future__ import annotations
from typing import Any, Dict, List, Optional
from .config_loader import Blueprint, PlanStep
from .mocks.tool_mocks import MOCK_REGISTRY
import asyncio
from .llm.ollama_client import acomplete


def _render_prompt(system: str, user: str, tool_context: str | None = None) -> str:
    parts: List[str] = [f"<system>
{system}
</system>"]
    if tool_context:
        parts.append(f"<tools>
{tool_context}
</tools>")
    parts.append(f"<user>
{user}
</user>")
    return "

".join(parts)


def _execute_tool(name: str, args: Dict[str, Any] | None) -> str:
    fn = MOCK_REGISTRY.get(name)
    if not fn:
        return f"[tool-error] Unknown tool: {name}"
    args = args or {}
    try:
        return str(fn(**args))
    except TypeError:
        # Fallback: pass single 'input' param if available
        if "input" in args:
            return str(fn(args["input"]))
        return f"[tool-error] Bad arguments for tool: {name}"


def run_agent(
    blueprint: Blueprint,
    input_text: Optional[str] = None,
    model_name: str = "qwen3:8b",
    stream: bool = False,
) -> Dict[str, Any]:
    """Execute the plan with simple semantics: tool_use steps populate tool_context; generate creates final answer."""
    tool_contexts: List[str] = []
    user_input = input_text or ""

    for step in blueprint.plan:
        if step.kind == "tool_use":
            output = _execute_tool(step.name or "", step.with or {"input": user_input})
            tool_contexts.append(f"[{step.name}] {output}")
        elif step.kind == "note":
            tool_contexts.append(f"[note] {step.with or ''}")
        elif step.kind == "generate":
            # Single LLM generation; include prior tool contexts
            prompt = _render_prompt(
                blueprint.system_prompt,
                user_input,
                tool_context="
".join(tool_contexts) if tool_contexts else None,
            )
            text = asyncio.run(acomplete(prompt=prompt, model=model_name, stream=stream))
            return {
                "agent": blueprint.name,
                "input": user_input,
                "tool_context": tool_contexts,
                "output": text,
            }

    # If no generate step was found, return context only
    return {
        "agent": blueprint.name,
        "input": user_input,
        "tool_context": tool_contexts,
        "output": "",
        "warning": "No generate step in plan.",
    }