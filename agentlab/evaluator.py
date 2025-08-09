## agentlab/evaluator.py

from __future__ import annotations
from typing import Dict, Any
from .config_loader import Blueprint
from .runner import run_agent


def run_evaluations(blueprint: Blueprint, model_name: str = "qwen3:8b") -> Dict[str, Any]:
    results = []
    passed = 0
    for case in blueprint.evaluation:
        outcome = run_agent(blueprint, input_text=case.input, model_name=model_name)
        output = (outcome.get("output") or "").strip()
        ok = case.expected.lower() in output.lower()
        results.append({
            "input": case.input,
            "expected_substring": case.expected,
            "actual": output,
            "pass": ok,
        })
        if ok:
            passed += 1
    return {
        "agent": blueprint.name,
        "total": len(blueprint.evaluation),
        "passed": passed,
        "results": results,
    }