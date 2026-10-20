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


def parse_json(text: str) -> dict:
    """Convert the LLM's answer text into a dict. Return {} if it cannot be read as JSON.

    The answer is meant to be JSON, but the LLM may wrap it in a code fence or add a sentence
    before or after it. Both are handled.
    """
    # Remove spaces and a code fence (```json ... ```) around the JSON.
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Retry with only the part from the first { to the last }.
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


def curator_adds(task_dir: Path) -> list[str] | None:
    """Extract the text of the new bullets that the Curator proposed to add after this task.

    The Curator's answer is a list of operations, and each ADD operation is one new bullet.
    Return either:
      - a list with the text of each ADD operation, which is [] when the Curator ran but
        proposed no ADD, or
      - None, when this task has no Curator call in its log.
    """
    for call in read_calls(task_dir):
        if call_kind(call) == "curator":
            operations = parse_json(output_text(call)).get("operations") or []
            return [
                op.get("content", "")
                for op in operations
                if isinstance(op, dict) and op.get("type") == "ADD"
            ]
    return None


def reflector_text(task_dir: Path) -> str | None:
    """The Reflector's error_identification text for this task, or None when it did not run."""
    for call in read_calls(task_dir):
        if call_kind(call) == "reflector":
            return str(parse_json(output_text(call)).get("error_identification") or "")
    return None
