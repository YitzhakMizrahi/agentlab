from agentlab.config_loader import Blueprint
from agentlab.runner import run_agent


def test_strip_think(monkeypatch):
    bp = Blueprint(name="t", plan=[{"step": "generate", "name": "final"}])

    async def fake_acomplete(prompt: str, **_):
        return "<think>internal</think>Visible"

    import agentlab.runner as R

    monkeypatch.setattr(R, "acomplete", fake_acomplete)

    out = run_agent(bp, input_text="x")
    assert out["output"] == "Visible"
