"""One task of a run: its starting playbook, Generator replies and result, and the task order."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from utils.llm_calls import calls_of_kind, output_text, playbook_in_prompt, prompt_text
from utils.playbook import Bullet, parse_bullets


def task_family_and_instance(task_id: str) -> tuple[str, int]:
    """Split a task id like d0b1f43_2 into the family (d0b1f43) and the instance number (2)."""
    family, _, instance = task_id.rpartition("_")
    return family, int(instance) if instance.isdigit() else 0
