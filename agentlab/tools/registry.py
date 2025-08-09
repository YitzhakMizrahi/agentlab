from __future__ import annotations

from typing import Callable, Dict, Any, List, Optional


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


