## agentlab/runner.py

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .config_loader import Blueprint
from .llm.ollama_client import acomplete
from .tools.registry import get_tool, load_default_tools
from .utils.templates import render_mapping


def _render_prompt(system: str, user: str, tool_context: str | None = None) -> str:
    parts: List[str] = [f"<system>\n{system}\n</system>"]
    if tool_context:
        parts.append(f"<tools>\n{tool_context}\n</tools>")
    parts.append(f"<user>\n{user}\n</user>")
    return "\n\n".join(parts)


def _execute_tool(name: str, args: Dict[str, Any] | None) -> str:
    # Ensure default tools are available
    load_default_tools()
    fn = get_tool(name)
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
            # Ensure plugin tools are discoverable each run (lazy import to avoid mypy attr issues)
            try:
                from .tools.registry import load_plugin_tools as _load_plugin_tools

                _load_plugin_tools()
            except Exception:
                pass
            rendered_args = render_mapping(
                step.with_ or {"input": user_input}, {"input": user_input}
            )
            output = _execute_tool(step.name or "", rendered_args)
            tool_contexts.append(f"[{step.name}] {output}")
        elif step.kind == "note":
            tool_contexts.append(f"[note] {step.with_ or ''}")
        elif step.kind == "generate":
            # Single LLM generation; include prior tool contexts
            prompt = _render_prompt(
                blueprint.system_prompt,
                user_input,
                tool_context="\n".join(tool_contexts) if tool_contexts else None,
            )
            if stream:
                fragments: List[str] = []

                def _on_tok(tok: str) -> None:
                    fragments.append(tok)

                asyncio.run(
                    acomplete(prompt=prompt, model=model_name, stream=True, on_token=_on_tok)
                )
                text = "".join(fragments)
            else:
                text = asyncio.run(acomplete(prompt=prompt, model=model_name, stream=False))
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
