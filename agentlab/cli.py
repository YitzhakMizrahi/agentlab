## agentlab/cli.py

from __future__ import annotations
import json
from pathlib import Path
import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

from .config_loader import load_blueprint
from .runner import run_agent
from .evaluator import run_evaluations

app = typer.Typer(add_completion=False, help="AgentLab CLI")
console = Console()


@app.command()
def run(
    blueprint: Path = typer.Argument(..., exists=True, help="Path to agent blueprint YAML"),
    input_text: str = typer.Option(None, "--input", "-i", help="Optional single input payload"),
    model: str = typer.Option("qwen3:8b", "--model", help="Ollama model name"),
    stream: bool = typer.Option(False, "--stream", help="Stream output from LLM if supported"),
):
    """Run a single agent from a blueprint."""
    bp = load_blueprint(blueprint)
    result = run_agent(bp, input_text=input_text, model_name=model, stream=stream)
    console.print(Panel.fit("[bold]Result[/bold]", expand=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def eval(
    blueprint: Path = typer.Argument(..., exists=True, help="Path to agent blueprint YAML"),
    model: str = typer.Option("qwen3:8b", "--model", help="Ollama model name"),
):
    """Run the blueprint's evaluation cases and report pass/fail."""
    bp = load_blueprint(blueprint)
    summary = run_evaluations(bp, model_name=model)
    console.print(Panel.fit("[bold]Evaluation Summary[/bold]", expand=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
