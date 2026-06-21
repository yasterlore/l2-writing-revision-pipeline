# Summary Manifest Sync Check Release Integration Design

This document is design documentation only. It does not change shell scripts,
CI workflows, test code, summary generation, scoring logic, scorer weights,
formulas, or tie-break policy.

It is not a performance evaluation. It does not approve real-data processing,
private validation, learner-state estimation, or expected-action tuning.

## 1. Purpose

The purpose of this design is to define how the no-config summary manifest sync
check should fit into a future release-quality process.

The release process should verify that shared manifest schema constants,
generated manifest metadata, and checker expectations remain aligned before a
public release-quality checkpoint. This must preserve output safety and
no-oracle boundaries.

The integration should not print generated bodies, introduce performance
metrics, or make the check part of scoring behavior.

## 2. Current State

Current components:

- shared constants file:
  `scripts/lib/summary_manifest_schema.sh`
- no-config summary generator:
  `scripts/run_synthetic_e2e_summary.sh`
- diagnostic distribution checker:
  `scripts/check_synthetic_diagnostic_distribution.sh`
- schema sync checker:
  `scripts/check_summary_manifest_schema_sync.sh`
- generated no-config manifest:
  `tmp/synthetic_e2e_summary/summary.manifest.json`
- public release docs:
  `docs/public_release_checklist.md`

Step 120 centralized manifest schema constants in the shared shell file.
Step 122 added the sync check script that compares the generated no-config
manifest with those constants. The public release checklist has a documentation
path for the check, but CI integration is not defined yet.

## 3. Why Integration Is Needed

Integration is useful because:

- release review should catch manifest schema drift before publication
- future field additions can miss generator, checker, docs, or test updates
- the generated manifest should match the shared allowed-key list and expected
  version constants
- forbidden-key validation should stay visible in release-quality checks
- diagnostic distribution checks and schema sync checks both depend on a fresh
  no-config summary run

The check is reliability infrastructure. It is not a correctness score, model
performance report, or learner-state estimate.

## 4. Recommended Execution Order

The no-config summary must be generated first:

```bash
scripts/run_synthetic_e2e_summary.sh
```

Two adjacent checks then depend on that output:

```bash
scripts/check_summary_manifest_schema_sync.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

Running the sync check before the diagnostic distribution check catches schema
drift early and confirms that the manifest shape matches shared constants before
the distribution check relies on the marker. Running the diagnostic distribution
check first is still valid when both commands are run sequentially after summary
generation, but it may surface distribution precondition errors before the
clearer schema-sync failure.

Initial recommendation:

1. `scripts/run_synthetic_e2e_summary.sh`
2. `scripts/check_summary_manifest_schema_sync.sh`
3. `scripts/check_synthetic_diagnostic_distribution.sh`

Do not run the summary generator in parallel with either dependent check.

## 5. Integration Options

### Option A: Public Release Checklist Manual Command

Keep the sync check as an explicit command in release-quality instructions.

This is the lowest-risk initial integration because it does not change CI,
scripts, or test runners. It also keeps the sync check visible during manual
release review.

### Option B: CI Workflow Step

Add the sync check to CI after summary generation.

This would catch drift automatically, but it should be a separate step after
the manual release process is stable.

### Option C: Wrapper Script

Create a wrapper that runs summary generation, sync check, and diagnostic
distribution check in order.

This would reduce ordering mistakes, but it would add another command surface
and should be deferred until the release command bundle is clearer.

### Option D: Integrate Into Diagnostic Distribution Check

Fold sync validation into `scripts/check_synthetic_diagnostic_distribution.sh`.

This reduces command count, but it blurs schema reliability checks with
diagnostic distribution checks. Keeping them separate makes failures easier to
understand.

### Option E: Python Unittest

Move the sync check into Python unit tests.

This may be useful if shell parsing becomes complex, but the current shell
smoke script already fits the surrounding release workflow.

## 6. Recommended Approach

The initial recommendation is Option A, with Option B as a future step:

- keep `scripts/check_summary_manifest_schema_sync.sh` independent
- document it in the public release checklist
- run it after `scripts/run_synthetic_e2e_summary.sh`
- run it before or adjacent to the diagnostic distribution check, with
  sync-before-distribution preferred for fail-fast schema drift detection
- defer CI integration to a later implementation step
- do not create a wrapper script yet
- do not merge the sync check into the diagnostic distribution check

This keeps the check small, explicit, and easy to reason about.

## 7. Output Safety Policy

The release-integrated sync check may print only:

- safe status labels
- safe repository-relative paths
- safe reason codes
- key names when they are not generated body content
- count-only metadata

It must not print:

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

## 8. Failure Policy

Sync check failure should be a release blocker.

Fail closed when:

- generated manifest is missing
- generated manifest is malformed
- manifest schema version mismatches the shared constant
- summary schema version mismatches the shared constant
- generator script field mismatches the shared constant
- allowed-key set and actual manifest keys differ
- unknown keys appear
- forbidden keys appear
- body-like fields appear

No failure should become a silent pass. Failure messages should remain safe and
count-only.

## 9. CI And Manual Guidance

Manual release-quality review should run the sync check whenever it runs the
no-config summary and diagnostic distribution checks.

CI guidance for a future step:

- generate the no-config summary first
- run the schema sync check after generation completes
- run the diagnostic distribution check in the same sequential group
- do not run dependent checks in parallel with summary generation
- keep `tmp/` outputs ignored
- keep logs safe and count-only

The sync check should remain no-config only and should not read config-enabled
summary paths.

## 10. Future Implementation Roadmap

Possible future work:

- add the sync check to a CI workflow after summary generation
- add an optional wrapper command bundle if manual ordering remains error-prone
- move or mirror the check in Python only if shell complexity grows
- keep summary hash hardening separate
- keep per-case diagnostic consistency hardening separate
- keep config-enabled summary checks separate from no-config manifest checks

Any future integration should update the public release checklist and preserve
safe-output behavior.

For the broader command ordering that would contain this sync check alongside
Python, Rust, TypeScript, config, and repository hygiene checks, see
[release-quality command bundle design](release_quality_command_bundle_design.md).

## 11. Beginner Notes

Release integration means deciding where a check belongs in the list of commands
run before a release-quality review.

Creating a check is not enough by itself. The check only helps if humans or CI
run it at the right time. Here, the right time is after the no-config summary
manifest has been generated.

The order matters because the sync check reads generated manifest metadata. If
the manifest does not exist yet, the check should fail as a precondition issue.
It should not guess, silently pass, or read another output family.

This is not performance evaluation. It only checks that safe metadata and shared
schema constants agree.

## 12. Related Documents

- [Summary manifest schema sync check design](summary_manifest_schema_sync_check_design.md)
- [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md)
- [Summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Public release checklist](public_release_checklist.md)
