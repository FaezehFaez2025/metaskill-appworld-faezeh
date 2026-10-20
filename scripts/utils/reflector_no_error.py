"""Decide whether a Reflector text says "no error": by keyword matching or by asking an LLM."""

from __future__ import annotations

import re

NO_ERROR_RE = re.compile(
    r"^\W*none\b"  # the text starts with "None"
    r"|\bno\b[^.]{0,40}\b(errors?|root causes?|mistakes?|flaws?|failures?)\b"
    r"|\bdid not (make|have)\b[^.]{0,20}\berrors?\b"
    r"|\b(flawless(ly)?|fully correct|executed (all steps )?correctly)\b",
    re.I,
)

PROMPT = """Below is an analysis of why an agent failed a task. Does the analysis conclude that \
the agent made no real error? Remarks about style or efficiency do not count as errors.

Answer with one word: NO_ERROR or ERROR.

Analysis:
\"\"\"
{text}
\"\"\"
"""


def says_no_error(text: str, model: str | None = None) -> bool:
    """True when the text says the agent made no error.

    With no `model`, a rule decides. With a `model` (an LLM name such as "openai/gpt-4.1"),
    that LLM decides. Its API key is read from the environment.
    """
    if model is None:
        return bool(NO_ERROR_RE.search(text))

    import litellm  # only needed for the LLM option

    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        temperature=0,
    )
    answer = response.choices[0].message.content.strip().upper()
    if "ERROR" not in answer:
        raise ValueError(f"Unexpected answer from {model}: {answer!r}")
    return answer.startswith("NO_ERROR")
