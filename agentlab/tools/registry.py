from __future__ import annotations

import importlib.metadata as importlib_metadata
from typing import Any, Callable, Dict, Iterable, List, Optional

ToolFunction = Callable[..., Any]


_TOOL_REGISTRY: Dict[str, ToolFunction] = {}


def register_tool(name: str, fn: ToolFunction) -> None:
    """Register a tool function under a unique name."""
    _TOOL_REGISTRY[name] = fn


def get_tool(name: str) -> Optional[ToolFunction]:
    """Retrieve a tool by name if registered; otherwise None."""
    return _TOOL_REGISTRY.get(name)


def list_tools() -> List[str]:
    """Return a sorted list of available tool names."""
    return sorted(_TOOL_REGISTRY.keys())


def load_default_tools() -> None:
    """Load built-in mock tools once. Safe to call multiple times."""
    # Import locally to avoid import cycles during package init
    from agentlab.mocks import tool_mocks

    # Register/mock tools dynamically from the mock registry
    for name, fn in tool_mocks.MOCK_REGISTRY.items():
        register_tool(name, fn)


def load_plugin_tools(entry_point_group: str = "agentlab.tools") -> None:
    """Discover and load tools from installed packages via entry points.

    Packages can expose an entry point mapping of name->callable (e.g., a dict), or individual
    callables. If an entry point returns a dict, we register all items.
    """
    group: Iterable[Any] = []
    try:
        eps = importlib_metadata.entry_points()
        if hasattr(eps, "select"):
            group = eps.select(group=entry_point_group)
        else:
            # Older importlib_metadata: mapping-style access
            group = importlib_metadata.entry_points().get(entry_point_group, [])
    except Exception:
        group = []

    for ep in group:
        try:
            obj = ep.load()
        except Exception:
            continue
        if isinstance(obj, dict):
            for name, fn in obj.items():
                if callable(fn):
                    register_tool(str(name), fn)
        elif callable(obj):
            register_tool(str(ep.name), obj)
