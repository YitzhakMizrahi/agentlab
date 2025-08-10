from agentlab.config_loader import load_blueprint
from agentlab.evaluator import run_evaluations


def test_my_agent_blueprint(tmp_path):
    path = tmp_path / "my-agent.yaml"
    path.write_text(blueprint_content)
    bp = load_blueprint(path)

    # Monkeypatch LLM to deterministic output
    import agentlab.runner as R

    async def fake_acomplete(prompt: str, **_):
        return "sample output"

    R.acomplete = fake_acomplete

    summary = run_evaluations(bp)
    assert summary["total"] >= 1


blueprint_content = """
name: my-agent
description: A starter agent created by agentlab init.
system_prompt: |
  You are a precise assistant. Produce a short, direct answer.

tools: []

memory:
  strategy: short_term

plan:
  - step: generate
    name: final

evaluation:
  - input: "Sample input here"
    expected: "sample"

"""
