"""Synthetic expected-action registry helpers.

The registry maps synthetic case names to synthetic expected-action fixture
paths. It validates paths only; it does not read expected-action JSONL bodies.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACTIVE_STATUS = "active"
PENDING_STATUS = "pending"
MISSING_STATUS = "missing"
FORBIDDEN_PATH_PARTS: frozenset[str] = frozenset(
    {"manual_outputs", "private_data", "real_data", "participant_data"}
)


class ExpectedActionRegistryError(ValueError):
    """Raised when the synthetic expected-action registry is unsafe or invalid."""


@dataclass(frozen=True)
class ExpectedActionRegistryEntry:
    case_name: str
    status: str
    expected_action_path: Path | None
    notes: str


@dataclass(frozen=True)
class ExpectedActionRegistryLookup:
    case_name: str
    status: str
    expected_action_path: Path | None
    notes: str


def load_expected_action_registry(
    registry_path: str | Path,
    *,
    base_dir: str | Path | None = None,
) -> dict[str, ExpectedActionRegistryEntry]:
    """Load and validate a synthetic expected-action registry.

    Paths are resolved against `base_dir` when provided, otherwise against the
    current working directory. Expected-action JSONL contents are not read.
    """

    path = Path(registry_path)
    root = Path(base_dir) if base_dir is not None else Path.cwd()
    with path.open("r", encoding="utf-8") as handle:
        try:
            registry = json.load(handle)
        except json.JSONDecodeError as error:
            raise ExpectedActionRegistryError(
                f"malformed registry JSON: {error.msg}"
            ) from error

    if not isinstance(registry, dict):
        raise ExpectedActionRegistryError("registry must be a JSON object")
    if registry.get("synthetic_only") is not True:
        raise ExpectedActionRegistryError("registry must set synthetic_only=true")

    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise ExpectedActionRegistryError("registry entries must be a list")

    loaded: dict[str, ExpectedActionRegistryEntry] = {}
    for index, entry in enumerate(entries, start=1):
        parsed = parse_registry_entry(entry, index=index, base_dir=root)
        if parsed.case_name in loaded:
            raise ExpectedActionRegistryError(
                f"duplicate case_name in registry: {parsed.case_name}"
            )
        loaded[parsed.case_name] = parsed
    return loaded


def lookup_expected_action_path(
    registry: dict[str, ExpectedActionRegistryEntry],
    case_name: str,
) -> ExpectedActionRegistryLookup:
    entry = registry.get(case_name)
    if entry is None:
        return ExpectedActionRegistryLookup(
            case_name=case_name,
            status=MISSING_STATUS,
            expected_action_path=None,
            notes="No synthetic expected action registry entry for this case.",
        )
    return ExpectedActionRegistryLookup(
        case_name=entry.case_name,
        status=entry.status,
        expected_action_path=entry.expected_action_path,
        notes=entry.notes,
    )


def parse_registry_entry(
    entry: Any,
    *,
    index: int,
    base_dir: Path,
) -> ExpectedActionRegistryEntry:
    if not isinstance(entry, dict):
        raise ExpectedActionRegistryError(f"entry {index}: expected JSON object")
    case_name = entry.get("case_name")
    status = entry.get("status")
    if not isinstance(case_name, str) or not case_name:
        raise ExpectedActionRegistryError(f"entry {index}: missing case_name")
    if status not in {ACTIVE_STATUS, PENDING_STATUS}:
        raise ExpectedActionRegistryError(
            f"entry {index}: status must be active or pending"
        )
    notes = str(entry.get("notes", ""))
    expected_action_path = entry.get("expected_action_path")

    if status == PENDING_STATUS:
        if expected_action_path is not None:
            raise ExpectedActionRegistryError(
                f"entry {index}: pending case must not define expected_action_path"
            )
        return ExpectedActionRegistryEntry(
            case_name=case_name,
            status=PENDING_STATUS,
            expected_action_path=None,
            notes=notes,
        )

    if not isinstance(expected_action_path, str) or not expected_action_path:
        raise ExpectedActionRegistryError(
            f"entry {index}: active case requires expected_action_path"
        )
    resolved = resolve_registry_path(expected_action_path, base_dir=base_dir)
    if not resolved.is_file():
        raise ExpectedActionRegistryError(
            f"entry {index}: expected_action_path does not exist: {expected_action_path}"
        )
    return ExpectedActionRegistryEntry(
        case_name=case_name,
        status=ACTIVE_STATUS,
        expected_action_path=resolved,
        notes=notes,
    )


def resolve_registry_path(path_value: str, *, base_dir: Path) -> Path:
    raw_path = Path(path_value)
    parts = set(raw_path.parts)
    forbidden = sorted(parts.intersection(FORBIDDEN_PATH_PARTS))
    if forbidden:
        joined = ", ".join(forbidden)
        raise ExpectedActionRegistryError(
            f"expected_action_path contains forbidden path component(s): {joined}"
        )
    if raw_path.is_absolute():
        resolved = raw_path
    else:
        resolved = base_dir / raw_path
    return resolved


def run_lookup_cli(registry_path: str | Path, case_name: str) -> str:
    registry = load_expected_action_registry(registry_path)
    lookup = lookup_expected_action_path(registry, case_name)
    path_text = "" if lookup.expected_action_path is None else str(lookup.expected_action_path)
    return f"{lookup.status}\t{path_text}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lookup synthetic expected-action fixture path by case name."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    lookup_parser = subparsers.add_parser(
        "lookup",
        help="Print expected action status and path without reading JSONL bodies.",
    )
    lookup_parser.add_argument("--registry", required=True, help="Registry JSON path")
    lookup_parser.add_argument("--case-name", required=True, help="Synthetic case name")
    args = parser.parse_args(argv)

    try:
        if args.command == "lookup":
            print(run_lookup_cli(args.registry, args.case_name))
            return 0
    except ExpectedActionRegistryError as error:
        print(f"expected_action_registry: error: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
