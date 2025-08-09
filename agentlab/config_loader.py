## agentlab/config_loader.py

from __future__ import annotations
from pathlib import Path
from typing import List, Literal, Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field, ValidationError


class ToolRef(BaseModel):
    name: str


class PlanStep(BaseModel):
    kind: Literal["tool_use", "generate", "note"] = Field(alias="step")
    name: Optional[str] = None  # tool name for tool_use or generator name for generate
    with: Optional[Dict[str, Any]] = None  # additional args

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class EvalCase(BaseModel):
    input: str
    expected: str


class MemorySpec(BaseModel):
    strategy: Literal["none", "short_term", "episode"] = "short_term"


class Blueprint(BaseModel):
    name: str
    description: str = ""
    system_prompt: str = Field(
        default=(
            "You are a helpful, precise agent. Be concise, cite assumptions, and use the provided tools context when available."
        )
    )
    tools: List[ToolRef] = []
    memory: MemorySpec = MemorySpec()
    plan: List[PlanStep] = []
    evaluation: List[EvalCase] = []


def load_blueprint(path: Path) -> Blueprint:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    try:
        return Blueprint.model_validate(data)
    except ValidationError as e:
        raise SystemExit(f"Invalid blueprint: {e}")