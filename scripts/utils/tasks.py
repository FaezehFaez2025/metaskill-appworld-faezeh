"""One task of a run: its starting playbook, Generator replies and result, and the task order."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from utils.llm_calls import calls_of_kind, output_text, playbook_in_prompt
from utils.playbook import Bullet, parse_bullets

TASK_ID_RE = re.compile(r'"([0-9a-fA-F]+_\d+)"')


@dataclass
class TaskRecord:
    task_id: str
    finished: bool
    passed: bool | None
    passed_tests: int | None
    failed_tests: int | None
    total_tests: int | None
    generator_steps: int
    has_curator_call: bool
    starting_bullets: dict[str, Bullet]  # bullet id -> bullet, of the starting playbook
    generator_replies: str  # all Generator replies of the task, joined into one text


def task_family_and_instance(task_id: str) -> tuple[str, int]:
    """Split a task id like d0b1f43_2 into the family (d0b1f43) and the instance number (2)."""
    family, _, instance = task_id.rpartition("_")
    return family, int(instance) if instance.isdigit() else 0


def task_order(config_path: Path) -> list[str]:
    """The task ids in the config's task_ids list, in the order the tasks run."""
    match = re.search(r'"task_ids"\s*:\s*\[(.*?)\]', config_path.read_text(), re.S)
    if not match:
        raise SystemExit(f"No task_ids list in {config_path}")
    return TASK_ID_RE.findall(match.group(1))


def parse_report(path: Path) -> tuple[int | None, int | None, int | None]:
    """Passed, failed and total evaluation assertions from evaluation/report.md."""
    text = path.read_text()

    def grab(label: str) -> int | None:
        match = re.search(rf"{label}\s*:\s*(\d+)", text)
        return int(match.group(1)) if match else None

    return (
        grab("Num Passed Tests"),
        grab("Num Failed Tests"),
        grab("Num Total  Tests"),
    )


def load_task(task_dir: Path) -> TaskRecord | None:
    generator_calls = calls_of_kind(task_dir, "generator")
    if not generator_calls:
        return None

    report_path = task_dir / "evaluation" / "report.md"
    passed_tests = failed_tests = total_tests = None
    finished = report_path.is_file()
    passed = None
    if finished:
        passed_tests, failed_tests, total_tests = parse_report(report_path)
        passed = (
            failed_tests == 0
            and total_tests is not None
            and total_tests > 0
            and passed_tests == total_tests
        )

    return TaskRecord(
        task_id=task_dir.name,
        finished=finished,
        passed=passed,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        total_tests=total_tests,
        generator_steps=len(generator_calls),
        has_curator_call=bool(calls_of_kind(task_dir, "curator")),
        starting_bullets=parse_bullets(playbook_in_prompt(generator_calls[0])),
        generator_replies="\n".join(output_text(call) for call in generator_calls),
    )

