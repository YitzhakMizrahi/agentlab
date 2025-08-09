from __future__ import annotations

from typing import Any, Callable, Dict, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """Protocol for a tool implementation.

    A tool may be a callable (function) or an object with a __call__ method.
    The registry treats both uniformly.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - protocol
        ...


ToolRegistryMap = Dict[str, Tool | Callable[..., Any]]
