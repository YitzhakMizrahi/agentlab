from types import SimpleNamespace
from typing import Any, Dict

from agentlab.tools.registry import get_tool, list_tools, load_plugin_tools


def test_load_plugin_tools_monkeypatch(monkeypatch):
    calls: Dict[str, Any] = {}

    def external_tool(x: int) -> int:
        calls["x"] = x
        return x * 2

    class FakeEntryPoint:
        def __init__(self, name: str, obj):
            self.name = name
            self._obj = obj

        def load(self):
            return self._obj

    def fake_entry_points():
        # Simulate both single callable and a dict mapping
        return SimpleNamespace(
            select=lambda group: [
                FakeEntryPoint("external_tool", external_tool),
                FakeEntryPoint("external_pack", {"ext_map": external_tool}),
            ]
        )

    monkeypatch.setattr(
        "agentlab.tools.registry.importlib_metadata.entry_points", fake_entry_points
    )

    load_plugin_tools()

    assert "external_tool" in list_tools() or "ext_map" in list_tools()
    fn = get_tool("external_tool") or get_tool("ext_map")
    assert fn is not None
    assert fn(3) == 6
    assert calls["x"] == 3
