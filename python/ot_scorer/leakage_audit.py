"""Leakage audit for candidate feature extraction."""

from __future__ import annotations

from typing import Any


def audit_candidate_set(candidate_set: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if candidate_set.get("no_oracle_safe") is not True:
        flags.append("candidate_set_not_no_oracle_safe")
    if candidate_set.get("uses_observed_edit_text") is True:
        flags.append("candidate_set_uses_observed_edit_text")
    return flags


def audit_candidate(candidate: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if candidate.get("no_oracle_safe") is not True:
        flags.append("candidate_not_no_oracle_safe")
    if candidate.get("uses_observed_edit_text") is True:
        flags.append("candidate_uses_observed_edit_text")
    return flags
