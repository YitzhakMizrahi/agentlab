# AgentLab

A CLI framework for designing, running, and evaluating AI **agent blueprints** locally. Write agents as clean YAML configs, run them with local LLMs via **Ollama** (default `qwen3:8b`), mock tools, and add evaluations.

## Quickstart

```bash
# 1) Ensure Ollama is running and qwen3:8b is pulled
ollama pull qwen3:8b

# 2) Install
pip install -e .

# 3) Run an agent
agentlab run blueprints/summarizer.yaml -i "Login failed due to rate limits"

# 4) Run evaluations
agentlab eval blueprints/summarizer.yaml
```

## Concepts
- **Blueprint**: YAML spec of agent purpose, tools, memory, and plan
- **Plan**: ordered steps (tool_use | generate | note)
- **Tools**: mocked for local development
- **LLM**: local via Ollama (Qwen3:8b by default)

## Roadmap (Phased)
- Phase 1 (MVP): CLI, YAML config, Ollama, mocks, eval harness ✅
- Phase 2 (in progress):
  - [x] Tool SDK (entry points, registry, example plugin)
  - [x] Streaming output (CLI --stream)
  - [x] Structured inputs (CLI --input-json/--input-file)
  - [x] CI + pre-commit (ruff, mypy, pytest)
  - [ ] OpenAPI ingester for tools
  - [ ] Richer evaluators (contains/regex/any-of/JSONPath, JUnit report)
  - [ ] Prompt templates/patterns
- Phase 3: Visual designer (Next.js), agent graphs, export to LangChain

## Plugins / Tools
See `docs/plugins.md` for how to create and publish external tools via entry points.