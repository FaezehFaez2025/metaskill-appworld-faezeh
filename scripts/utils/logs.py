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
