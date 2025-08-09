from agentlab.config_loader import Blueprint
from agentlab.runner import run_agent


def test_runner_accepts_dict_input(monkeypatch):
    bp = Blueprint(
        name="dict-agent",
        plan=[
            {
                "step": "tool_use",
                "name": "summarize",
                "with": {"text": "{{title}}: {{details.msg}}"},
            },
            {"step": "generate", "name": "final"},
        ],
    )

    async def fake_acomplete(prompt: str, **_):
        return "done"

    import agentlab.runner as R

    monkeypatch.setattr(R, "acomplete", fake_acomplete)

    payload = {"title": "Issue", "details": {"msg": "Rate limit exceeded"}}
    out = run_agent(bp, input_text=payload)
    assert out["agent"] == "dict-agent"
    assert any("Rate limit exceeded" in c for c in out["tool_context"])  # templated
