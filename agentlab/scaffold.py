from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

BLUEPRINT_TEMPLATE = """name: {name}
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


TEST_TEMPLATE = """from agentlab.config_loader import load_blueprint
from agentlab.evaluator import run_evaluations


def test_{py_slug}_blueprint(tmp_path):
    path = tmp_path / "{slug}.yaml"
    path.write_text(blueprint_content)
    bp = load_blueprint(path)

    # Monkeypatch LLM to deterministic output
    import agentlab.runner as R

    async def fake_acomplete(prompt: str, **_):
        return "sample output"

    R.acomplete = fake_acomplete

    summary = run_evaluations(bp)
    assert summary["total"] >= 1
"""


def create_blueprint_scaffold(
    name: str,
    out_dir: Path,
    with_tests: bool = False,
    force: bool = False,
) -> List[Tuple[Path, str]]:
    """Create a new blueprint YAML (and optional test) under out_dir.

    Returns a list of (path, status) tuples where status is "created" or "skipped".
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = name.replace(" ", "-").lower()
    blueprint_path = out_dir / f"{slug}.yaml"
    statuses: List[Tuple[Path, str]] = []

    if blueprint_path.exists() and not force:
        statuses.append((blueprint_path, "skipped (exists)"))
    else:
        blueprint_text = BLUEPRINT_TEMPLATE.format(name=slug)
        blueprint_path.write_text(blueprint_text, encoding="utf-8")
        statuses.append((blueprint_path, "created"))

    if with_tests:
        tests_dir = Path("tests") / "blueprints"
        tests_dir.mkdir(parents=True, exist_ok=True)
        test_path = tests_dir / f"test_{slug}.py"
        if test_path.exists() and not force:
            statuses.append((test_path, "skipped (exists)"))
        else:
            # Write a small helper variable to avoid nested triple quotes issues
            blueprint_content = BLUEPRINT_TEMPLATE.format(name=slug)
            py_slug = slug.replace("-", "_")
            test_text = (
                TEST_TEMPLATE.format(slug=slug, py_slug=py_slug)
                + "\nblueprint_content = '''\n"
                + blueprint_content
                + "\n'''\n"
            )
            test_path.write_text(test_text, encoding="utf-8")
            statuses.append((test_path, "created"))

    return statuses
