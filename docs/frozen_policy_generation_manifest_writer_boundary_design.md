# Frozen Policy Generation Manifest Writer Boundary Design

## 1. Purpose

This document fixes the boundary for a future frozen policy generation
manifest writer before any implementation work starts.

It is a docs-only boundary design. It is not an implementation, fixture
creation, validator implementation, release-quality integration, performance
evaluation, real-data readiness claim, or production readiness claim.

The design is synthetic-only, metadata-only, and no-oracle. It describes what
a future manifest writer may summarize, what it must reject or suppress, how
future output paths should be constrained, and how future fixture, validator,
Makefile, release-quality, and remote-marker steps should be staged.

## 2. Current State

- artifact writer metadata-only runtime exists
- artifact body generation exists
- artifact body safe-metadata file writing exists
- artifact body isolated write validation exists and is tracked by
  release-quality
- manifest metadata IDs exist in current summaries
- manifest body remains suppressed
- manifest file writing is not implemented
- artifact writer CLI integration for manifest writing is not implemented
- Step377 records a public-safe remote/manual Release Quality status marker
  for isolated write validation, but that marker is not manifest writer
  evidence

## 3. Manifest Writer Role

The future manifest writer should bundle metadata about:

- artifact identity
- artifact body identity
- validation references
- safety flags
- count summaries
- safe relative output-path availability
- related release-quality or status-marker references

It must not include generated policy bodies, artifact body payloads, request
bodies, pointer bodies, expected-result bodies, raw rows, logits, learner
text, private paths, absolute paths, performance claims, or production
readiness claims.

The manifest should be a safe metadata index. It should not become a payload
container.

## 4. Allowed Manifest Fields

Future manifests may use field names such as:

- `schema_version`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `writer_version`
- `generation_version`
- `validation_reference_ids`
- `artifact_body_status`
- `artifact_file_written`
- `artifact_body_output_path_available`
- `artifact_body_output_path_safe_relative`
- `manifest_file_written`
- `manifest_body_available`
- `safety_flags`
- `count_summary`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `created_by`
- `created_at_policy`
- `source_summary_ids`
- `release_quality_reference_ids`
- `optional_status_marker_ids`

This list is a field-name boundary, not a manifest body example.

## 5. Forbidden Manifest Fields / Content

Future manifest writer behavior must forbid:

- raw learner text
- raw events
- revision event rows
- micro episode raw rows
- `final_text`
- `observed_after_text`
- gold labels
- expected action payload
- scoring feedback payload
- logits
- probabilities
- model scores
- performance metrics as proof
- generated policy body
- frozen policy body
- artifact body payload
- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- expected result body
- `isolated_write_request` body
- `case_metadata` body
- manifest body nested inside manifest
- private paths
- absolute local paths
- absolute temp paths
- cloud/local user paths
- raw GitHub logs
- full job outputs
- screenshots of logs
- real participant identifiers
- production data references

The validator and CLI summary should treat any of these as fail-closed or
input-error conditions depending on where the violation is detected.

## 6. Output Path Policy

The default should be no manifest file writing.

Future manifest file writing should require an explicit output option. The
output path should be a safe relative path only, resolved under a dedicated
synthetic/temp root such as:

- `tmp/frozen_policy_generation_manifest/`

Future implementations should reject:

- absolute paths
- home paths
- parent traversal
- cloud/private markers
- hidden private directories
- unsafe filename characters
- non-`.json` extension
- overwrite attempts unless an explicit safe overwrite policy exists

Summary output must not expose an absolute resolved path. If a manifest output
path appears in a summary, it should be safe-relative only.

## 7. CLI / API Boundary For Future Implementation

Proposed future module:

- `learner_state.frozen_policy_generation_manifest_writer`

Proposed future CLI:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`

Potential future arguments:

- `--artifact-result`
- `--artifact-body-result`
- `--manifest-out`
- `--json`
- `--help`

This step does not implement the module, CLI, arguments, manifest body
generation, manifest file writing, or artifact writer CLI integration.

## 8. Future Fixture Strategy

Proposed future fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/`

Potential valid cases:

- `metadata_only_manifest_no_file`
- `safe_relative_manifest_file`
- `manifest_with_artifact_body_reference`
- `manifest_with_release_quality_reference`

Potential invalid cases:

- `generated_policy_body_leakage`
- `artifact_body_payload_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_output`
- `parent_traversal_output`
- `manifest_body_nesting`
- `performance_claim_body`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `unknown_schema_version`

This step does not create fixture JSON.

## 9. Future Validator Strategy

Proposed future module:

- `learner_state.frozen_policy_generation_manifest_writer_validation`

Proposed checks:

- schema version
- allowed keys only
- forbidden field scan
- no raw rows
- no logits
- no private paths
- no absolute paths
- no generated policy body
- no artifact body payload
- no nested manifest body
- notices present
- count summary present
- safety flags present
- output path policy
- no overwrite by default
- summary-only output

The future validator should emit safe metadata summaries only. It should not
print manifest bodies, fixture JSON bodies, artifact body payloads, generated
policy bodies, raw rows, logits, private paths, absolute paths, or raw learner
text.

## 10. Relation To Artifact Body Isolated Write Validation

Artifact body isolated write validation checks artifact body file writing only.

The manifest writer will be separate. Manifest writer success must not be
inferred from isolated write validation success. The Step377 remote/manual
status marker improves traceability for isolated write validation only.

The manifest writer needs its own fixture contract, fixture JSON, validator,
implementation, standalone target, release-quality integration, and remote
status marker steps.

## 11. Release-Quality Staging Plan

Recommended staging:

- Step379: manifest writer fixture contract design
- Step380: manifest writer fixture JSON creation
- Step381: manifest writer validator design or implementation
- Step382: manifest writer implementation
- Step383: Makefile target design
- Step384: Makefile target implementation
- Step385: release-quality integration design
- Step386: wrapper integration
- Step387: remote/manual status marker design
- Step388: remote/manual status marker

Release-quality integration should wait until fixture validation and safe
summary behavior are stable.

## 12. Safety Interpretation

The future manifest writer should start as metadata-only.

Success would mean metadata manifest safety only. It would not mean
production artifact management, real-data readiness, model performance,
learner-state estimator correctness, calibration quality, or selective
prediction correctness.

## 13. Beginner-Friendly Explanation

A manifest is a safe index of what artifact metadata exists and how it relates
to other safe metadata. It is like a table of contents for artifact metadata.

The manifest is separate from the artifact body because the artifact body is
the payload-like object. A manifest should point to safe metadata and status,
not carry the body itself.

Bodies are excluded because they are easier to accidentally turn into raw
content, generated policy content, request content, or private data. Keeping
the manifest metadata-only reduces that risk.

Path policy is required because file writing can accidentally overwrite files
or leak local path details. Safe relative paths under a dedicated temp root
make later smoke tests and cleanup easier to reason about.

Release-quality is staged because each boundary should become stable before
it is added to the wrapper. That keeps future failures interpretable.

## 14. Docs Safety Policy

Docs for this area should include only field names, target names, command
shapes, case IDs, counts, and safety policy.

Docs must not include raw logs, full job output, copied log blocks,
screenshots containing raw logs, JSON body examples, manifest body examples,
artifact body payload examples, private path examples, raw rows, logits, raw
learner text, real participant data, or performance metric bodies.

## 15. What This Does Not Do

- does not implement manifest writer
- does not create fixtures
- does not implement validator
- does not change CLI
- does not change wrapper
- does not change workflow
- does not change Makefile
- does not change Python code/tests
- does not change fixture JSON
- does not use real data
- does not compute metrics
- does not prove production readiness

## 16. Next Recommended Steps

- design the manifest writer fixture contract
- create synthetic metadata-only fixture JSON
- implement manifest writer validation
- implement the metadata-only manifest writer
- design and implement a standalone Makefile target
- design and integrate release-quality wrapper coverage
- create a public-safe remote/manual status marker after successful remote
  coverage

## 17. Step379 Fixture Contract Design Status

Step379 adds the docs-only fixture contract design:

[Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md).

The fixture contract fixes the future fixture root, case directory structure,
schema names, field names, valid/invalid case taxonomy, expected fixture
counts, path policy, content policy, validator phases, and future staging.
It does not create fixture JSON, implement a manifest writer, implement a
validator, write manifest files, change Makefile, change the wrapper, change
workflow YAML, change Python code/tests, change fixture JSON, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 18. Related Documents

- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body isolated write release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
