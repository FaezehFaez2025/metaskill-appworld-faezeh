"""Reading the logs of one task: lm_calls.jsonl (Generator, Reflector, Curator) and report.md."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator


def read_calls(task_dir: Path) -> Iterator[dict]:
    """Read the LLM calls of one task, one call at a time.

    The file tasks/<id>/logs/lm_calls.jsonl has one line per call to the LLM. The Generator,
    Reflector and Curator all use the LLM, so the file holds all three. Each call is a dict with the keys id, input (the prompt) and output (the LLM's answer).
    call_kind(call) returns "generator", "reflector" or "curator" for a call, so you can tell
    which module made it.
    """
    for line in (task_dir / "logs" / "lm_calls.jsonl").read_text().splitlines():
        if line.strip():
            yield json.loads(line)


def call_kind(call: dict) -> str:
    """generator, reflector, curator or other, from how the first prompt message starts."""
    messages = (call.get("input") or {}).get("messages") or []
    if not messages:
        return "other"
    content = messages[0].get("content") or ""
    if content.startswith("I am your supervisor"):
        return "generator"
    if content.startswith("You are an expert"):
        return "reflector"
    if content.startswith("You are a master curator"):
        return "curator"
    return "other"


def output_text(call: dict) -> str:
    """The text the LLM answered in one call, or "" if there is none."""
    output = call.get("output") or {}
    try:
        # Usual place of the answer in these logs.
        content = output["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        # Fallback for logs saved in a different shape.
        content = output.get("content")
    return content or ""
