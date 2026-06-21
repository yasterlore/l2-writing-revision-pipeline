# Summary Manifest Schema Centralization Design

This document records the design and initial implementation for centralizing
safe/count-only schema constants for the no-config synthetic E2E summary
manifest.

It is not a performance evaluation. It does not approve real-data processing,
private validation, or any tuning workflow.

## 1. Purpose

The purpose of this design is to define where summary manifest schema constants
should live and how the generator, checker, docs, and tests should stay aligned.

The goals are:

- reduce synchronization drift between the generator, checker, docs, and tests
- keep `manifest_schema_version` and allowed keys aligned
- make future manifest field additions reviewable
- preserve output safety, privacy, and no-oracle boundaries
- keep the manifest as reliability metadata, not a report body

## 1.1 Implementation Status

Step 120 implemented the initial shared shell constants file:

- `scripts/lib/summary_manifest_schema.sh` defines the current manifest schema
  version, summary schema version, expected generator script, expected safe
  boolean values, allowed keys, and forbidden keys
- `scripts/run_synthetic_e2e_summary.sh` uses the shared version and schema
  constants when writing the no-config manifest
- `scripts/check_synthetic_diagnostic_distribution.sh` uses the shared version,
  allowed keys, forbidden keys, and expected generator script when validating
  the manifest
- manifest fields and `manifest_schema_version` remain unchanged

Summary hash, per-case diagnostic consistency hardening, and wrapper scripts
remain future work.

For the follow-up design on verifying that shared constants, generated
manifests, and checker expectations stay aligned, see
[Summary manifest schema sync check design](summary_manifest_schema_sync_check_design.md).
Step 122 implements the initial shell smoke sync check as
`scripts/check_summary_manifest_schema_sync.sh`.

## 2. Current State

Current no-config summary manifest state:

- `scripts/run_synthetic_e2e_summary.sh` generates
  `tmp/synthetic_e2e_summary/summary.manifest.json`
- `scripts/check_synthetic_diagnostic_distribution.sh` validates that manifest
- `manifest_schema_version` is `1.0`
- manifest schema constants are centralized in
  `scripts/lib/summary_manifest_schema.sh`
- docs list the current fields and explain the safe/count-only intent
- config-enabled summary output is separate and is not connected to this
  manifest

The current manifest fields are:

- `manifest_schema_version`
- `run_id`
- `completed_at`
- `summary_path`
- `case_count`
- `diagnostic_summary_count`
- `content_suppressed`
- `no_config_summary`
- `generator_script`
- `summary_schema_version`

## 3. Why Centralization Is Needed

Centralization is useful because future manifest changes touch several places:

- generator output fields
- checker validation rules
- docs field lists
- expected-failure tests
- release checklist guidance

If the allowed-key list is copied in multiple places, a future field could be
added to the generator but not the checker, or documented without being tested.
That kind of drift makes fail-closed safety harder to reason about.

A centralized schema can:

- reduce duplicate allowed-key definitions
- manage schema version and field list together
- make migration steps explicit
- reduce mismatch between shell scripts and docs
- make release-readiness checks easier to audit

## 4. Design Options

### Option A: Keep Constants In Shell Scripts

Leave `manifest_schema_version`, allowed keys, and forbidden keys directly in
the current scripts.

This is simple and has no additional files, but it keeps the drift risk. It is
acceptable for a tiny schema, but weaker once future fields are added.

### Option B: Shared Shell Constants File

Create a shared shell file such as
`scripts/lib/summary_manifest_schema.sh`.

This keeps the shell-first workflow simple. The generator and checker can source
the same version and key lists. Step 120 implements this initial option.

### Option C: JSON Schema File

Create a public schema file such as
`docs/schemas/summary_manifest_schema_v1.json`.

This is useful for documentation and review, but using a docs file as the
runtime source of truth should be considered carefully. It may be better as a
published reference generated from or aligned with implementation constants.

### Option D: Python Schema Validator Or Helper

Move manifest validation into a Python helper shared by tests and shell wrappers.

This can provide stronger parsing and testing ergonomics, but it is a larger
shift from the current shell-first smoke scripts.

### Option E: Generated Docs From Schema

Generate the docs field list from a central schema source.

This reduces documentation drift, but it adds tooling and should wait until the
schema changes often enough to justify generation.

## 5. Recommended Approach

The recommended initial approach is Option B: shared shell constants. Step 120
implements this approach.

Reasons:

- the current summary generation and distribution checks are shell-first
- the schema is small
- a shared shell file reduces duplication with minimal moving parts
- it avoids introducing a Python validator before there is a clear need
- it can later be replaced or wrapped by a Python helper if validation grows

The implemented initial shape defines:

- `SUMMARY_MANIFEST_SCHEMA_VERSION`
- `SUMMARY_MANIFEST_SUMMARY_SCHEMA_VERSION`
- `SUMMARY_MANIFEST_GENERATOR_SCRIPT`
- `SUMMARY_MANIFEST_CONTENT_SUPPRESSED`
- `SUMMARY_MANIFEST_NO_CONFIG_SUMMARY`
- `SUMMARY_MANIFEST_ALLOWED_KEYS`
- `SUMMARY_MANIFEST_FORBIDDEN_KEYS`

A JSON schema document may still be useful as public documentation later, but it
should not become a source of unsafe body content. Raw output bodies do not
belong in any schema file.

## 6. Information To Include Or Exclude

### Include In The Central Schema

The central schema should include:

- `manifest_schema_version`
- allowed keys
- required keys
- forbidden keys
- expected `no_config_summary`
- expected `content_suppressed`
- expected `generator_script`
- safe field descriptions
- a clear statement that raw body fields are not allowed

### Do Not Include In The Central Schema

The central schema must not include:

- raw summary body
- diagnostic summary body
- JSONL body
- candidate score rows
- expected action details
- config body
- performance metrics
- real participant data
- private paths

The schema should describe allowed metadata shape, not contain generated output.

## 7. Migration Policy

Future manifest field additions should require:

- schema version review
- docs update
- generator update
- checker update
- tests update
- release checklist update when relevant
- documented old-version behavior
- output-safety review

Unknown keys should remain fail-closed unless the manifest schema version is
bumped or the key is explicitly documented and validated.

If a field is added without updating the central schema, that should be treated
as a release-readiness problem, not as a reason to weaken validation.

## 8. Future Tests

Future centralization tests should verify:

- generator and checker use the same allowed-key list
- an allowed-key mismatch fails
- a new field requires schema update
- forbidden keys remain rejected
- manifest version mismatch fails
- docs or schema references stay aligned, where feasible
- stdout/stderr remain safe and do not print manifest bodies

These tests should stay synthetic-only and should not inspect or print raw
generated bodies.

## 9. Output Safety, Privacy, And No-Oracle Policy

Schema centralization is reliability and safety infrastructure.

It is:

- not a performance metric
- not a tuning signal
- not expected-action feedback
- not real-data evidence
- not private validation

It must preserve:

- no raw summary body in schema or docs
- no marker body output
- no JSONL body
- no diagnostic body
- no score rows
- no expected action feedback
- no real participant data

## 10. Beginner Notes

Schema constants are the small set of names and values that define what a file
is allowed to contain. For the summary manifest, examples include the schema
version and the list of allowed field names.

Putting these constants in one place reduces drift. If the generator and checker
each keep separate field lists, one can change without the other, and the check
may fail for confusing reasons.

The schema version says which rule set applies. When a new field is needed, the
team can decide whether it belongs in the current version or requires a new
version.

Raw body fields do not belong in the schema because the schema should describe
safe metadata, not carry the generated summary, JSONL, diagnostic body, or
private content.

## 11. Related Documents

- [Summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md)
- [Summary manifest schema hardening design](summary_manifest_schema_hardening_design.md)
- [Summary manifest schema sync check design](summary_manifest_schema_sync_check_design.md)
- [Synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md)
- [Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
