## agentlab/cli.py

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from .config_loader import load_blueprint
from .evaluator import run_evaluations
from .runner import run_agent
from .scaffold import create_blueprint_scaffold
from .tools.openapi.ingest import ingest_openapi

app = typer.Typer(add_completion=False, help="AgentLab CLI")
console = Console()


@app.command()
def run(
    blueprint: Path = typer.Argument(..., exists=True, help="Path to agent blueprint YAML"),
    input_text: str = typer.Option(None, "--input", "-i", help="Optional single input payload"),
    input_json: str = typer.Option(
        None, "--input-json", help="JSON string payload to pass to agent"
    ),
    input_file: Path = typer.Option(None, "--input-file", help="Path to JSON file payload"),
    temperature: float = typer.Option(0.0, "--temperature", help="LLM temperature (default 0)"),
    top_p: float = typer.Option(1.0, "--top-p", help="LLM top-p (default 1)"),
    model: str = typer.Option("qwen3:8b", "--model", help="Ollama model name"),
    stream: bool = typer.Option(False, "--stream", help="Stream output from LLM if supported"),
    strip_think: bool = typer.Option(
        False, "--strip-think", help="Strip <think> tags from outputs"
    ),
    openapi_spec: str = typer.Option(
        None, "--openapi-spec", help="Optional OpenAPI spec URL or file to ingest before run"
    ),
    openapi_tag: str = typer.Option(
        "api", "--openapi-tag", help="Tag/prefix for tools from --openapi-spec"
    ),
    openapi_base_url: str = typer.Option(
        None, "--openapi-base-url", help="Override base URL when ingesting --openapi-spec"
    ),
):
    """Run a single agent from a blueprint."""
    bp = load_blueprint(blueprint)
    # Optional: ingest OpenAPI tools in-process so they are available to the run
    if openapi_spec:
        ingest_openapi(openapi_spec, tag=openapi_tag, base_url_override=openapi_base_url)
    # Determine payload precedence: file > json > text
    payload = input_text
    if input_json:
        payload = json.loads(input_json)
    if input_file:
        payload = json.loads(Path(input_file).read_text(encoding="utf-8"))
    if stream:
        # Display incremental output while the agent runs
        with Live(refresh_per_second=8, console=console) as live:
            # Run once; our run_agent handles streaming accumulation
            result = run_agent(
                bp,
                input_text=payload,
                model_name=model,
                stream=True,
                generation_kwargs={"temperature": temperature, "top_p": top_p},
                strip_think=strip_think,
            )
            live.update(Panel.fit("[bold]Result[/bold]"))
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = run_agent(
            bp,
            input_text=payload,
            model_name=model,
            stream=False,
            generation_kwargs={"temperature": temperature, "top_p": top_p},
            strip_think=strip_think,
        )
        console.print(Panel.fit("[bold]Result[/bold]"))
        print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def eval(
    blueprint: Path = typer.Argument(..., exists=True, help="Path to agent blueprint YAML"),
    model: str = typer.Option("qwen3:8b", "--model", help="Ollama model name"),
    junit: Path = typer.Option(None, "--junit", help="Optional JUnit XML output path"),
    no_strip_think: bool = typer.Option(
        False, "--no-strip-think", help="Do not strip <think> tags from outputs"
    ),
    openapi_spec: str = typer.Option(
        None, "--openapi-spec", help="Optional OpenAPI spec URL or file to ingest before eval"
    ),
    openapi_tag: str = typer.Option(
        "api", "--openapi-tag", help="Tag/prefix for tools from --openapi-spec"
    ),
    openapi_base_url: str = typer.Option(
        None, "--openapi-base-url", help="Override base URL when ingesting --openapi-spec"
    ),
):
    """Run the blueprint's evaluation cases and report pass/fail."""
    bp = load_blueprint(blueprint)
    if openapi_spec:
        ingest_openapi(openapi_spec, tag=openapi_tag, base_url_override=openapi_base_url)
    # Positional call keeps typing simple across mypy versions
    summary = run_evaluations(bp, model, not no_strip_think, str(junit) if junit else None)
    console.print(Panel.fit("[bold]Evaluation Summary[/bold]"))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


@app.command()
def init(
    name: str = typer.Argument(..., help="Blueprint name (slug will be derived)"),
    out: Path = typer.Option(Path("blueprints"), "--out", help="Output directory"),
    tests: bool = typer.Option(False, "--tests", help="Also create a basic test file"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
):
    """Scaffold a new blueprint (and optional test)."""
    statuses = create_blueprint_scaffold(name=name, out_dir=out, with_tests=tests, force=force)
    console.print(Panel.fit("[bold]Scaffold[/bold]"))
    print(json.dumps([{str(p): s} for p, s in statuses], indent=2))


@app.command()
def openapi(
    spec: Path = typer.Argument(..., exists=True, help="Path to OpenAPI spec (yaml/json)"),
    tag: str = typer.Option("api", "--tag", help="Prefix/tag for generated tools"),
    base_url: str = typer.Option(None, "--base-url", help="Override base URL from spec"),
):
    """Ingest a simple OpenAPI spec and register tools at runtime."""
    registered = ingest_openapi(spec, tag=tag, base_url_override=base_url)
    console.print(Panel.fit("[bold]OpenAPI Tools Registered[/bold]"))
    print(json.dumps(registered, indent=2))


if __name__ == "__main__":
    app()
