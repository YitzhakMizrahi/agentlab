from agentlab.config_loader import Blueprint, PlanStep
from agentlab.evaluator import run_evaluations


def _bp_for_output(text: str) -> Blueprint:
    # A blueprint that returns a fixed output via monkeypatched LLM will be provided by the test
    return Blueprint(name="t", plan=[PlanStep(kind="generate", name="final")], evaluation=[])


def test_evaluator_contains_regex_anyof(monkeypatch):
    bp = _bp_for_output("x")

    async def fake_acomplete(prompt: str, **_):
        return "Error: code 404 not found"

    import agentlab.runner as R

    monkeypatch.setattr(R, "acomplete", fake_acomplete)

    bp.evaluation = [
        {"input": "", "checks": [{"type": "contains", "value": "404"}]},
        {"input": "", "checks": [{"type": "regex", "pattern": r"code\s+404"}]},
        {"input": "", "checks": [{"type": "any_of", "options": ["500", "404"]}]},
    ]

    summary = run_evaluations(bp)
    assert summary["passed"] == 3
