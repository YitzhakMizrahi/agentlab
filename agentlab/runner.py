## agentlab/runner.py

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

import orjson

from .config_loader import Blueprint
from .llm.ollama_client import acomplete
from .tools.registry import get_tool, load_default_tools, load_plugin_tools
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
    input_text: Optional[Union[str, Dict[str, Any]]] = None,
    model_name: str = "qwen3:8b",
    stream: bool = False,
) -> Dict[str, Any]:
    """Execute the plan with simple semantics: tool_use steps populate tool_context; generate creates final answer."""
    tool_contexts: List[str] = []
    # Normalize input for templating and user prompt
    if isinstance(input_text, dict):
        variables: Dict[str, Any] = input_text
        try:
            user_input_str = orjson.dumps(input_text).decode()
        except Exception:
            user_input_str = str(input_text)
    else:
        variables = {"input": input_text or ""}
        user_input_str = input_text or ""

    # Load plugin tools once per run
    try:
        load_plugin_tools()
    except Exception:
        pass

    for step in blueprint.plan:
        if step.kind == "tool_use":
            rendered_args = render_mapping(step.with_ or {"input": user_input_str}, variables)
            output = _execute_tool(step.name or "", rendered_args)
            label = step.name or "tool"
            args_str = (
                " ".join(f"{k}={v}" for k, v in rendered_args.items()) if rendered_args else ""
            )
            tool_contexts.append(f"[{label}{(' ' + args_str) if args_str else ''}] {output}")
        elif step.kind == "note":
            tool_contexts.append(f"[note] {step.with_ or ''}")
        elif step.kind == "generate":
            # Single LLM generation; include prior tool contexts
            prompt = _render_prompt(
                blueprint.system_prompt,
                user_input_str,
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
                "input": input_text or "",
                "tool_context": tool_contexts,
                "output": text,
            }

    # If no generate step was found, return context only
    return {
        "agent": blueprint.name,
        "input": input_text or "",
        "tool_context": tool_contexts,
        "output": "",
        "warning": "No generate step in plan.",
    }
