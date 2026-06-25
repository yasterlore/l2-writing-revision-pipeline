# Frozen Policy Generation Artifact Body File Writing Implementation Final Design

## 1. Purpose

This document freezes the final implementation design for future artifact body
file writing from the artifact body generation CLI.

This is a docs-only final implementation design. It is not an implementation,
not CLI option implementation, not isolated temp write validation, not a
manifest writer, not artifact writer CLI integration, and not release-quality
integration.

The design keeps the boundary synthetic-only, metadata-only, no-oracle, and
body-safe. It prepares the next implementation step without writing files in
this step.

## 2. Current State

- Artifact body generation API exists.
- Artifact body generation CLI exists.
- Safe-metadata mode exists.
- Suppressed mode exists.
- Safe-metadata and suppressed Makefile targets exist.
- Both generation targets are in release-quality.
- Remote/manual status markers exist for suppressed generation and
  safe-metadata generation smoke coverage.
- File writing fixtures exist.
- Static/no-write file writing fixture validator API exists.
- Static/no-write file writing fixture validator CLI exists.
- Static/no-write file writing fixture validator Makefile target exists.
- File writing fixture validation is in release-quality.
- File writing fixture remote/manual status marker exists.
- Artifact body file writing does not exist.
- `--artifact-body-out` does not exist.
- Isolated temp write validation does not exist.
- Manifest writer does not exist.
- Artifact writer CLI integration does not exist.

The file writing fixture root contains 29 synthetic metadata-only cases and
116 JSON files. Those fixtures are contracts for future validation; this
design does not modify them.

## 3. Implementation Goal For Next Step

The minimal future implementation step should:

- add `--artifact-body-out`
- allow file writing only with `--mode safe-metadata`
- write only `generated_safe_metadata_body`
- keep stdout and stderr body-free
- write only to a safe relative path resolved under a controlled output root
- avoid manifest file writing
- avoid artifact writer CLI integration
- avoid release-quality integration in the same step
- avoid isolated temp write validator integration in the same step unless
  minimal unit tests require temporary directories

The next step should remain a CLI/unit-test implementation step, not a
release-quality or workflow step.

## 4. CLI Option Contract

Recommended option:

`--artifact-body-out <relative-safe-path>`

Contract:

- When absent, existing suppressed and safe-metadata behavior remains
  unchanged.
- When present with `--mode safe-metadata`, the CLI may attempt file writing
  only after generation and body audit pass.
- When present with the default suppressed mode, the CLI returns a usage
  error.
- When present with explicit `--mode suppressed`, the CLI returns a usage
  error.
- When present with an unsafe path, the CLI returns a usage error before any
  write attempt.
- stdout remains summary-only.
- stderr must not print the body payload.
- The body payload is never printed to stdout or stderr.

The option name is intentionally specific: it identifies artifact body file
output and avoids confusion with manifest output, artifact writer output, or
stdout printing.

## 5. Output Path Policy

Future file writing must enforce:

- relative path required
- allowed root required
- no absolute path
- no home path
- no drive root
- no parent traversal
- no private path marker
- no private cloud marker
- no hidden private directories
- `.json` extension required
- safe filename charset required
- path length limit required
- no overwrite unless an explicit future overwrite policy exists
- created parent directories allowed only under the safe root if the future
  implementation chooses to allow parent creation
- initial implementation uses only a caller-provided relative path resolved
  under a safe root

The path policy should fail before any body file is opened when the path is
unsafe.

## 6. Safe Root Policy

Candidate policies:

| Candidate | Summary | Tradeoff |
| --- | --- | --- |
| A. Require `--artifact-body-out tmp/...` | Caller includes the temporary root in the relative path. | Simple, but repeats root policy in every invocation and makes unsafe path review noisier. |
| B. Resolve a relative path under repository root | Any safe relative path could be placed under the repository root. | Flexible, but easier to accidentally target fixture or source directories. |
| C. Resolve a relative path under `tmp/artifact_body_generation/` | CLI owns a fixed safe output root and accepts a relative child path. | Best initial safety boundary and easiest future cleanup story. |

Recommended policy:

Use a fixed safe root: `tmp/artifact_body_generation/`.

Reasons:

- It helps avoid accidental repository fixture overwrite.
- It is safe for local smoke and unit tests before release-quality staging.
- It avoids exposing private absolute paths in summaries.
- It provides a clear future cleanup policy.
- It keeps output files out of fixture roots and source directories.

This step does not implement that root policy.

## 7. File Content Contract

Allowed file content fields:

- artifact_body_schema_version
- artifact_body_id
- artifact_id
- manifest_id
- writer_version
- body_status
- body_type
- synthetic_only_notice
- no_oracle_notice
- non_proof_notice
- validation_reference_ids
- safety flags
- count summary
- safe metadata sections
- no raw data notices

Forbidden file content:

- raw learner text
- raw rows
- raw events
- revision events
- micro episode rows
- final_text
- observed_after_text
- gold labels
- expected action payload
- scoring feedback payload
- logits
- probabilities
- model scores
- performance metric body
- request body
- pointer body
- expected result body
- generated policy body
- frozen policy body
- manifest body
- private paths
- absolute local paths
- GitHub raw logs
- full job output
- real participant metadata

The written file, if implemented later, must be parseable and must contain
only allowed safe metadata. This design intentionally does not include any
artifact body payload example.

## 8. Result Summary Contract

Future summary fields may include:

- `artifact_file_written=true/false`
- `artifact_body_output_path_available=true/false`
- `artifact_body_output_path=<safe-relative-path-only>`
- `artifact_body_output_path_safety_checked=true`
- `artifact_body_write_policy=safe_metadata_only_relative_tmp`
- `manifest_file_written=false`
- `manifest_body_generated=false`
- `stdout_body_suppressed=true`

Future summary fields must not include:

- absolute output path
- private output path
- full body payload
- file contents
- manifest body

Summary output should remain small, deterministic, and body-free.

## 9. Fail-Closed / Usage-Error Matrix

| Scenario | Recommended outcome | File written |
| --- | --- | --- |
| safe-metadata plus safe relative output path | pass | yes |
| safe-metadata without output path | pass | no |
| default suppressed mode plus output path | usage error | no |
| explicit suppressed mode plus output path | usage error | no |
| safe-metadata plus absolute path | usage error | no |
| safe-metadata plus parent traversal | usage error | no |
| safe-metadata plus private marker | usage error | no |
| safe-metadata plus existing output path without overwrite policy | fail closed | no |
| generation fail-closed plus output path | fail closed | no |
| unsafe body audit plus output path | fail closed | no |
| manifest write request | fail closed | no |
| generated policy body write attempt | fail closed | no |

Usage errors are preferred for caller-supplied invalid option/path shapes.
Fail-closed outcomes are preferred for generated result, audit, or policy
violations discovered after valid CLI usage.

## 10. Tests For Implementation Step

Future Step364 tests should cover:

- no output option keeps existing suppressed behavior
- no output option keeps existing safe-metadata behavior
- safe-metadata plus safe relative output writes a file
- written file is parseable
- written file contains only allowed keys
- stdout does not contain payload
- `artifact_file_written=true` only when file written
- `manifest_file_written=false` always
- suppressed/default plus output path returns usage error
- absolute output path rejected
- parent traversal rejected
- private marker rejected
- overwrite without policy rejected
- no real data in written file
- no raw text in written file
- no raw rows in written file
- no logits in written file
- no private path in written file
- no manifest body in written file
- no generated policy body in written file
- existing CLI tests remain passing
- static fixture validator remains passing
- release-quality still passes

Unit tests may use isolated temporary directories. Release-quality should not
gain a file-writing target in the same implementation step.

## 11. Relation To Fixture Validator

- The static fixture validator remains no-write.
- File writing implementation tests should use isolated temp directories in
  unit tests only.
- The fixture validator should not change in the same implementation step
  unless absolutely necessary.
- Isolated temp write validation can be a future step.
- The no-write release-quality target should remain no-write.

The file writing fixtures are contracts for path and content policy. The
first implementation should not turn the fixture validator into a writer.

## 12. Relation To Makefile / Release-Quality

- Do not add file-writing execution to release-quality in the initial
  implementation.
- Do not add a Makefile target in the initial implementation unless a
  separate design approves it.
- First implement the CLI option and unit tests.
- Later design a standalone file-writing smoke target.
- Later design release-quality integration.
- Later create a remote/manual status marker after wrapper integration.

The existing no-write target remains the release-quality safety check.

## 13. Relation To Manifest Writer

- Manifest writer remains separate.
- File writing does not create a manifest.
- `manifest_file_written=false`.
- `manifest_body_generated=false`.
- A future manifest may reference artifact body file metadata only after a
  separate manifest design.

Artifact body file writing success is not manifest generation success.

## 14. Relation To Artifact Writer CLI

- Artifact writer CLI remains body-free.
- File writing is initially limited to the artifact body generation CLI.
- Artifact writer CLI integration requires a separate design.
- Artifact writer runtime target remains unchanged.

This keeps the artifact writer metadata boundary stable while the body file
writing path is introduced in a narrower CLI.

## 15. Docs Safety Policy

Docs for this work may include:

- option names
- field names
- target names
- command shapes
- safe policy descriptions
- pass-only/count-only summaries

Docs for this work must not include:

- body payload examples
- JSON body examples
- private path examples
- raw logs
- raw rows
- logits
- probabilities
- real data
- raw learner text
- manifest body

## 16. Beginner-Friendly Explanation

The final design exists so the next implementation step has a small, agreed
boundary. File writing is a place where mistakes can leak content or write to
the wrong location, so the policy is fixed before adding code.

Only safe-metadata mode should be able to write because it is the only mode
that produces the safe metadata body intended for this future file output.
Suppressed mode is intentionally body-free, so asking it to write a body file
should be a usage error.

The CLI should not print the body to stdout because terminal output is easy
to copy into logs or docs. The future implementation may write a file, but
the terminal summary should stay metadata-only.

A safe root is needed so a caller cannot accidentally write into fixture
directories, source directories, private directories, or arbitrary local
paths. A fixed temporary output root gives the first implementation a tight
boundary.

The manifest writer is separate because a manifest is a different artifact
with its own body-suppression and file-writing policy. Writing an artifact
body file should not quietly imply manifest generation.

## 17. What This Does Not Do

- does not implement file writing
- does not add a CLI option
- does not write artifact files
- does not write manifest files
- does not change Makefile
- does not change release-quality
- does not change workflow YAML
- does not change Python code/tests
- does not change fixture JSON
- does not use real data
- does not compute metrics
- does not prove production readiness

## 18. Next Recommended Steps

- Step364: minimal CLI file writing implementation.
- Step365: standalone file-writing smoke target design.
- Step366: standalone file-writing smoke target implementation.
- Step367: isolated temp write validation design.
- Later: release-quality integration design for a standalone file-writing
  smoke target after the implementation and isolated checks are stable.

## 19. Step364 Implementation Status

Step364 implements the minimal artifact body generation CLI file-writing
path described here. The implementation adds `--artifact-body-out` for
`--mode safe-metadata` only, writes under the fixed safe root
`tmp/artifact_body_generation/`, keeps stdout/stderr summary-only, rejects
suppressed/default mode output requests as usage errors, rejects unsafe
relative paths, and keeps manifest writing disabled.

The implementation does not add a Makefile smoke target, does not add
release-quality integration, does not change workflow YAML, does not change
fixture JSON, does not implement isolated temp write validation, does not
write manifest files, does not connect artifact writer CLI, does not use
real data, and does not compute metrics.

## 20. Step365 Smoke Target Design Status

Step365 adds a docs-only standalone smoke target design:

[Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md).

The design explains a future Makefile target that should run one safe
safe-metadata file-writing smoke, parse the generated file, and clean it up.
It does not implement a Makefile target, does not add release-quality
integration, does not implement isolated temp write validation, does not
write manifests, does not connect artifact writer CLI, does not use real
data, and does not compute metrics.

## 21. Step366 Smoke Target Implementation Status

Step366 implements the standalone Makefile smoke target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`

The target runs one safe-metadata file-writing smoke, validates that the
generated output parses as JSON, scans for forbidden payload field names
without printing file content, and cleans up the generated smoke output. It
does not add release-quality integration, does not change workflow YAML, does
not change Python code/tests, does not change fixture JSON, does not
implement isolated temp write validation, does not write manifests, does not
connect artifact writer CLI, does not use real data, and does not compute
metrics.

## 22. Step367 Isolated Temp Write Validation Design Status

Step367 adds the docs-only isolated temp write validation design:

[Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md).

The design covers future multi-case validation under an isolated temp root.
It remains separate from the single-path smoke target, the no-write fixture
validator, release-quality, manifest writer work, and artifact writer CLI
integration.

## 23. Step368 Isolated Temp Write Fixture Contract Design Status

Step368 adds the docs-only fixture contract design:

[Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md).

The contract design fixes future case files and expected result fields for
isolated temp write validation. It does not create fixture JSON, implement a
validator, change Makefile, change release-quality, write manifests, connect
artifact writer CLI, use real data, or compute metrics.

## 24. Related Documents

- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body file writing fixture release-quality integration design](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_integration_design.md)
- [Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Public release checklist](public_release_checklist.md)
