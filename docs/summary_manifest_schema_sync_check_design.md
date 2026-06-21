# Summary Manifest Schema Sync Check Design

This document is design documentation only. It does not change shell scripts,
test code, summary generation, scoring logic, scorer weights, formulas, or
tie-break policy.

It is not a performance evaluation. It does not approve real-data processing,
private validation, or any tuning workflow.

## 1. Purpose

The purpose of this design is to define a sync check for the no-config summary
manifest schema constants.

The sync check should reduce drift between:

- shared schema constants
- the summary generator
- the diagnostic distribution checker
- generated manifest metadata
- schema-related docs and release checklist guidance

The check must preserve output safety and no-oracle boundaries. It should report
safe metadata status only and must not print generated bodies.

## 2. Current State

Current components:

- shared constants file:
  `scripts/lib/summary_manifest_schema.sh`
- generator:
  `scripts/run_synthetic_e2e_summary.sh`
- checker:
  `scripts/check_synthetic_diagnostic_distribution.sh`
- manifest output:
  `tmp/synthetic_e2e_summary/summary.manifest.json`
- docs:
  schema-related docs and the public release checklist

Step 120 centralized the current manifest schema constants in the shared shell
file. Step 122 implemented `scripts/check_summary_manifest_schema_sync.sh` as a
small shell smoke script that verifies generated manifest metadata against those
shared constants.

## 3. Why A Sync Check Is Needed

A sync check is useful because:

- changing the constants file can still leave generator, checker, docs, or tests
  out of date
- generated manifest output should match the expected shared constants
- the actual manifest key set should exactly match the allowed-key list
- forbidden-key validation should remain active after refactors
- release readiness is easier to review when there is a small command dedicated
  to schema synchronization

The sync check should be a safety/reliability check, not an evaluation report.

## 4. Candidate Sync Check Shapes

### Option A: Shell Smoke Script

Add a small shell smoke script such as
`scripts/check_summary_manifest_schema_sync.sh`.

This fits the current shell-first workflow and can source
`scripts/lib/summary_manifest_schema.sh` directly. It is easy to call from
release checklists, but JSON parsing in shell should stay minimal or delegate to
Python.

### Option B: Python Unittest

Add a Python unittest under `python/test_support/tests/`.

This is test-runner friendly and has safer JSON parsing, but it needs a clean
way to read shell constants without duplicating them.

### Option C: Python Helper That Sources Shell Constants

Use a Python helper or unittest that invokes a small shell subprocess to source
the constants and emit safe key/value metadata for comparison.

This avoids duplicating constants in Python while keeping JSON parsing in
Python. It is slightly more complex than a shell smoke script.

### Option D: Docs-Only Checklist

Document a manual checklist only.

This is useful context, but it cannot reliably catch drift during automated
checks.

### Option E: Release Checklist Command Bundle

Add the sync check to an existing release-quality command bundle later.

This is useful after the check exists, but it does not define the check itself.

## 5. Recommended Approach

The recommended initial implementation is either:

- a small shell smoke script that sources the shared constants and uses Python
  only for safe JSON parsing, or
- a Python unittest that obtains shared constants through a subprocess rather
  than duplicating them

For the current project shape, a small shell smoke script is the most practical
first step because the existing summary and diagnostic checks are shell-first.

Recommended behavior:

- source `scripts/lib/summary_manifest_schema.sh`
- generate or read the no-config manifest after
  `scripts/run_synthetic_e2e_summary.sh`
- compare manifest metadata with shared constants
- compare actual manifest keys with `SUMMARY_MANIFEST_ALLOWED_KEYS`
- verify forbidden keys are absent
- print only safe status, path, counts, and reason codes
- do not print the marker JSON body
- do not report performance metrics

## 6. Items The Sync Check Should Verify

The future sync check should verify:

- `manifest_schema_version` matches `SUMMARY_MANIFEST_SCHEMA_VERSION`
- `summary_schema_version` matches `SUMMARY_MANIFEST_SUMMARY_SCHEMA_VERSION`
- `generator_script` matches `SUMMARY_MANIFEST_GENERATOR_SCRIPT`
- actual manifest keys exactly equal `SUMMARY_MANIFEST_ALLOWED_KEYS`
- `SUMMARY_MANIFEST_FORBIDDEN_KEYS` are not present
- `content_suppressed` equals the expected shared constant
- `no_config_summary` equals the expected shared constant
- `case_count` is positive
- `diagnostic_summary_count` is nonnegative
- no raw body-like fields are present

The check should remain no-config only and must not read config-enabled summary
paths as valid inputs.

## 7. Information The Sync Check Must Not Output

The sync check must not print:

- marker JSON body
- summary CSV body
- diagnostic summary body
- JSONL body
- candidate score rows
- raw text
- config body
- expected action details
- performance metrics
- real participant data

Safe status, safe paths, counts, field names, and reason codes are acceptable
when they do not reveal generated bodies.

## 8. Implementation Status And Future Options

Step 122 implements the initial shell smoke script:

- `scripts/check_summary_manifest_schema_sync.sh`
- sources `scripts/lib/summary_manifest_schema.sh`
- parses the generated no-config manifest with Python
- compares keys, versions, expected values, and forbidden-key absence
- prints only safe status, path, key counts, and case counts

Future options:

- add a Python unittest under `python/test_support/tests/`
- use both only if each covers a distinct need
- let the public release checklist call the script once it exists
- add the check to CI later if the project introduces CI

Avoid duplicating the allowed-key list in multiple implementation languages
unless there is a test that proves the duplicates match.

## 9. Failure Policy

The future sync check should fail when:

- schema version mismatches
- summary schema version mismatches
- generator script mismatches
- an unknown key appears
- a required key is missing
- a forbidden key appears
- a body-like field appears
- an output body leak is detected

Failures should be explicit and safe. The check should not silently pass when a
precondition is missing or when the manifest is stale.

## 10. Migration Policy

Future manifest field additions should require:

- shared constants update
- generator update
- checker update
- sync check update
- docs update
- release checklist update when relevant
- schema version bump if the schema changes materially

Unknown keys should remain fail-closed unless they are intentionally added to
the shared constants and documented.

## 11. Output Safety, Privacy, And No-Oracle Policy

The sync check is reliability infrastructure.

It is:

- not a performance metric
- not a tuning signal
- not expected-action feedback
- not real-data evidence
- not private validation

It must preserve:

- no marker body output
- no summary body output
- no JSONL body output
- no diagnostic body output
- no score rows
- no expected action feedback
- no real participant data

## 12. Beginner Notes

A sync check is a small verification that two or more parts of the system agree.
Here, it would check that the shared schema constants, the generated manifest,
and the checker all describe the same safe metadata shape.

This matters because the generator writes the manifest, the checker validates
it, and docs explain it. If one of those gets out of sync, a future change may
look safe in one place but fail or drift in another.

The check should not print the manifest body because the manifest is still a
generated file. The public output only needs safe status and count-only metadata.

Unknown keys should fail because an unexpected field can hide schema drift or an
unsafe output field. This is not performance evaluation; it only checks schema
alignment.

## 13. Related Documents

- [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md)
- [Summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md)
- [Summary manifest schema hardening design](summary_manifest_schema_hardening_design.md)
- [Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md)
- [Public release checklist](public_release_checklist.md)
