# Tool SDK — Building Plugin Tools

## Overview
AgentLab discovers external tools via Python entry points under the group `agentlab.tools`.
Plugins can expose either:
- a single callable per entry point, or
- a mapping (dict) of `name -> callable`

The callable signature is flexible; pass keyword args from your blueprint `with:` block.

## 1) Write your tool
```python
# my_ext_pkg/tools.py

def add(x: int, y: int) -> int:
    return x + y

# Optional: expose multiple tools as a mapping

def get_tools() -> dict[str, object]:
    return {
        "multiply": lambda x, y: x * y,
    }
```

## 2) Declare entry points
Add to your plugin's `pyproject.toml`:
```toml
[project]
name = "my-ext-pkg"
version = "0.1.0"
requires-python = ">=3.10"

[project.entry-points."agentlab.tools"]
# Single callable
add = "my_ext_pkg.tools:add"
# Mapping (multiple tools)
my_ext_pkg = "my_ext_pkg.tools:get_tools"
```

Install your plugin (editable during development):
```bash
pip install -e /path/to/my-ext-pkg
```

## 3) Use in a blueprint
```yaml
# blueprints/math.yaml
name: math-agent
plan:
  - step: tool_use
    name: add
    with:
      x: 2
      y: 3
  - step: generate
    name: final
```

Run it:
```bash
python -m agentlab.cli run blueprints/math.yaml -i "unused here"
```

AgentLab will auto-discover plugin tools at runtime. If the tool is not found, verify your plugin is installed and that the entry point names match the tool names used in the blueprint.

## Referencing inputs in tool args
- Use `{{input}}` to reference the raw string input (from `-i/--input`).
- For structured inputs (dicts), you can reference keys with dot paths, e.g. `{{user.name}}` or `{{event.payload.id}}`.

Example:
```yaml
plan:
  - step: tool_use
    name: add
    with:
      x: "{{metrics.current}}"
      y: 7
  - step: generate
```

Run with structured input:
```bash
python -m agentlab.cli run blueprints/math.yaml \
  --input-json '{"metrics": {"current": 5}}'
```

Or load from a file:
```bash
python -m agentlab.cli run blueprints/math.yaml --input-file payload.json
```


