"""Read the bullets of a playbook and find the API and argument names each bullet mentions."""

from __future__ import annotations

import re
from dataclasses import dataclass

from utils.config import MIN_NAME_LENGTH, QUOTE_LENGTH

BULLET_RE = re.compile(r"^\[([A-Za-z]+-\d+)\]\s*(.*)$")


@dataclass
class Bullet:
    bullet_id: str
    content: str

    @property
    def quote(self) -> str:
        collapsed = re.sub(r"\s+", " ", self.content).strip()
        return collapsed[:QUOTE_LENGTH]


def parse_bullets(playbook_text: str) -> dict[str, Bullet]:
    bullets: dict[str, Bullet] = {}
    for line in playbook_text.splitlines():
        match = BULLET_RE.match(line.strip())
        if match:
            bullets[match.group(1)] = Bullet(match.group(1), match.group(2).strip())
    return bullets
