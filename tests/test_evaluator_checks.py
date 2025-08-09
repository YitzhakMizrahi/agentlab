from agentlab.config_loader import Blueprint, EvalCase
from agentlab.evaluator import run_evaluations


def _bp_for_output(text: str) -> Blueprint:
    # Build via dict + model_validate to avoid mypy call-arg noise while keeping runtime schema
    data = {"name": "t", "plan": [{"step": "generate", "name": "final"}], "evaluation": []}
    return Blueprint.model_validate(data)


def test_evaluator_contains_regex_anyof(monkeypatch):
    bp = _bp_for_output("x")

    async def fake_acomplete(prompt: str, **_):
        return "Error: code 404 not found"

    import agentlab.runner as R

    monkeypatch.setattr(R, "acomplete", fake_acomplete)

    bp.evaluation = [
        EvalCase(input="", checks=[{"type": "contains", "value": "404"}]),
        EvalCase(input="", checks=[{"type": "regex", "pattern": r"code\s+404"}]),
        EvalCase(input="", checks=[{"type": "any_of", "options": ["500", "404"]}]),
    ]

    summary = run_evaluations(bp)
    assert summary["passed"] == 3
