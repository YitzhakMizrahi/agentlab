from __future__ import annotations

from typing import Dict, Any


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """Very small and safe curly-brace template renderer.

    Replaces occurrences of {{var}} with variables[var] if present; otherwise leaves as-is.
    This is intentionally minimal to avoid bringing in a templating engine.
    """
    result = []
    i = 0
    while i < len(template):
        start = template.find("{{", i)
        if start == -1:
            result.append(template[i:])
            break
        result.append(template[i:start])
        end = template.find("}}", start + 2)
        if end == -1:
            # unmatched, append rest
            result.append(template[start:])
            break
        key = template[start + 2 : end].strip()
        value = variables.get(key, f"{{{{{key}}}}}")
        result.append(str(value))
        i = end + 2
    return "".join(result)


def render_mapping(mapping: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    """Render a dict by applying render_template to any string values recursively."""
    rendered: Dict[str, Any] = {}
    for k, v in mapping.items():
        if isinstance(v, str):
            rendered[k] = render_template(v, variables)
        elif isinstance(v, dict):
            rendered[k] = render_mapping(v, variables)
        elif isinstance(v, list):
            rendered[k] = [render_mapping(i, variables) if isinstance(i, dict) else (render_template(i, variables) if isinstance(i, str) else i) for i in v]
        else:
            rendered[k] = v
    return rendered


