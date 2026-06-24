# Frozen Policy Generation Artifact Body File Writing Design

## 1. Purpose

This document designs a future artifact body file writing boundary for frozen
policy generation.

It is a docs-only design. It does not implement file writing, does not add a
CLI output option, does not implement a manifest writer, does not connect the
artifact writer CLI, does not add release-quality integration, does not
evaluate performance, and does not claim real-data or production readiness.

The design keeps the first writable artifact body path synthetic-only,
metadata-only, and no-oracle. It is limited to safe metadata body content and
must not include learner text, raw rows, logits, private paths, performance
metric bodies, request bodies, pointer bodies, expected-result bodies,
generated policy bodies, frozen policy bodies, or manifest bodies.

## 2. Current State

- The artifact body generation API exists.
- The artifact body generation CLI exists.
- Suppressed and safe-metadata CLI modes exist.
- Suppressed and safe-metadata Makefile targets exist.
- Both Makefile targets are included in release-quality.
- Remote/manual Release Quality status markers exist for the suppressed and
  safe-metadata smoke paths.
- Artifact body file writing does not exist.
- Manifest body generation does not exist.
- Manifest file writing does not exist.
- Artifact writer CLI integration does not exist.

## 3. File Writing Scope

Initial file writing should target only safe metadata bodies.

- Suppressed mode should not write a body file.
- `generated_safe_metadata_body` should be the only write candidate.
- `suppressed_metadata_only` should remain summary-only and no-file.
- `fail_closed` results should never write a body file.
- Unsafe audit results should never write a body file.
- Manifest files should not be written by this boundary.
- Artifact writer request, pointer, and expected-result bodies should not be
  written by this boundary.

This keeps the first file-writing surface small: one safe body status, one
explicit output option, no manifest writing, and no writer CLI coupling.

## 4. Allowed Artifact Body File Content

The future file may contain only safe metadata fields such as:

- `artifact_body_schema_version`
- `artifact_body_id`
- `artifact_id`
- `manifest_id`
- `writer_version`
- `body_status`
- `body_type`
- `synthetic_only_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `allowed_sections`
- `validation_reference_ids`
- safety flags
- count summary
- safe metadata field names
- file writing policy summary

These fields are identifiers, notices, field names, flags, and counts. They
are not learner content, request payloads, policy payloads, logs, or model
outputs.

## 5. Forbidden Artifact Body File Content

The future file must not contain:

- raw learner text
- raw rows
- raw event rows
- revision event rows
- micro episode rows
- `final_text`
- `observed_after_text`
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

The writer should treat any such content as a fail-closed condition rather
than trying to partially redact a body after the fact.

## 6. Output Path Policy

The default should remain no file writing.

Future file writing should require an explicit output path. That path should
be relative to a controlled safe output root. The path policy should reject:

- absolute local paths
- home directory paths
- parent traversal
- private cloud or local sync path markers
- existing file overwrite unless a later explicit overwrite policy exists
- output paths that would reveal private filesystem structure in summaries

An initial implementation should probably use a controlled temporary output
root for tests only. Production or research output locations remain a future
design problem and should not be inferred from this document.

## 7. Proposed Future CLI Option

Candidate names:

- `--write-body`
- `--output-body`
- `--artifact-body-out`

Recommended name: `--artifact-body-out`.

Reasoning:

- It clearly names artifact body file output.
- It is easier to distinguish from artifact file output and manifest file
  output.
- It signals file output rather than stdout printing.

This option is not implemented in this step.

## 8. Proposed Write Behavior

Future behavior should be:

- Write only when `--artifact-body-out <relative-safe-path>` is provided.
- Allow writing only with `--mode safe-metadata`.
- Treat suppressed mode with an output path as a usage error.
- Write nothing when generation returns `fail_closed`.
- Write nothing when the body safety audit fails.
- Print only a body-free summary on stdout/stderr.
- Allow the summary to report `artifact_file_written=true` after a successful
  write.
- Allow only a safe relative output path in the summary.
- Keep `manifest_file_written=false`.

The CLI should never print the artifact body payload, even when writing the
file succeeds.

## 9. Proposed Result Summary Fields

Future summaries may include:

- `artifact_file_written`
- `artifact_body_output_path_available`
- `artifact_body_output_path`
- `artifact_body_output_path_safety_checked`
- `artifact_body_write_policy`
- `manifest_file_written=false`
- `manifest_body_generated=false`

The summary must not include private paths, absolute paths, request bodies,
pointer bodies, expected bodies, manifest bodies, generated policy bodies, or
artifact body payload content.

## 10. Fail-Closed Behavior

Future implementation should fail closed for:

- unsafe output path
- absolute path
- parent traversal
- private path marker
- suppressed mode with an output path
- `fail_closed` generation result
- unsafe body audit
- missing synthetic-only notice
- missing no-oracle notice
- forbidden count greater than zero
- attempt to write a manifest
- attempt to write generated policy body content
- attempt to include raw text
- overwrite attempt without an explicit policy

Fail-closed summaries should report safe reason-code names and failed check
names only. They should not echo the unsafe path if it is private, and should
not echo any forbidden payload.

## 11. Tests For Future Implementation

Future tests should cover:

- no output path means no file is written
- safe-metadata mode with a safe relative output path writes a file
- suppressed mode with an output path returns a usage error
- `fail_closed` generation result with an output path writes no file
- absolute output path fails closed
- parent traversal fails closed
- private path marker fails closed
- body file is parseable by structured tooling
- body file contains only allowed keys
- body file includes synthetic-only, no-oracle, and non-proof notices
- body file has no raw text
- body file has no rows
- body file has no logits
- body file has no private paths
- body file has no performance metric body
- stdout summary does not include body payload
- manifest file is not written
- existing files are not overwritten without a future explicit policy
- existing CLI behavior is unchanged when no output option is provided

Tests should use only synthetic metadata fixtures and controlled temporary
paths.

## 12. Relation To Manifest Writer

Artifact body file writing does not write a manifest.

The manifest writer remains a separate future design. A later manifest may
reference safe artifact body file metadata, but this design does not generate
manifest bodies and does not write manifest files. Artifact body file writing
success is not manifest generation success.

## 13. Relation To Artifact Writer CLI

The artifact writer CLI remains body-free.

Artifact body generation CLI file writing should remain separate at first.
Integration into the artifact writer CLI requires a separate design because
it would change the writer surface, runtime target interpretation, and
release-quality safety review.

## 14. Relation To Release-Quality

File writing should not be added to release-quality initially.

Recommended staging:

- Local API and CLI tests first.
- Standalone target design only after the file-writing boundary is stable.
- Standalone target implementation after fixture and path-policy coverage.
- Release-quality integration only after a separate integration design.
- Remote status marker only after wrapper integration and remote/manual
  success.

The current suppressed and safe-metadata release-quality smoke paths should
remain summary-only and body-free.

## 15. Docs Safety Policy

Docs should include only safe field names, option names, target names, and
policies.

Docs must not include artifact body examples, request or pointer body
examples, raw logs, full job output, private path examples, generated policy
bodies, manifest bodies, raw rows, logits, raw learner text, real participant
data, or performance metric bodies.

## 16. Beginner-Friendly Explanation

File writing has been avoided so far because writing a body creates a new
place where sensitive content could accidentally persist. The existing CLI
therefore returns only a safe summary.

Safe-metadata mode is the first reasonable candidate for file writing because
it is already designed to carry identifiers, notices, flags, counts, and
field names rather than learner content or model output. Suppressed mode has
no body to write.

Even when a safe metadata body is written to a file, stdout should remain
summary-only. Terminal output and CI logs are easier to copy accidentally, so
they should not become a body inspection surface.

Manifest writing is separate because a manifest has a different contract: it
describes files and references. That needs its own suppression rules, path
rules, and audit checks.

Release-quality should not include file writing immediately because the file
surface needs local tests, fixture coverage, and path-policy validation first.

## 17. What This Does NOT Do

- Does not implement file writing.
- Does not add a CLI option.
- Does not write artifact body files.
- Does not write manifest files.
- Does not print artifact body payloads.
- Does not change the artifact writer CLI.
- Does not change workflow YAML.
- Does not change the release-quality wrapper.
- Does not change Makefile.
- Does not change Python code or tests.
- Does not change fixture JSON.
- Does not use real data.
- Does not compute metrics.
- Does not prove production readiness.

## 18. Next Recommended Steps

- Step351: file writing fixture and path-policy design.
- Step352: file writing fixture JSON creation.
- Step353: file writing fixture validator design or implementation.
- Step354: CLI file writing implementation.
- Later: standalone Makefile target design.
- Later: release-quality integration design.
- Later: remote/manual run record workflow and status marker.

Manifest writer design and artifact writer CLI integration should remain
separate tracks.

## 19. Step351 Fixture And Path-Policy Design Status

Step351 designs the future fixture root, case names, path-policy checks,
content-policy checks, expected result schema, and validator staging for
artifact body file writing:

[Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md).

The design does not create fixture JSON, does not implement file writing,
does not add a CLI option, does not write artifacts or manifests, does not
connect artifact writer CLI, does not change release-quality, does not use
real data, and does not compute metrics.

## 20. Step352 Fixture Creation Status

Step352 creates the synthetic-only metadata fixture root for future artifact
body file writing validation:

[Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md).

The fixture root has 29 cases and 116 JSON files. It is a contract fixture
root only; it does not implement writing, does not add `--artifact-body-out`,
does not write manifests, does not connect artifact writer CLI, does not
change release-quality, does not use real data, and does not compute metrics.

## 21. Related Documents

- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact body generation CLI design](frozen_policy_generation_artifact_body_generation_cli_design.md)
- [Frozen policy generation artifact body safe-metadata Makefile target design](frozen_policy_generation_artifact_body_safe_metadata_makefile_target_design.md)
- [Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md)
- [Learner-state frozen policy generation artifact body safe-metadata release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Public release checklist](public_release_checklist.md)
