from agentlab.utils.templates import render_mapping, render_template


def test_render_template_basic():
    assert render_template("Hello {{name}}", {"name": "World"}) == "Hello World"


def test_render_template_missing_kept():
    assert render_template("{{unknown}}", {}) == "{{unknown}}"


def test_render_mapping_nested():
    data = {"a": "{{x}}", "b": {"c": "{{y}}"}, "d": ["{{x}}", 1, {"e": "{{y}}"}]}
    out = render_mapping(data, {"x": "X", "y": "Y"})
    assert out == {"a": "X", "b": {"c": "Y"}, "d": ["X", 1, {"e": "Y"}]}
