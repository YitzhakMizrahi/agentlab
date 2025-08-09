# 🧪 AgentLab
**Local-First Test Harness for AI Agents**  
Run, test, and debug your agents anywhere — no cloud, no lock-in, no noise.

## Why AgentLab?
Most “agent sandboxes” are cloud-heavy and tied to a single framework. AgentLab is **lightweight**, **offline**, and **framework-agnostic** — giving you a reproducible developer experience for building and testing AI agents from your terminal.

**Perfect for**
- Backend & AI engineers who want **fast iteration** without cloud friction
- Integrating agents into **existing systems**
- **Reproducible, CI-friendly** agent tests

## Key Features
- **Local-First** — Works with Ollama (default model: `qwen3:8b`) or any HTTP LLM endpoint
- **Framework-Agnostic** — Blueprints are plain YAML; adapters can target LangChain/LlamaIndex later
- **Reproducible Tests** — Define evaluation cases alongside the blueprint
- **Mockable Tools** — Run deterministic CI without hitting real APIs
- **Developer-First UX** — CLI-first, Git-friendly configs

## Quick Start
```bash
# 0) Ensure Ollama has the model
ollama pull qwen3:8b

# 1) (Optional) Create venv
python -m venv .venv && source .venv/bin/activate

# 2) Install
pip install -e .

# 3) Run an example agent (summarizer)
agentlab run blueprints/summarizer.yaml \
  -i "User failed login due to rate limits." \
  --model qwen3:8b

# 4) Run its evaluations
agentlab eval blueprints/summarizer.yaml
```

## Example: Incident Triage Agent
Run a second example focused on operations-style summaries.

```bash
agentlab run blueprints/incident-triage.yaml \
  -i "Database connection timeout after 5 retries." \
  --model qwen3:8b
```

### Blueprint (`blueprints/incident-triage.yaml`)
```yaml
name: incident-triage
description: Triage incident statements into a concise, actionable summary.
system_prompt: |
  You are an incident triage assistant. Produce a single sentence that states the core issue
  and the likely action. Avoid hedging. If a cause is clear (e.g., rate limit, timeout),
  include it directly.

tools: []

memory:
  strategy: short_term

plan:
  - step: generate
    name: final

evaluation:
  - input: "Database connection timeout after 5 retries."
    expected: "timeout"
  - input: "User login failed due to exceeding rate limits."
    expected: "rate limit"
```

## Concepts
- **Blueprint**: YAML spec for agent purpose, tools, memory, plan, and eval cases
- **Plan**: ordered steps (currently `tool_use` | `note` | `generate`)
- **Tools**: mocked for local dev; real tool adapters can be added later
- **LLM**: local via Ollama (Qwen3:8b by default)

## Roadmap
- Phase 1 (MVP): CLI, YAML config, Ollama, mocks, basic evals ✅
- Phase 2: `agentlab init`, streaming CLI, prompt templating, richer evaluators
- Phase 3: TUI mode, adapters (LangChain/LlamaIndex), exportable reports

## Plugins / Tools
See `docs/plugins.md` for how to create and publish external tools via entry points.

## License
MIT