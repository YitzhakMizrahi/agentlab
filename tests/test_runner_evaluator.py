from pathlib import Path

from agentlab.config_loader import load_blueprint
from agentlab.evaluator import run_evaluations
from agentlab.runner import run_agent


def make_blueprint(tmp_path: Path) -> Path:
    p = tmp_path / "bp.yaml"
    p.write_text(
        """
name: summarizer-agent
system_prompt: simple
tools:
  - name: internalSearch
plan:
  - step: tool_use
    name: internalSearch
    with:
      query: "{{input}}"
  - step: generate
evaluation:
  - input: foo
    expected: foo
        """.strip()
    )
    return p


def test_run_agent_no_llm(monkeypatch, tmp_path: Path):
    # Monkeypatch LLM to return deterministic text
    from agentlab import runner

    async def fake_acomplete(prompt: str, model: str = "qwen3:8b", stream: bool = False, **_):
        return "result with foo"

    monkeypatch.setattr(runner, "acomplete", fake_acomplete)

    bp = load_blueprint(make_blueprint(tmp_path))
    out = run_agent(bp, input_text="foo")
    assert out["agent"] == "summarizer-agent"
    assert any("internalSearch" in c for c in out["tool_context"])  # tool ran
    assert "result with foo" in out["output"]


def test_evaluator(monkeypatch, tmp_path: Path):
    from agentlab import runner

    async def fake_acomplete(prompt: str, model: str = "qwen3:8b", stream: bool = False, **_):
        return "foo bar"

    monkeypatch.setattr(runner, "acomplete", fake_acomplete)

    bp = load_blueprint(make_blueprint(tmp_path))
    summary = run_evaluations(bp)
    assert summary["total"] == 1
    assert summary["passed"] == 1
