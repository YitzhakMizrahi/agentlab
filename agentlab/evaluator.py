## agentlab/evaluator.py

from __future__ import annotations

import re
from typing import Any, Dict, List

from .config_loader import Blueprint
from .runner import run_agent


def _check_contains(output: str, needle: str) -> bool:
    return needle.lower() in output.lower()


def _check_regex(output: str, pattern: str, flags: int = re.IGNORECASE) -> bool:
    try:
        return re.search(pattern, output, flags) is not None
    except re.error:
        return False


def _evaluate_checks(
    output: str, checks: List[Dict[str, Any]] | None, expected: str | None
) -> bool:
    if checks:
        for chk in checks:
            typ = str(chk.get("type", "")).lower()
            if typ == "contains":
                if not _check_contains(output, str(chk.get("value", ""))):
                    return False
            elif typ == "regex":
                if not _check_regex(output, str(chk.get("pattern", ""))):
                    return False
            elif typ == "any_of":
                options = chk.get("options", []) or []
                if not any(_check_contains(output, str(opt)) for opt in options):
                    return False
            else:
                return False
        return True
    if expected:
        return _check_contains(output, expected)
    return False


def run_evaluations(blueprint: Blueprint, model_name: str = "qwen3:8b") -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    passed = 0
    for case in blueprint.evaluation:
        outcome = run_agent(blueprint, input_text=case.input, model_name=model_name)
        output = (outcome.get("output") or "").strip()
        ok = _evaluate_checks(output, case.checks, case.expected)
        results.append(
            {
                "input": case.input,
                "expected_substring": case.expected,
                "checks": case.checks,
                "actual": output,
                "pass": ok,
            }
        )
        if ok:
            passed += 1
    return {
        "agent": blueprint.name,
        "total": len(blueprint.evaluation),
        "passed": passed,
        "results": results,
    }
