# Frozen Policy Generation Artifact Body Safe-Metadata Makefile Target Design

## 1. Purpose

This document designs a future standalone Makefile target for running the
frozen policy generation artifact body generation CLI in `safe-metadata`
mode.

This is a docs-only design. It is not Makefile implementation, not
release-quality integration, not artifact file writing, not a manifest writer,
not artifact writer CLI integration, not performance evaluation, and not a
real-data readiness claim.

The target should make it easy to run the existing CLI safe-metadata smoke
without printing artifact body payloads or writing files.

## 2. Current State

- Artifact body generation API exists.
- Artifact body generation CLI exists.
- Default suppressed Makefile target exists.
- Default suppressed target is included in release-quality.
- Safe-metadata CLI mode exists and is manually runnable.
- Safe-metadata Makefile target does not exist.
- Artifact file writing does not exist.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

The current default suppressed target is:

`check-learner-state-frozen-policy-generation-artifact-body-generation`

The proposed target in this document is separate from that target and should
remain standalone first.

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata` | Closely parallels the existing generation target. It names the learner-state namespace, frozen policy generation pipeline, artifact body generation surface, and safe-metadata mode. | Long. |
| `check-learner-state-frozen-policy-generation-artifact-body-safe-metadata` | Slightly shorter while still scoped to learner-state and frozen policy generation. | Less clearly tied to the artifact body generation CLI target family. |
| `check-frozen-policy-generation-artifact-body-safe-metadata` | Shorter and readable. | Drops the learner-state namespace used by the surrounding targets. |
| `check-artifact-body-safe-metadata` | Very short. | Too broad for release-quality labels and easy to confuse with unrelated artifact body checks. |

Recommendation:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

Rationale:

- It aligns with the existing default generation target.
- It makes clear that this is a safe-metadata mode smoke.
- It preserves the learner-state / frozen policy generation namespace.
- It is suitable for future release-quality labels if needed.

## 4. Proposed Command

The future target should run:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_writer_result_pointer.json --mode safe-metadata`

This command uses the existing synthetic safe-metadata fixture pair. It should
not print request bodies, pointer bodies, expected result bodies, artifact body
payloads, generated policy bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata  Run artifact body generation safe-metadata CLI smoke`

## 6. Expected Behavior

The future target should:

- run artifact body generation CLI on one valid synthetic safe-metadata
  request/pointer pair
- exit 0
- emit `body_status=generated_safe_metadata_body`
- emit `generation_status=pass`
- emit `validation_status=pass`
- emit `reason_codes=none`
- emit `failed_checks=none`
- keep output summary-only and body-free
- emit `artifact_body_available=false` or an equivalent summary-only
  availability flag that does not expose the body payload
- emit `artifact_file_written=false`
- emit `manifest_file_written=false`
- emit `content_suppressed=true`
- emit `no_raw_rows=true`
- emit `no_logits_dump=true`
- emit `no_private_paths=true`
- emit `no_performance_claims=true`
- emit `synthetic_only_checked=true`
- emit `no_oracle_checked=true`
- emit `artifact_policy_checked=true`
- emit `body_suppression_checked=true`
- emit `raw_row_count=0`
- emit `logits_dump_count=0`
- emit `private_path_count=0`
- emit `performance_metric_count=0`
- emit `request_body_count=0`
- emit `pointer_body_count=0`
- emit `expected_body_count=0`
- emit `manifest_body_count=0`
- print no artifact body payload
- print no request body
- print no pointer body
- print no manifest body
- create no output file
- write no artifact file
- write no manifest file

The existing CLI summary may report that a safe metadata body is available as
safe metadata. That is acceptable only if stdout/stderr remain summary-only
and do not include the artifact body payload.

## 7. Output / Logging Safety

Allowed in target output:

- mode
- safe IDs
- body status
- generation status
- validation status
- reason code names
- failed check names
- safety flags
- count summary
- `artifact_file_written=false`
- `manifest_file_written=false`
- safe summary label

Forbidden in target output:

- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- `expected_artifact_body_result` body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body
- GitHub raw logs
- local absolute paths

## 8. Relation To Default Suppressed Generation Target

The default suppressed generation target proves that the CLI can return a
suppressed, body-free summary from one synthetic request/pointer pair.

The safe-metadata target would prove that the CLI can traverse safe-metadata
mode while still not printing body payloads and still not writing files.

Neither target proves artifact body generation correctness. Neither target
writes artifact files. Neither target writes manifest files. Neither target
uses real data or computes metrics.

## 9. Release-Quality Staging

Recommended staging:

- keep the safe-metadata target standalone first
- do not add it to release-quality in the same step as target implementation
- create a release-quality integration design later if needed
- keep the existing default suppressed smoke as the minimal release-quality
  generation path for now
- treat safe-metadata release-quality integration as optional future work

## 10. Future Implementation Notes

Future target implementation should:

- add the target to `.PHONY`
- add the help text to `make help`
- place the target near the default artifact body generation target
- use human safe summary by default
- not use `--json` by default
- not create output files
- not write temporary outputs
- not write artifact files
- not write manifest files
- not alter the release-quality wrapper in the same step
- not alter workflow YAML

## 11. Future Tests

Future implementation should verify:

- `make help` includes the safe-metadata target
- safe-metadata target exits 0
- output includes `body_status=generated_safe_metadata_body`
- output includes `generation_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes file-writing false flags
- output includes safety flags
- output includes zero counts
- no artifact body payload is printed
- no request or pointer body is printed
- no manifest body is printed
- no raw row, logits, private path, raw learner text, or performance metric
  leakage appears
- no output files are created
- Makefile diff is limited to target, help, and `.PHONY`
- wrapper and workflow diffs remain empty

## 12. Docs Safety Policy

Docs should include only target names, commands, field names, safety flags,
counts, and reason-code names.

Docs must not include command output examples, JSON output examples, artifact
body payload examples, request body examples, pointer body examples, manifest
body examples, raw logs, copied GitHub log blocks, raw rows, logits, private
paths, raw learner text, real participant data, or performance metric bodies.

## 13. Beginner-Friendly Explanation

Safe-metadata mode asks the artifact body generation CLI to build a safe
metadata-oriented body state internally, but the CLI still reports only a
summary. It should not print the body payload and should not write files.

The default suppressed target came first because it is the smallest safety
boundary: the CLI runs while keeping the body suppressed. A safe-metadata
target is a natural next standalone smoke because it exercises the broader
mode while keeping output body-free.

Safe-metadata should still avoid body payload output because logs and docs are
public-facing surfaces. Even safe metadata can become too detailed if copied
as a body. The target should therefore keep stdout/stderr limited to summary
fields, flags, IDs, and counts.

This target should not go into release-quality immediately. It should first
exist as a standalone command so the project can verify its behavior and log
safety before deciding whether to add it to the wrapper.

File writing and manifest writer behavior remain separate because they create
new storage and output surfaces. They need their own designs, checks, and
safety gates.

## 14. What This Does Not Do

This document does not:

- implement a Makefile target
- integrate release-quality
- change workflow YAML
- change Python code or tests
- change fixture JSON
- print artifact body payload
- write artifact files
- generate manifest bodies
- write manifest files
- change artifact writer CLI
- use real data
- evaluate performance
- compute metrics
- claim production readiness

## 15. Step345 Implementation Status

Step345 implements the standalone safe-metadata Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The target runs the artifact body generation CLI with the existing synthetic
safe-metadata request/pointer pair and `--mode safe-metadata`. It uses human
safe summary output by default, creates no output files, writes no artifact
files, writes no manifest files, and does not print artifact body payloads.

Step345 adds the target to `.PHONY` and `make help`. It does not add the
target to release-quality, does not change workflow YAML, does not change
Python code or tests, does not change fixture JSON, does not connect artifact
writer CLI, does not implement artifact file writing, does not generate
manifest bodies, does not use real data, does not evaluate performance, and
does not compute metrics.

## 16. Step346 Release-Quality Integration Design Status

Step346 designs a future release-quality wrapper integration for the
standalone safe-metadata target:

[Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md).

The design recommends placing the safe-metadata smoke after the default
suppressed generation smoke and before config/scoring smoke checks. It does
not change the wrapper, workflow YAML, Makefile, Python code or tests,
fixture JSON, artifact writer CLI behavior, artifact file writing, manifest
generation, real-data use, performance evaluation, or metrics.

## 17. Step347 Release-Quality Wrapper Integration Status

Step347 adds this standalone safe-metadata target to the release-quality
wrapper after the default suppressed artifact body generation CLI smoke and
before config/scoring smoke checks. The target remains summary-only and
body-free.

Step347 does not change workflow YAML, does not change Makefile, does not
change Python code or tests, does not change fixture JSON, does not connect
artifact writer CLI, does not write artifact files, does not generate
manifest bodies, does not use real data, does not evaluate performance, and
does not compute metrics.

## 18. Step348 Remote Run Record Workflow Design Status

Step348 designs the future remote/manual Release Quality run record workflow
for the safe-metadata target now included in the wrapper:

[Frozen policy generation artifact body safe-metadata release-quality remote run record workflow](frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_record_workflow.md).

The design keeps this Makefile target unchanged and specifies that a future
status marker should record only public-safe pass-only/count-only metadata.
It must not copy raw logs, full job output, request bodies, pointer bodies,
artifact body payloads, generated policy bodies, manifest bodies, raw rows,
logits, private paths, raw learner text, real participant data, or
performance metric bodies.

## 19. Step349 Remote Run Status Marker Status

Step349 creates the public-safe remote/manual Release Quality status marker
for this safe-metadata target:

[Learner-state frozen policy generation artifact body safe-metadata release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md).

The marker records that the target was included in release-quality and passed
remotely. It does not change this Makefile target, does not write artifact
files, does not generate manifest bodies, does not connect artifact writer
CLI, does not use real data, and does not compute metrics.

## 20. Step350 Artifact Body File Writing Design Status

Step350 designs future safe metadata artifact body file writing:

[Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md).

The design keeps this safe-metadata Makefile target unchanged and does not
add file writing to it. Future file writing should be a separate explicit
CLI option and later staging path. Step350 does not change Makefile, does
not change release-quality, does not write artifact files, does not generate
manifest bodies, does not connect artifact writer CLI, does not use real
data, and does not compute metrics.
