# Frozen Policy Generation Artifact Body Safe-Metadata Release-Quality Remote Run Record Workflow

## 1. Purpose

This document designs how to record a future remote or manual GitHub Actions
Release Quality run that includes the frozen policy generation artifact body
safe-metadata CLI smoke.

This is a docs-only workflow design. It is not an actual status marker, not a
workflow execution, not an artifact body correctness evaluation, not artifact
file writing, not a manifest writer, not performance evaluation, and not a
real-data readiness claim.

The future record should capture only public-safe metadata showing that the
Release Quality wrapper included the safe-metadata artifact body generation
CLI smoke and that the smoke returned a body-free safe summary.

## 2. Current State

- Artifact body generation API exists.
- Artifact body generation CLI exists.
- Default suppressed Makefile target exists.
- Default suppressed target is included in release-quality.
- Safe-metadata Makefile target exists.
- Safe-metadata target is included in release-quality.
- Artifact body generation remote status marker exists for the suppressed
  target.
- Safe-metadata remote status marker does not exist yet.
- Artifact file writing does not exist.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

The safe-metadata target is:

`make check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The target runs one synthetic metadata-only request/pointer path with
`--mode safe-metadata`. It emits a body-free safe summary and does not write
artifact or manifest files.

## 3. Remote / Manual Run Purpose

The future remote/manual run should confirm that:

- the release-quality wrapper passes in GitHub Actions, not only locally
- safe-metadata CLI smoke is included in release-quality
- only public-safe metadata is recorded afterward
- the safe-metadata CLI smoke result is recorded as pass-only and count-only
  metadata

The remote/manual run is not artifact body correctness evidence, printable
artifact body payload evidence, artifact writer quality evidence, production
readiness evidence, performance evidence, calibration evidence, selective
prediction correctness evidence, learner-state estimator correctness
evidence, or real-data readiness evidence.

## 4. Future Status Marker Path

Candidate future status marker paths:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md` | Consistent with the learner-state status marker family. It clearly states that the marker covers the safe-metadata smoke. It is easy to place next to the suppressed generation and artifact body fixture markers. | Long filename. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_generation_safe_metadata_release_quality_remote_run_status.md` | Very explicit that safe-metadata belongs to artifact body generation. | Longer and less parallel with the existing artifact body generation marker. |
| `docs/status/frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md` | Shorter and readable. | Less consistent with the existing learner-state status marker family. |

Recommendation:

Use
`docs/status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md`
for the future status marker.

This keeps the marker aligned with the learner-state status marker family,
makes the safe-metadata smoke scope explicit, and keeps it easy to compare
with the suppressed generation and artifact body fixture markers.

## 5. Metadata To Record

A future public-safe status marker may record:

- workflow name
- job name
- repository
- branch
- commit full hash
- commit short hash
- run status
- job status
- run trigger type
- run date/time, if available
- `release_quality_check` included: yes/no
- artifact body fixture validator target included: yes/no
- artifact body generation suppressed target included: yes/no
- artifact body safe-metadata target included: yes/no
- safe-metadata label
- safe-metadata command
- `mode=artifact_body_generation`
- `body_status=generated_safe_metadata_body`
- `generation_status=pass`
- `validation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `request_body_count=0`
- `pointer_body_count=0`
- `expected_body_count=0`
- `manifest_body_count=0`
- no request body copied
- no pointer body copied
- no expected result body copied
- no artifact body payload copied
- no generated policy body copied
- no manifest body copied
- no raw rows copied
- no logits copied
- no private paths copied
- no tmp output generated by this target
- no artifact file generated
- no manifest file generated
- workflow YAML changed: yes/no
- artifacts recorded: yes/no
- raw logs stored: yes/no
- full job output stored: yes/no
- safety review summary

The safe-metadata label should be recorded as metadata only:

`release_quality_check: learner-state frozen policy generation artifact body generation safe-metadata CLI smoke`

The safe-metadata command should be recorded as metadata only:

`make check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

## 6. Metadata Not To Record

Do not record:

- raw logs
- full job output
- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- `expected_artifact_body_result` body
- policy body
- generated policy body
- artifact body payload
- generated artifact body
- frozen policy artifact body
- manifest body
- JSON body
- raw rows
- logits or probability dumps
- private paths
- raw learner text
- real participant data
- performance metric body
- screenshots containing raw logs
- copied GitHub log blocks

If a remote log includes unsafe details, do not paste those details into docs.
Record only a safe failure category or keep the detailed note private/local.

## 7. Status Marker Structure

The future status marker should use this structure:

1. Title
2. Purpose
3. Run identity
4. Wrapper inclusion summary
5. Safe-metadata artifact body generation CLI smoke summary
6. Suppressed artifact body generation CLI smoke summary
7. Artifact body fixture validation summary
8. Artifact writer runtime smoke summary
9. Artifact writer fixture validation summary
10. Generator scaffold runtime smoke summary
11. Generator scaffold fixture validation summary
12. Runtime scaffold smoke summary
13. Runtime scaffold fixture validation summary
14. Related checks summary
15. Safety review
16. Interpretation
17. What this does not prove
18. Next actions
19. Update history

Run identity should include workflow, job, repository, branch, commit, status,
and timing metadata only.

Wrapper inclusion summary should state whether release-quality included the
safe-metadata artifact body generation CLI smoke, suppressed artifact body
generation CLI smoke, artifact body fixture validation, artifact writer
fixture validation, artifact writer runtime smoke, generator scaffold checks,
runtime scaffold checks, and whether workflow YAML changed.

All summaries should remain pass-only or count-only. They should not copy
request bodies, pointer bodies, expected result bodies, policy bodies,
generated policy bodies, artifact body payloads, manifest bodies, fixture
bodies, or raw log excerpts.

## 8. Safe-Metadata Artifact Body Generation CLI Smoke Summary

Pass-only and safe metadata:

- included: true/false
- target:
  `make check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`
- label:
  `release_quality_check: learner-state frozen policy generation artifact body generation safe-metadata CLI smoke`
- command uses `--mode safe-metadata`
- mode: `artifact_body_generation`
- body status: `generated_safe_metadata_body`
- generation status: `pass`
- validation status: `pass`
- reason codes: none
- failed checks: none
- artifact file written: false
- manifest file written: false
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- raw row count: 0
- logits dump count: 0
- private path count: 0
- performance metric count: 0
- request body count: 0
- pointer body count: 0
- expected body count: 0
- manifest body count: 0
- request body copied: no
- pointer body copied: no
- expected result body copied: no
- artifact body payload copied: no
- generated policy body copied: no
- manifest body copied: no
- raw rows copied: no
- logits copied: no
- private paths copied: no
- tmp output generated by this target: no
- artifact file generated: no
- manifest file generated: no
- performance evidence: no

The marker may record safe IDs and schema names if they are needed for
traceability. It must not record the artifact body payload.

## 9. Suppressed Artifact Body Generation CLI Smoke Summary

Pass-only metadata:

- included: true/false
- target:
  `make check-learner-state-frozen-policy-generation-artifact-body-generation`
- label:
  `release_quality_check: learner-state frozen policy generation artifact body generation CLI smoke`
- command uses default suppressed mode
- body status: `suppressed_metadata_only`
- generation status: `pass`
- validation status: `pass`
- reason codes: none
- failed checks: none
- artifact body available: false
- artifact file written: false
- manifest file written: false
- safety flags: pass-only
- body, raw row, logits, private path, performance, request, pointer,
  expected, and manifest body counts: zero-only

This summary should stay separate from the safe-metadata smoke summary because
the two targets exercise different CLI modes.

## 10. Artifact Body Fixture Validation Summary

Count-only metadata:

- included: true/false
- target:
  `make check-learner-state-frozen-policy-generation-artifact-body-fixtures`
- label:
  `release_quality_check: learner-state frozen policy generation artifact body fixture validation`
- total cases: 18
- valid cases: 4
- invalid cases: 14
- matched cases: 18
- mismatched cases: 0
- input error cases: 0
- reason code counts: count-only
- safety flags: pass-only
- body, raw row, logits, private path, performance, request, pointer,
  expected, and manifest body counts: zero-only

## 11. Artifact Writer / Generator / Runtime Scaffold Summaries

Record related release-quality checks using pass-only or count-only metadata:

- artifact writer runtime smoke:
  target included yes/no, writer status, reason codes, failed checks, artifact
  body suppressed, artifact writing false, manifest body suppressed, manifest
  writing false
- artifact writer fixture validation:
  target included yes/no, total cases 17, valid cases 3, invalid cases 14,
  matched cases 17, mismatched cases 0, input error cases 0
- generator scaffold runtime smoke:
  target included yes/no, generation status, reason codes, failed checks,
  generated artifact written false, generated artifact body available false,
  artifact body suppressed true
- generator scaffold fixture validation:
  target included yes/no, total cases 18, matched cases 18, mismatched cases
  0, input error cases 0
- runtime scaffold smoke:
  target included yes/no, scaffold status, content suppressed true, no raw
  rows true, generated artifact written false, generated artifact body
  available false, artifact body suppressed true
- runtime scaffold fixture validation:
  target included yes/no, total cases 11, matched cases 11, mismatched cases
  0, input error cases 0

These summaries provide context without copying request bodies, pointer
bodies, fixture bodies, generated bodies, raw logs, or performance bodies.

## 12. Related Checks Summary

For learner-state release-quality checks, record pass-only or count-only
metadata when available:

- audit fixtures
- exporter CLI
- estimator input validation
- selective prediction calibration validation
- frozen policy validation
- frozen policy generation validation
- scaffold fixture validation
- scaffold runtime smoke
- generator scaffold fixture validation
- generator scaffold runtime smoke
- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation suppressed CLI smoke
- artifact body generation safe-metadata CLI smoke

Do not copy request bodies, pointer bodies, fixture bodies, generated bodies,
raw logs, or performance bodies from any related check.

## 13. Safety Review

The future marker must state:

- raw logs not copied
- full job output not copied
- `artifact_body_request` body not copied
- `artifact_writer_result_pointer` body not copied
- `expected_artifact_body_result` body not copied
- policy body not copied
- generated policy body not copied
- artifact body payload not copied
- generated artifact body not copied
- frozen policy artifact body not copied
- manifest body not copied
- JSON body not copied
- raw rows not copied
- logits/probability dump not copied
- private paths not copied
- raw learner text not copied
- real participant data not used
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`

## 14. Interpretation

Remote Release Quality success means the wrapper passed in GitHub Actions.

Safe-metadata smoke success means one safe-metadata synthetic request/pointer
path returned a body-free safe summary.

Suppressed smoke success means one default suppressed-mode synthetic
request/pointer path returned a body-free safe summary.

Artifact body fixture validation success means 18 metadata-only artifact body
fixture expected outcomes matched.

Artifact writer runtime smoke success means metadata-only artifact writer CLI
ran on one valid synthetic request/pointer and returned a safe pass summary.

Artifact writer fixture validation success means 17 metadata-only artifact
writer fixture expected outcomes matched.

Generator scaffold runtime smoke success means metadata-only generator
scaffold CLI ran on one valid synthetic request/pointer and returned a safe
pass summary.

Generator scaffold fixture validation success means 18 metadata-only generator
scaffold fixture expected outcomes matched.

Runtime scaffold fixture validation success means 11 runtime scaffold fixture
expected outcomes matched.

Runtime scaffold smoke success means runtime scaffold CLI ran on one valid
synthetic fixture and returned a safe pass summary.

It does not mean:

- artifact body generation correctness
- printable artifact body payload exists
- artifact body file writing exists
- manifest generation exists
- artifact writer implementation correctness
- generated policy quality
- model performance
- calibration quality
- learner-state estimator correctness
- real-data readiness
- production readiness

## 15. Failure Handling

If the remote run fails:

- record failure status only if public-safe
- do not paste raw logs
- summarize failure category only
- do not include private paths
- fix in a separate branch
- rerun and update the future status marker

## 16. Workflow For Actually Recording Later

Future recording steps:

1. Merge wrapper integration to main.
2. Trigger Release Quality manually or via the existing workflow.
3. Inspect the log locally in GitHub UI.
4. Extract only safe metadata.
5. Create the status marker in `docs/status`.
6. Run local checks.
7. Commit the status marker.
8. Do not store raw logs.

## 17. Relation To Public Release Checklist

The future status marker improves traceability. It is not a formal public
release, does not resolve license/reuse policy, and does not provide
performance evidence or real-data readiness.

Remote success is one safety signal only. It should be interpreted alongside
the public release checklist and the repository's synthetic-only/no-oracle
policy.

## 18. What This Does Not Do

This document does not:

- run a remote workflow
- create a status marker
- change workflow YAML
- change the release-quality wrapper
- change Makefile
- change Python code or tests
- change fixture JSON
- implement artifact file writing
- generate manifest bodies
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 19. Beginner-Friendly Explanation

A remote/manual run is the same release-quality command running in GitHub
Actions instead of only on a local machine. It helps show that the integrated
wrapper works in the shared CI environment.

A status marker is a short public-safe note that records the result. It is not
a copied log. It should say what ran, whether it passed, and which safe counts
or flags were observed.

Raw logs are not pasted because logs can accidentally contain unsafe content,
private paths, or too much operational detail. Pass-only and count-only
metadata is enough for traceability without copying payloads.

Safe-metadata smoke success means one safe-metadata path ran and produced a
body-free safe summary. It is not a proof that artifact body generation is
correct, that printable body payloads exist, or that the system is
production-ready.

## 20. Next Recommended Steps

- Run the remote/manual Release Quality workflow after this docs-only workflow
  design is reviewed.
- Create the future status marker only after a public-safe successful remote
  or manual run.
- Keep artifact body file writing, manifest writer, output file options, and
  artifact writer CLI integration as separate future work.

## 21. Step349 Remote Run Status Marker Status

Step349 creates the public-safe remote/manual Release Quality status marker
for the safe-metadata artifact body generation CLI smoke:

[Learner-state frozen policy generation artifact body safe-metadata release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md).

The marker records only run identity metadata, wrapper inclusion metadata,
pass-only safe-metadata smoke status, pass-only suppressed smoke status,
count-only related summaries, and safety review statements. It does not
include raw logs, full job output, request bodies, pointer bodies, expected
result bodies, artifact body payloads, generated policy bodies, manifest
bodies, raw rows, logits, private paths, raw learner text, real participant
data, performance metric bodies, or production readiness claims.
