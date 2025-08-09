from __future__ import annotations

from typing import Dict


def add(x: int, y: int) -> int:
    return int(x) + int(y)


def multiply(x: int, y: int) -> int:
    return int(x) * int(y)


def get_tools() -> Dict[str, object]:
    return {
        "add": add,
        "multiply": multiply,
    }
