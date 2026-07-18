#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
cd "$repo_root"

section() {
  echo
  echo "release_quality_check: $1"
}

run() {
  echo "command: $*"
  "$@"
}

run_in_dir() {
  run_dir=$1
  shift
  echo "command: cd $run_dir && $*"
  (cd "$run_dir" && "$@")
}

check_conflict_markers() {
  tmp_file="${TMPDIR:-/tmp}/release_quality_conflict_markers.$$"
  marker_left='<<<<'
  marker_left="${marker_left}<<<"
  marker_mid='===='
  marker_mid="${marker_mid}==="
  marker_right='>>>>'
  marker_right="${marker_right}>>>"
  marker_pattern="${marker_left}|${marker_mid}|${marker_right}"

  rm -f "$tmp_file"
  trap 'rm -f "$tmp_file"' EXIT HUP INT TERM

  if grep -R -nE \
    --exclude-dir=.git \
    --exclude-dir=target \
    --exclude-dir=node_modules \
    --exclude-dir=tmp \
    --exclude-dir=dist \
    --exclude-dir=dist-test \
    "$marker_pattern" . >"$tmp_file"; then
    echo "release_quality_check: fail" >&2
    echo "failure_kind=conflict_marker" >&2
    echo "conflict_marker_locations:" >&2
    cut -d: -f1,2 "$tmp_file" >&2
    echo "content_suppressed=true" >&2
    exit 1
  else
    grep_status=$?
  fi

  if [ "$grep_status" -ne 1 ]; then
    echo "release_quality_check: fail" >&2
    echo "failure_kind=conflict_marker_scan_error" >&2
    echo "content_suppressed=true" >&2
    exit "$grep_status"
  fi

  rm -f "$tmp_file"
  trap - EXIT HUP INT TERM
  echo "conflict_marker_grep: ok"
}

section "git diff whitespace"
run git diff --check

section "conflict marker grep"
check_conflict_markers

section "shell syntax"
run sh -n scripts/lib/summary_manifest_schema.sh
run sh -n scripts/run_synthetic_e2e_summary.sh
run sh -n scripts/check_synthetic_diagnostic_distribution.sh
run sh -n scripts/check_summary_manifest_schema_sync.sh

section "no-config synthetic summary"
run scripts/run_synthetic_e2e_summary.sh

section "summary manifest schema sync"
run scripts/check_summary_manifest_schema_sync.sh

section "synthetic diagnostic distribution"
run scripts/check_synthetic_diagnostic_distribution.sh

section "markdown link check"
echo "markdown_link_check: manual"
echo "reason=no_existing_project_markdown_link_check_command"
echo "content_suppressed=true"

section "python checks"
echo "command: PYTHONPATH=python python3 -m unittest discover -s python"
PYTHONPATH=python python3 -m unittest discover -s python
echo "command: PYTHONPATH=python python3 -m compileall python"
PYTHONPATH=python python3 -m compileall python

section "web logger unicode hash vector fixture validation"
run make check-web-logger-unicode-hash-vector-fixtures

section "web logger Rust UTF-16 offset conversion helper"
run make check-web-logger-rust-utf16-offset-conversion

section "learner-state audit fixtures"
run make check-learner-state-audit-fixtures

section "learner-state exporter CLI smoke"
run make check-learner-state-exporter-cli

section "learner-state estimator input validation"
run make check-learner-state-estimator-input

section "learner-state selective prediction calibration validation"
run make check-learner-state-selective-prediction

section "learner-state frozen policy validation"
run make check-learner-state-frozen-policy

section "learner-state frozen policy generation validation"
run make check-learner-state-frozen-policy-generation

section "learner-state frozen policy generation scaffold fixture validation"
run make check-learner-state-frozen-policy-generation-scaffold-fixtures

section "learner-state frozen policy generation scaffold runtime smoke"
run make check-learner-state-frozen-policy-generation-scaffold-runtime

section "learner-state frozen policy generation generator scaffold fixture validation"
run make check-learner-state-frozen-policy-generation-generator-scaffold-fixtures

section "learner-state frozen policy generation generator scaffold runtime smoke"
run make check-learner-state-frozen-policy-generation-generator-scaffold-runtime

section "learner-state frozen policy generation artifact writer fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-writer-fixtures

section "learner-state frozen policy generation artifact writer runtime smoke"
run make check-learner-state-frozen-policy-generation-artifact-writer-runtime

section "learner-state frozen policy generation artifact writer CLI integration fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures

section "learner-state frozen policy generation artifact writer CLI integration runtime fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures

section "learner-state frozen policy generation artifact writer CLI integration runtime smoke"
run make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime

section "learner-state frozen policy generation artifact writer CLI actual invocation fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures

section "learner-state frozen policy generation artifact writer CLI actual invocation runtime smoke"
run make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime

section "learner-state frozen policy generation artifact body generation integration fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures

section "learner-state frozen policy generation artifact body generation runtime integration plan-only bridge smoke"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration

section "learner-state frozen policy generation artifact body generation runtime integration safe-metadata v0.2 fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures

section "learner-state frozen policy generation artifact body generation runtime integration safe-metadata runtime smoke"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime

section "learner-state frozen policy generation artifact body generation runtime invocation fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures

section "learner-state frozen policy generation artifact body generation runtime invocation planned-only v0.3 smoke"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation

section "learner-state frozen policy generation actual-controlled artifact body generation runtime invocation fixture validation"
run make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures

section "learner-state frozen policy generation actual-controlled artifact body generation runtime invocation smoke"
run make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation

section "learner-state frozen policy generation actual-controlled v0.4 multi-case runtime smoke"
run make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke

section "learner-state frozen policy generation actual-controlled v0.4 invalid-case runtime fail-closed smoke"
run make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke

section "learner-state frozen policy generation actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke"
run make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke

section "learner-state frozen policy generation actual-controlled v0.4 artifact body payload audit without payload emission"
run make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission

section "learner-state frozen policy generation artifact body fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-body-fixtures

section "learner-state frozen policy generation artifact body generation CLI smoke"
run make check-learner-state-frozen-policy-generation-artifact-body-generation

section "learner-state frozen policy generation artifact body generation safe-metadata CLI smoke"
run make check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata

section "learner-state frozen policy generation artifact body to manifest handoff metadata-only no-writer-invocation"
run make check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation

section "learner-state frozen policy generation manifest writer handoff input validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation

section "learner-state frozen policy generation manifest writer dry-run no-body no-file-writing validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-dry-run-no-body-no-file-writing-validation

section "learner-state frozen policy generation artifact body file writing fixture validation"
run make check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures

section "learner-state frozen policy generation artifact body isolated write validation"
run make check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation

section "learner-state frozen policy generation manifest writer fixture validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-fixtures

section "learner-state frozen policy generation manifest writer runtime fixture validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures

section "learner-state frozen policy generation manifest writer runtime smoke"
run make check-learner-state-frozen-policy-generation-manifest-writer-runtime

section "learner-state frozen policy generation manifest writer file writing fixture validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures

section "learner-state frozen policy generation manifest writer isolated write validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation

section "learner-state frozen policy generation manifest writer production file writing fixture validation"
run make check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures

section "learner-state frozen policy generation manifest writer runtime file writing smoke"
run make check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing

section "config and scoring smoke checks"
run scripts/check_config_enabled_summary_smoke.sh
run scripts/check_config_enabled_e2e_smoke.sh
run scripts/check_no_config_scoring_fixture_lock.sh
run scripts/check_hand_weight_config_validation.sh
run scripts/check_explicit_config_ranking_diff.sh

section "rust checks"
run cargo fmt --all -- --check
run cargo test --workspace
run cargo clippy --workspace -- -D warnings

section "synthetic policy"
run scripts/check_synthetic_policy.sh

section "logger-web checks"
run_in_dir apps/logger-web npm run typecheck
run_in_dir apps/logger-web npm test
run_in_dir apps/logger-web npm run build

section "complete"
echo "release_quality_check: ok"
echo "content_suppressed=true"
