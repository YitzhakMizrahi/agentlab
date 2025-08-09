from pathlib import Path

from agentlab.config_loader import Blueprint, load_blueprint


def test_load_blueprint_minimal(tmp_path: Path):
    bp_path = tmp_path / "bp.yaml"
    bp_path.write_text(
        """
name: t
plan: []
        """.strip()
    )
    bp = load_blueprint(bp_path)
    assert isinstance(bp, Blueprint)
    assert bp.name == "t"
