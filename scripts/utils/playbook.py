"""Read the bullets of a playbook and find the API and argument names each bullet mentions."""

from __future__ import annotations

import re
from dataclasses import dataclass

from utils.config import MIN_NAME_LENGTH, QUOTE_LENGTH


@dataclass
class Bullet:
    bullet_id: str
    content: str

    @property
    def quote(self) -> str:
        collapsed = re.sub(r"\s+", " ", self.content).strip()
        return collapsed[:QUOTE_LENGTH]
