from types import SimpleNamespace

from agentlab.config_loader import load_blueprint
from agentlab.runner import run_agent


def test_plugin_tools_integration(monkeypatch, tmp_path):
    # Simulate entry points for an external plugin
    def add(x: int, y: int) -> int:
        return int(x) + int(y)

    class FakeEP:
        def __init__(self, name, obj):
            self.name = name
            self._obj = obj

        def load(self):
            return self._obj

    def fake_entry_points():
        return SimpleNamespace(select=lambda group: [FakeEP("add", add)])

    monkeypatch.setattr(
        "agentlab.tools.registry.importlib_metadata.entry_points", fake_entry_points
    )

    # Create a minimal blueprint using the plugin tool
    bp_path = tmp_path / "bp.yaml"
    bp_path.write_text(
        """
name: math-agent
plan:
  - step: tool_use
    name: add
    with:
      x: 2
      y: 3
  - step: generate
        """.strip()
    )
    bp = load_blueprint(bp_path)

    # Stub LLM to avoid real network calls in CI
    async def fake_acomplete(prompt: str, **_):
        return "ok"

    import agentlab.runner as R

    monkeypatch.setattr(R, "acomplete", fake_acomplete)

    out = run_agent(bp, input_text="unused")
    assert out["agent"] == "math-agent"
    assert any("[add] 5" in c for c in out["tool_context"])  # tool result recorded
