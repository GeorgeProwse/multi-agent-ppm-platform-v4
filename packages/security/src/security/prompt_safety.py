from __future__ import annotations

import re
from dataclasses import dataclass


INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ignore (all|any|previous) instructions", re.IGNORECASE), "ignore_previous"),
    (re.compile(r"system prompt", re.IGNORECASE), "system_prompt"),
    (re.compile(r"reveal (the )?system prompt", re.IGNORECASE), "reveal_system_prompt"),
    (re.compile(r"reveal hidden", re.IGNORECASE), "reveal_hidden"),
    (re.compile(r"exfiltrate secrets?", re.IGNORECASE), "exfiltrate_secrets"),
    (re.compile(r"print env", re.IGNORECASE), "print_env"),
    (re.compile(r"bypass safety", re.IGNORECASE), "bypass_safety"),
    (re.compile(r"disable safety", re.IGNORECASE), "disable_safety"),
    (re.compile(r"jailbreak", re.IGNORECASE), "jailbreak"),
]


@dataclass(frozen=True)
class PromptSafetyResult:
    decision: str
    reasons: list[str]
    sanitized_text: str


def _sanitize(text: str, matches: list[re.Match[str]]) -> str:
    if not matches:
        return text
    sanitized = text
    for match in matches:
        segment = match.group(0)
        sanitized = sanitized.replace(segment, "[REMOVED_UNSAFE_SEGMENT]")
    return sanitized


def evaluate_prompt(text: str) -> PromptSafetyResult:
    reasons: list[str] = []
    matches: list[re.Match[str]] = []

    for pattern, label in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            reasons.append(label)
            matches.append(match)

    sanitized = _sanitize(text, matches)
    decision = "allow"
    if reasons:
        decision = "allow_with_warning"
    if len(reasons) >= 2:
        decision = "deny"

    return PromptSafetyResult(decision=decision, reasons=reasons, sanitized_text=sanitized)
