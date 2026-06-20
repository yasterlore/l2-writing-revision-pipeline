"""Test-only helpers for scanning safe CLI output.

These helpers are intentionally limited to stdout/stderr-style text. They
normalize environment-dependent absolute paths before forbidden-fragment scans,
but they should not be used to blanket-normalize generated JSONL or report
bodies.
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from typing import Iterable

_PATH_PREFIX_BOUNDARY = r"(?<![A-Za-z0-9._~\\/:-])"


def normalize_environment_paths_for_scan(
    text: str,
    project_root: str | Path | None = None,
    extra_temp_roots: Iterable[str | Path] = (),
) -> str:
    """Replace environment-dependent path prefixes in CLI output.

    Temporary paths are collapsed as whole path tokens because random temporary
    directory segments can contain forbidden-looking substrings. Project-root
    paths keep their relative suffix so project-controlled output names remain
    visible to the scan.
    """

    normalized = text
    root = Path(project_root or Path.cwd()).resolve()

    temp_roots = [
        tempfile.gettempdir(),
        os.environ.get("TMPDIR"),
        os.environ.get("TEMP"),
        os.environ.get("TMP"),
        "/tmp",
        "/private/tmp",
        *extra_temp_roots,
    ]
    normalized = _replace_paths_under_roots(normalized, temp_roots, "<TMP_PATH>")

    normalized = _replace_root_prefixes(normalized, [root], "<PROJECT_ROOT>")

    workspace_roots = [
        os.environ.get("GITHUB_WORKSPACE"),
        os.environ.get("CI_PROJECT_DIR"),
        os.environ.get("BUILDKITE_BUILD_CHECKOUT_PATH"),
        os.environ.get("WORKSPACE"),
    ]
    normalized = _replace_root_prefixes(normalized, workspace_roots, "<WORKSPACE>")

    normalized = _replace_root_prefixes(normalized, [Path.home()], "<HOME>")
    return normalized


def assert_no_forbidden_fragments(
    test_case: unittest.TestCase,
    text: str,
    forbidden_fragments: Iterable[str],
    *,
    normalize_paths: bool = False,
    project_root: str | Path | None = None,
) -> None:
    scan_text = (
        normalize_environment_paths_for_scan(text, project_root=project_root)
        if normalize_paths
        else text
    )
    for fragment in forbidden_fragments:
        test_case.assertNotIn(fragment, scan_text)


def _replace_paths_under_roots(
    text: str,
    roots: Iterable[str | Path | None],
    placeholder: str,
) -> str:
    normalized = text
    for root in _normalized_roots(roots):
        pattern = re.compile(
            _PATH_PREFIX_BOUNDARY + re.escape(root) + r"(?:[\\/][^\s\"'<>]*)?"
        )
        normalized = pattern.sub(placeholder, normalized)
    return normalized


def _replace_root_prefixes(
    text: str,
    roots: Iterable[str | Path | None],
    placeholder: str,
) -> str:
    normalized = text
    for root in _normalized_roots(roots):
        pattern = re.compile(_PATH_PREFIX_BOUNDARY + re.escape(root))
        normalized = pattern.sub(placeholder, normalized)
    return normalized


def _normalized_roots(roots: Iterable[str | Path | None]) -> list[str]:
    normalized: set[str] = set()
    for root in roots:
        if root is None:
            continue
        root_text = str(root).rstrip("/\\")
        if not root_text or root_text == ".":
            continue
        expanded = str(Path(root_text).expanduser()).rstrip("/\\")
        if expanded and expanded not in {"/", "\\"}:
            normalized.add(expanded)
        try:
            resolved = str(Path(root_text).expanduser().resolve()).rstrip("/\\")
        except OSError:
            resolved = expanded
        if resolved and resolved not in {"/", "\\"}:
            normalized.add(resolved)
    return sorted(normalized, key=len, reverse=True)
