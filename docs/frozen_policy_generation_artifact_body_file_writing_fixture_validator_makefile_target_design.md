# Frozen Policy Generation Artifact Body File Writing Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for running the artifact body
file writing fixture validator CLI.

It is a docs-only Makefile target design. It does not implement the target,
does not add release-quality integration, does not implement artifact body
file writing, does not add `--artifact-body-out`, does not run isolated temp
write validation, does not implement a manifest writer, and does not connect
artifact writer CLI.

The target design stays synthetic-only, metadata-only, and no-oracle. It
uses safe target names, command shapes, field names, counts, safety flags, and
reason-code names only.

## 2. Current State

- The static validator module exists.
- The safe no-write CLI exists.
- The default root CLI validates 29 cases and 116 JSON files.
- The CLI default root, JSON mode, and single-case validation pass.
- Makefile target does not exist.
- Release-quality integration does not exist.
- Artifact body file writing does not exist.
- `--artifact-body-out` does not exist.
- Isolated temp write validation does not exist.

## 3. Proposed Target Name

Candidate target names:

| Candidate | Notes |
| --- | --- |
| `check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures` | Long, but fully aligned with learner-state, frozen policy generation, artifact body, and file writing fixture naming. |
| `check-learner-state-artifact-body-file-writing-fixtures` | Shorter, but loses the frozen policy generation namespace. |
| `check-artifact-body-file-writing-fixtures` | Compact, but too broad for release-quality logs. |
| `check-file-writing-fixtures` | Too vague and likely to collide with future unrelated file-writing checks. |

Recommended:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

Reasons:

- It aligns with the learner-state / frozen policy generation / artifact body
  namespace.
- It is clear that the target validates file writing fixtures.
- It follows existing target naming patterns.
- It will remain understandable if later added to release-quality.

## 4. Proposed Command

Future command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing`

The command should use the human safe summary by default. It should not use
`--json` by default.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures  Validate artifact body file writing fixture contracts`

## 6. Expected Behavior

The future target should:

- run the static/no-write validator CLI on the default fixture root
- exit 0
- emit `mode=fixture_root`
- emit `total_cases=29`
- emit `valid_cases=5`
- emit `invalid_cases=24`
- emit `matched_cases=29`
- emit `mismatched_cases=0`
- emit `input_error_cases=0`
- emit `content_suppressed=true`
- emit `no_raw_rows=true`
- emit `no_logits_dump=true`
- emit `no_private_paths=true`
- emit `synthetic_only_checked=true`
- emit `no_oracle_checked=true`
- emit `path_policy_checked=true`
- emit `body_content_policy_checked=true`
- emit `stdout_body_suppression_checked=true`
- emit `manifest_absence_checked=true`
- emit `file_writing_isolated=false`
- perform no file writing
- create no temp directories
- print no artifact body payload
- print no request, pointer, file write, or expected result bodies
- write no manifest file
- provide no performance evidence

## 7. Output And Logging Safety

Allowed output:

- mode
- validation schema version
- counts
- reason code names and count-only summaries
- safety flags
- safe summary fields

Forbidden output:

- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- `file_write_request` body
- `expected_file_write_result` body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- absolute local paths
- raw learner text
- performance metric body
- GitHub raw logs
- full job output copied into docs

## 8. Makefile Implementation Notes

For the future implementation step:

- Add the target to `.PHONY`.
- Add the help text to `make help`.
- Place it near existing artifact body fixture and artifact body generation
  targets.
- Call the CLI default fixture root.
- Do not use `--json` by default.
- Do not create output files.
- Do not write temp directories.
- Do not call file writing implementation.
- Do not call artifact writer CLI.
- Do not call manifest writer.

## 9. Relation To Existing Targets

- The existing artifact body fixture validator target checks the body
  generation boundary.
- This future file writing fixture validator target checks the
  file-output/path-policy boundary.
- The safe-metadata generation target checks a safe-metadata generation path.
- This target does not overlap with artifact writer runtime.
- This target does not test a manifest writer.
- This target does not prove artifact file writing implementation exists or
  works.

## 10. Release-Quality Staging

- Do not add this target to release-quality in the same step.
- Implement the standalone Makefile target first.
- Then create a docs-only release-quality integration design.
- Then integrate the wrapper.
- Then record a remote/manual status marker after success.
- Keep workflow YAML unchanged unless a later step proves a workflow change is
  necessary.

## 11. Future Tests For Makefile Implementation

Future tests should verify:

- `make help` includes the target.
- The target exits 0.
- Target output includes `total_cases=29`.
- Target output includes `matched_cases=29`.
- Target output includes `input_error_cases=0`.
- Target output includes `file_writing_isolated=false`.
- Target output is body-free.
- No files are created.
- No temp directories are created.
- Wrapper diff is none.
- Workflow diff is none.
- Existing checks pass.

## 12. Docs Safety Policy

Docs should include target names, command shapes, field names, expected
counts, safety flags, and reason-code names only.

Docs must not include raw command output blocks with fixture bodies, JSON body
examples, artifact body payloads, private path examples, raw logs, full job
output, copied log blocks, raw rows, logits, real data, raw learner text,
generated policy bodies, manifest bodies, or performance metric bodies.

## 13. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command in a
consistent way.

After a CLI exists, a Makefile target gives developers a shorter, predictable
entrypoint. It also makes future release-quality integration easier because
the wrapper can call one stable target name.

The target should stay standalone first. Adding it to release-quality in a
separate step keeps failures easier to understand and preserves a clear audit
trail.

Even though this is a no-write target, it matters because it checks the
contracts that will guard future file writing: safe paths, no body leakage,
no manifest writing, no raw rows, no logits, and no private paths.

## 14. What This Does NOT Do

- Does not implement the Makefile target.
- Does not add release-quality integration.
- Does not implement file writing.
- Does not create output files.
- Does not add `--artifact-body-out`.
- Does not run isolated temp write validation.
- Does not write manifests.
- Does not connect artifact writer CLI.
- Does not use real data.
- Does not compute metrics.

## 14a. Step358 Implementation Status

Step358 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

The target runs the safe no-write validator CLI against the default file
writing fixture root. It uses the human summary by default and keeps the
output limited to counts, reason-code names/counts, safety flags, schema
names, and body-free summary fields.

The Makefile implementation adds the target to `.PHONY`, adds the help text,
and places the command near the existing artifact body fixture and generation
targets. It does not add release-quality integration, does not change
workflow YAML, does not change Python code or tests, does not change fixture
JSON, does not write artifact body files, does not create temp output
directories, does not implement `--artifact-body-out`, does not run isolated
temp write validation, does not write manifests, does not connect artifact
writer CLI, does not use real data, and does not compute metrics.

## 15. Next Recommended Steps

- Step359: release-quality integration design.
- Step360: wrapper integration.
- Later: remote/manual Release Quality status marker.
- Later: isolated temp write validation after artifact body file writing
  exists.

## 16. Related Documents

- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Public release checklist](public_release_checklist.md)
