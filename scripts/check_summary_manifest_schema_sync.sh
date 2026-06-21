#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
. "$script_dir/lib/summary_manifest_schema.sh"

manifest_path=${1:-tmp/synthetic_e2e_summary/summary.manifest.json}
expected_manifest_path="tmp/synthetic_e2e_summary/summary.manifest.json"

usage() {
  echo "Usage: scripts/check_summary_manifest_schema_sync.sh [summary.manifest.json]" >&2
  echo "Checks safe/count-only no-config summary manifest schema constants sync." >&2
}

if [ "$#" -gt 1 ]; then
  usage
  exit 2
fi

case "$manifest_path" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "summary_manifest_schema_sync_check: fail" >&2
    echo "failure_kind=precondition" >&2
    echo "reason=private_or_real_path_not_supported" >&2
    echo "summary_manifest=$manifest_path" >&2
    echo "content_suppressed=true" >&2
    exit 2
    ;;
  *synthetic_e2e_config_summary* )
    echo "summary_manifest_schema_sync_check: fail" >&2
    echo "failure_kind=precondition" >&2
    echo "reason=config_enabled_summary_not_supported" >&2
    echo "summary_manifest=$manifest_path" >&2
    echo "expected_summary_manifest=$expected_manifest_path" >&2
    echo "content_suppressed=true" >&2
    exit 2
    ;;
esac

if [ ! -f "$manifest_path" ]; then
  echo "summary_manifest_schema_sync_check: fail" >&2
  echo "failure_kind=precondition" >&2
  echo "reason=missing_summary_manifest" >&2
  echo "summary_manifest=$manifest_path" >&2
  echo "next_step=scripts/run_synthetic_e2e_summary.sh" >&2
  echo "content_suppressed=true" >&2
  exit 2
fi

if [ ! -s "$manifest_path" ]; then
  echo "summary_manifest_schema_sync_check: fail" >&2
  echo "failure_kind=precondition" >&2
  echo "reason=empty_summary_manifest" >&2
  echo "summary_manifest=$manifest_path" >&2
  echo "next_step=scripts/run_synthetic_e2e_summary.sh" >&2
  echo "content_suppressed=true" >&2
  exit 2
fi

SUMMARY_MANIFEST_SCHEMA_VERSION="$SUMMARY_MANIFEST_SCHEMA_VERSION" \
SUMMARY_MANIFEST_SUMMARY_SCHEMA_VERSION="$SUMMARY_MANIFEST_SUMMARY_SCHEMA_VERSION" \
SUMMARY_MANIFEST_GENERATOR_SCRIPT="$SUMMARY_MANIFEST_GENERATOR_SCRIPT" \
SUMMARY_MANIFEST_CONTENT_SUPPRESSED="$SUMMARY_MANIFEST_CONTENT_SUPPRESSED" \
SUMMARY_MANIFEST_NO_CONFIG_SUMMARY="$SUMMARY_MANIFEST_NO_CONFIG_SUMMARY" \
SUMMARY_MANIFEST_ALLOWED_KEYS="$SUMMARY_MANIFEST_ALLOWED_KEYS" \
SUMMARY_MANIFEST_FORBIDDEN_KEYS="$SUMMARY_MANIFEST_FORBIDDEN_KEYS" \
python3 - "$manifest_path" "$expected_manifest_path" <<'PY'
import json
import os
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
expected_manifest_path = sys.argv[2]

expected_manifest_schema_version = os.environ["SUMMARY_MANIFEST_SCHEMA_VERSION"]
expected_summary_schema_version = os.environ["SUMMARY_MANIFEST_SUMMARY_SCHEMA_VERSION"]
expected_generator_script = os.environ["SUMMARY_MANIFEST_GENERATOR_SCRIPT"]
expected_content_suppressed = os.environ["SUMMARY_MANIFEST_CONTENT_SUPPRESSED"].lower() == "true"
expected_no_config_summary = os.environ["SUMMARY_MANIFEST_NO_CONFIG_SUMMARY"].lower() == "true"
allowed_keys = {
    key.strip()
    for key in os.environ["SUMMARY_MANIFEST_ALLOWED_KEYS"].splitlines()
    if key.strip()
}
forbidden_keys = {
    key.strip()
    for key in os.environ["SUMMARY_MANIFEST_FORBIDDEN_KEYS"].splitlines()
    if key.strip()
}


def fail(reason, **details):
    print("summary_manifest_schema_sync_check: fail", file=sys.stderr)
    print("failure_kind=schema_sync", file=sys.stderr)
    print(f"reason={reason}", file=sys.stderr)
    for key, value in details.items():
        print(f"{key}={value}", file=sys.stderr)
    print("content_suppressed=true", file=sys.stderr)
    sys.exit(2)


try:
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
except json.JSONDecodeError:
    fail("malformed_summary_manifest_json", summary_manifest=manifest_path)

if not isinstance(manifest, dict):
    fail("invalid_summary_manifest_shape", summary_manifest=manifest_path)

actual_keys = set(manifest)
forbidden_present = sorted(actual_keys & forbidden_keys)
if forbidden_present:
    fail(
        "forbidden_summary_manifest_key",
        summary_manifest=manifest_path,
        forbidden_keys_count=len(forbidden_present),
        first_forbidden_key=forbidden_present[0],
    )

unknown_keys = sorted(actual_keys - allowed_keys)
if unknown_keys:
    fail(
        "unknown_summary_manifest_key",
        summary_manifest=manifest_path,
        unknown_keys_count=len(unknown_keys),
        first_unknown_key=unknown_keys[0],
    )

missing_keys = sorted(allowed_keys - actual_keys)
if missing_keys:
    fail(
        "missing_summary_manifest_key",
        summary_manifest=manifest_path,
        missing_keys_count=len(missing_keys),
        first_missing_key=missing_keys[0],
    )

if manifest.get("manifest_schema_version") != expected_manifest_schema_version:
    fail(
        "manifest_schema_version_mismatch",
        summary_manifest=manifest_path,
        expected_manifest_schema_version=expected_manifest_schema_version,
    )

if manifest.get("summary_schema_version") != expected_summary_schema_version:
    fail(
        "summary_schema_version_mismatch",
        summary_manifest=manifest_path,
        expected_summary_schema_version=expected_summary_schema_version,
    )

if manifest.get("generator_script") != expected_generator_script:
    fail(
        "generator_script_mismatch",
        summary_manifest=manifest_path,
        expected_generator_script=expected_generator_script,
    )

if manifest.get("content_suppressed") is not expected_content_suppressed:
    fail("content_suppressed_mismatch", summary_manifest=manifest_path)

if manifest.get("no_config_summary") is not expected_no_config_summary:
    fail("no_config_summary_mismatch", summary_manifest=manifest_path)

if manifest.get("summary_path") != "tmp/synthetic_e2e_summary/summary.csv":
    fail(
        "summary_path_mismatch",
        summary_manifest=manifest_path,
        expected_summary_path="tmp/synthetic_e2e_summary/summary.csv",
    )

case_count = manifest.get("case_count")
if not isinstance(case_count, int) or isinstance(case_count, bool) or case_count <= 0:
    fail("invalid_case_count", summary_manifest=manifest_path)

diagnostic_summary_count = manifest.get("diagnostic_summary_count")
if (
    not isinstance(diagnostic_summary_count, int)
    or isinstance(diagnostic_summary_count, bool)
    or diagnostic_summary_count < 0
):
    fail("invalid_diagnostic_summary_count", summary_manifest=manifest_path)

print("summary_manifest_schema_sync_check: ok")
print(f"summary_manifest: {manifest_path}")
print(f"expected_summary_manifest: {expected_manifest_path}")
print(f"manifest_schema_version: {expected_manifest_schema_version}")
print(f"allowed_keys_count: {len(allowed_keys)}")
print(f"forbidden_keys_count: {len(forbidden_keys)}")
print(f"case_count: {case_count}")
print(f"diagnostic_summary_count: {diagnostic_summary_count}")
print("performance_metrics_included: false")
print("content_suppressed: true")
PY
