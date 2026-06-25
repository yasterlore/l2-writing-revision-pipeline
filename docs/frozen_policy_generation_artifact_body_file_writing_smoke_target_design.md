# Frozen Policy Generation Artifact Body File Writing Smoke Target Design

## 1. Purpose

This document designs a future standalone Makefile smoke target for the
minimal artifact body file-writing path added in Step364.

It is a docs-only design. It does not implement a Makefile target, does not
add release-quality integration, does not implement isolated temp write
validation, does not implement a manifest writer, and does not connect the
artifact writer CLI.

This is not performance evaluation, real-data readiness, or production
readiness evidence.

## 2. Current State

- The artifact body generation CLI supports `--artifact-body-out`.
- Only `--mode safe-metadata` can write an artifact body file.
- The safe root is `tmp/artifact_body_generation/`.
- stdout/stderr remain body-free summaries.
- default/suppressed mode with `--artifact-body-out` is a usage error.
- No standalone file-writing smoke target exists yet.
- No release-quality file-writing smoke exists yet.
- No isolated temp write validator exists yet.
- No manifest writer exists.
- No artifact writer CLI integration exists.

## 3. Proposed Target Name

Candidates:

- `check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`
- `check-learner-state-artifact-body-file-writing-smoke`
- `check-artifact-body-file-writing-smoke`
- `check-artifact-body-output-smoke`

Recommended:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`

Reasons:

- It matches the learner-state / frozen policy generation / artifact body
  namespace.
- It is distinct from the no-write file writing fixture validator target.
- It clearly indicates actual file-writing smoke coverage.
- It remains meaningful if later added to release-quality.

## 4. Proposed Command

The future target should use one safe synthetic metadata-only fixture path and
one safe output path under the fixed safe root.

Recommended target sequence:

```bash
rm -f tmp/artifact_body_generation/smoke/safe_metadata_artifact_body.json
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_writer_result_pointer.json --mode safe-metadata --artifact-body-out smoke/safe_metadata_artifact_body.json
python3 -m json.tool tmp/artifact_body_generation/smoke/safe_metadata_artifact_body.json >/dev/null
rm -f tmp/artifact_body_generation/smoke/safe_metadata_artifact_body.json
rmdir tmp/artifact_body_generation/smoke 2>/dev/null || true
```

Optional written-file safety checks may scan only for forbidden field names or
synthetic sentinels. They must not print the written file content.

Recommended optional checks:

- no raw rows marker
- no logits marker
- no private path marker
- no manifest body marker
- no generated policy body marker
- no request body marker
- no pointer body marker

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke  Run artifact body safe-metadata file writing smoke`

## 6. Expected Behavior

- The target uses a safe output path under `tmp/artifact_body_generation/`.
- A file is written during the smoke.
- The written file parses as JSON.
- The smoke output is cleaned up.
- stdout/stderr remain body-free.
- The CLI summary includes:
  - `mode=artifact_body_generation`
  - `body_status=generated_safe_metadata_body`
  - `generation_status=pass`
  - `validation_status=pass`
  - `artifact_file_written=true`
  - `artifact_body_output_path_available=true`
  - `artifact_body_output_path=tmp/artifact_body_generation/smoke/safe_metadata_artifact_body.json`
  - `artifact_body_output_path_safety_checked=true`
  - `artifact_body_write_policy=safe_metadata_only_relative_tmp`
  - `manifest_file_written=false`
  - `manifest_body_generated=false`
  - `stdout_body_suppressed=true`
  - `reason_codes=none`
  - `failed_checks=none`
- No artifact body payload is printed.
- No manifest file is written.
- No generated policy body is written.
- No private or absolute path is printed.
- No real data is used.
- No performance evidence is produced.

## 7. Output And Logging Safety

Allowed:

- target label/help
- command shape
- summary fields
- safe relative output path
- parse check pass/fail
- cleanup confirmation

Forbidden:

- written file content
- artifact body payload
- request body
- pointer body
- expected body
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- absolute paths
- raw learner text
- raw logs

## 8. Cleanup Policy

- The target should remove the generated smoke file before running, avoiding
  overwrite errors from previous smoke attempts.
- The target should remove the generated smoke file after parse and safety
  checks.
- The target may remove the empty smoke directory.
- The target must not remove unrelated files.
- The target must not use absolute paths.
- Cleanup must tolerate a missing generated file.
- The expected steady state is no residue under the smoke output path.

## 9. Relation To The No-Write Fixture Validator

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`
remains a no-write fixture contract validator.

The proposed smoke target is different: it is a write-then-parse-then-cleanup
check for one valid safe-metadata output path. The two checks validate
different boundaries and should remain separate.

The no-write fixture target is already in release-quality. The new smoke
target should not be added to release-quality yet.

## 10. Relation To Release-Quality

- Do not add the smoke target to release-quality in the implementation step.
- First implement the standalone target.
- Then create a separate release-quality integration design.
- Then integrate the wrapper in a later step.
- Then create a remote/manual status marker after a successful remote run.

Release-quality may later include the smoke target only after cleanup,
body-free output, and no-leak checks are stable.

## 11. Relation To Isolated Temp Write Validation

The smoke target is not a fixture validator. It exercises one known-good
safe-metadata file-writing path.

Isolated temp write validation remains future work. A future isolated
validator can exercise many valid and invalid write cases without writing into
repository fixture directories.

Step367 adds the docs-only design for that future validator:
[Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md).

## 12. Future Tests And Checks For Implementation

Future implementation should verify:

- `make help` includes the target.
- The smoke target exits 0.
- The generated file exists during the command.
- The generated file parses as JSON.
- Cleanup removes the generated file.
- No output residue remains.
- stdout/stderr do not contain body payload.
- The summary includes `artifact_file_written=true`.
- The summary includes only a safe relative output path.
- The summary does not include an absolute path.
- `manifest_file_written=false`.
- `manifest_body_generated=false`.
- Safety scans over the generated file pass without printing content.
- Existing file-writing CLI tests remain passing.
- The no-write fixture target remains passing.
- `make check-release-quality` remains passing.

## 13. Docs Safety Policy

Docs for this smoke target may include command shapes, target names, field
names, and safe policy descriptions.

Docs must not include:

- written file body examples
- artifact body JSON examples
- artifact body payload examples
- raw logs
- private path examples
- output payload
- request body
- pointer body
- expected body
- manifest body
- raw rows
- logits
- raw learner text
- real data

## 14. Beginner-Friendly Explanation

A smoke target is a short command that checks one important path still works.
Here, the path is: generate a safe-metadata artifact body, write it to the
fixed safe root, parse it, and clean it up.

The Makefile target is useful after the CLI option exists because it gives
developers one memorable command instead of a long CLI invocation.

The no-write fixture target checks the contract for many future file-writing
cases without writing files. The proposed smoke target writes one file and
then removes it. They are complementary.

Cleanup matters because the CLI intentionally refuses to overwrite existing
output files. Leaving smoke residue behind would make the next run fail and
could confuse later checks.

The target should not enter release-quality immediately. It should first be
implemented and proven stable as a standalone local check.

## 15. What This Does Not Do

- does not add release-quality integration
- does not implement isolated temp write validation
- does not write a manifest
- does not connect artifact writer CLI
- does not change workflow YAML
- does not change Python code/tests
- does not change fixture JSON
- does not use real data
- does not compute metrics
- does not prove production readiness

## 16. Next Recommended Steps

- Step367: isolated temp write validation design.
- Step368: release-quality integration design for the smoke target.
- Later: wrapper integration and remote/manual status marker after the
  standalone smoke target is stable.

## 17. Step366 Implementation Status

Step366 implements the standalone Makefile smoke target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`

The target runs one safe-metadata artifact body file-writing smoke under
`tmp/artifact_body_generation/`, parses the generated file without printing
its content, scans for forbidden payload field names without printing
matches, and cleans up the generated smoke output. The target emits only the
CLI body-free summary and pass/fail metadata for parse, safety scan, and
cleanup.

This implementation does not add the smoke target to release-quality, does
not change workflow YAML, does not change Python code/tests, does not change
fixture JSON, does not implement isolated temp write validation, does not
write manifests, does not connect artifact writer CLI, does not use real
data, and does not compute metrics.

## 18. Step367 Isolated Temp Write Validation Design Status

Step367 adds the docs-only isolated temp write validation design:

[Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md).

The design covers a future isolated temp-root validator for multiple valid
and invalid artifact body file-writing cases. It does not implement the
validator, does not add a Makefile target, does not add release-quality
integration, does not change workflow YAML, does not change Python code/tests,
does not change fixture JSON, does not write manifests, does not connect
artifact writer CLI, does not use real data, and does not compute metrics.

## 19. Step368 Isolated Temp Write Fixture Contract Design Status

Step368 adds the docs-only fixture contract design:

[Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md).

The contract design keeps the standalone smoke target separate from future
multi-case isolated temp validation. It does not create fixture JSON, change
this smoke target, add release-quality integration, write manifests, connect
artifact writer CLI, use real data, or compute metrics.

## 20. Step369 Isolated Temp Write Fixture JSON Creation Status

Step369 creates the isolated write validation fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

The root contains 22 synthetic-only metadata fixture cases and 110 JSON files.
It instantiates the Step368 fixture contract for future isolated temp write
validation. It does not implement the validator, does not add a Makefile
target, does not add release-quality integration, does not write manifests,
and does not connect the artifact writer CLI.

## 21. Related Documents

- [Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/README.md)
- [Frozen policy generation artifact body file writing implementation final design](frozen_policy_generation_artifact_body_file_writing_implementation_final_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Public release checklist](public_release_checklist.md)
