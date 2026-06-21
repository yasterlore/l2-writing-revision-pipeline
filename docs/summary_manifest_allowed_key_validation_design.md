# Summary Manifest Allowed-Key Validation Design

This document is design documentation only. It does not change shell scripts,
test code, summary generation, scoring logic, scorer weights, formulas, or
tie-break policy.

It is not a performance evaluation and does not approve any real-data workflow.
The summary manifest remains safe/count-only reliability metadata.

## 1. Purpose

The purpose of this design is to decide how `summary.manifest.json` should
handle unknown keys in future validation.

The goals are:

- make manifest allowed-key validation explicit
- clarify whether unknown keys should fail closed
- keep the manifest limited to safe/count-only metadata
- reduce the chance that raw bodies or private review details are added by
  accident
- preserve output safety, privacy, and no-oracle boundaries

Step 118 implemented the initial checker-side allowed-key validation for
`manifest_schema_version="1.0"`:

- `scripts/check_synthetic_diagnostic_distribution.sh` rejects unknown manifest
  keys as precondition failures
- explicit forbidden body-like keys still fail with the forbidden-key reason
  before the unknown-key check
- the manifest schema itself is unchanged
- the checker does not print the manifest body

Summary hash, per-case diagnostic consistency hardening, and wrapper scripts
remain future work.

For future work on moving manifest schema constants out of individual scripts,
see [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md).

## 2. Current Manifest Fields

The current no-config summary manifest fields are:

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

These fields describe completion and compatibility metadata for the no-config
synthetic E2E summary. They are not summary contents and are not performance
metrics.

## 3. Current Validation State

The diagnostic distribution check currently validates:

- required marker exists
- marker is valid JSON
- `manifest_schema_version` has the expected value
- all marker keys are in the allowed-key list for version `1.0`
- `content_suppressed` is `true`
- `no_config_summary` is `true`
- `case_count` is an integer greater than zero
- `diagnostic_summary_count` is an integer greater than or equal to zero
- `summary_path` matches the expected no-config summary path
- `generator_script` matches the expected summary script
- forbidden body-like keys are absent
- marker `case_count` equals the summary data-row count

The checker fails closed for malformed or unsafe manifest states. It does not
print the manifest body.

## 4. Benefits And Risks

### Benefits

Strict allowed-key validation can:

- reject unknown unsafe fields early
- prevent quiet manifest schema drift
- reduce the chance that raw body fields are introduced accidentally
- make `manifest_schema_version` meaningful in practice
- improve public release safety by keeping manifest contents predictable
- make future review simpler because the allowed metadata surface is small

### Risks

Strict allowed-key validation can also:

- break future field additions unless the schema and checker are updated
- fail when docs and scripts disagree about the schema
- require an explicit migration path for optional future fields
- add friction during development
- make experimental metadata awkward if versioning rules are unclear

The safety benefit is worth the friction only if future field additions are
handled through documented schema updates.

## 5. Design Options

### Option A: Forbidden-Key Only

Keep the current model and reject only known unsafe keys.

This is flexible, but unknown safe-looking fields can drift into the manifest
without review. It also relies on the forbidden-key list staying complete.

### Option B: Strict Allowed-Key Validation

Reject any key that is not in a known allowed-key list.

This is the safest shape for the current small manifest, but it requires careful
updates whenever a new field is added.

### Option C: Allowed-Key Validation With Schema-Version Migration

Use strict allowed keys for each `manifest_schema_version`. Future fields must
be added through a schema-version bump or a documented optional-key update.

This balances safety and maintainability because the checker can decide which
keys are valid for each manifest schema version.

### Option D: Warning Phase Then Required Phase

First warn on unknown keys, then later make them fail closed.

This can help large migrations, but the current manifest producer and checker
are controlled together, so a warning phase is not necessary for the initial
strict mode.

### Option E: Allow `x_` Experimental Fields

Permit experimental keys with an `x_` prefix.

This is not recommended initially. Experimental fields can become an accidental
escape hatch for unreviewed metadata, and the manifest should stay deliberately
small.

## 6. Recommended Approach

The recommended approach is Option C:

- for `manifest_schema_version="1.0"`, use strict allowed keys
- future fields require a manifest schema-version bump or a documented optional
  key update
- no `x_` experimental fields initially
- unknown keys should be a precondition failure
- forbidden body-like keys should continue to fail with an explicit
  forbidden-key reason

This keeps the current manifest stable while leaving a clear path for future
safe/count-only metadata.

## 7. Allowed Keys Candidate List

For `manifest_schema_version="1.0"`, the candidate allowed keys are:

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

Future fields should require:

- manifest schema-version decision
- docs update
- validation update
- tests update
- output-safety review

No future field should carry raw summary rows, diagnostic bodies, JSONL rows,
candidate score rows, expected action details, config bodies, private paths, or
performance metrics.

## 8. Unknown Key Failure Policy

Unknown keys should be treated as a precondition failure.

Recommended behavior:

- exit with the same precondition-failure class used for invalid manifests
- print a safe reason only
- do not print the manifest JSON body
- print an unknown key name only if the key name itself is safe
- if the key is body-like or explicitly forbidden, fail with the forbidden-key
  reason
- do not silently ignore unknown keys

Step 118 implements this policy for `manifest_schema_version="1.0"`.

This policy makes schema drift visible while keeping stdout/stderr safe.

## 9. Future Tests

Future allowed-key validation should include tests for:

- current valid manifest passes
- unknown safe-looking key fails
- forbidden body-like key fails
- missing required key fails
- schema version mismatch fails
- future schema-version behavior is documented before implementation
- stdout/stderr remain safe and do not include marker bodies

These tests should remain no-config only and should not use real participant
data.

## 10. Output Safety, Privacy, And No-Oracle Policy

Allowed-key validation must preserve these boundaries:

- no marker body output
- no summary body output
- no JSONL body output
- no diagnostic body output
- no candidate score rows
- no expected action feedback
- no real participant data
- no config body
- no performance metric or publication-style claim

The manifest is not training data, not a tuning signal, and not performance
evidence. It only helps confirm that a safe no-config synthetic summary was
generated in the expected shape.

## 11. Beginner Notes

An allowed key is a field name that the checker expects and permits in the
manifest. If the manifest contains a field that is not on that list, it is an
unknown key.

Unknown keys can be risky because they may hide accidental schema drift or a
field that should never be public, such as raw output content. Strict validation
keeps the manifest small and predictable.

`manifest_schema_version` is the agreement between the manifest writer and the
manifest checker. If future metadata is needed, the schema version or documented
allowed-key list should change at the same time as the tests.

This is stricter than the current forbidden-key-only model, but it improves
safety because new fields cannot appear quietly.

## 12. Related Documents

- [Summary manifest schema hardening design](summary_manifest_schema_hardening_design.md)
- [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md)
- [Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md)
- [Synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Public release checklist](public_release_checklist.md)
