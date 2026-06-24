# Frozen Policy Generation Artifact Body Generation CLI Design

This document designs a future safe command-line interface for the frozen
policy generation artifact body generation API. It is docs-only. It does not
implement the CLI, connect artifact body generation to the artifact writer
CLI, add a Makefile target, change release-quality, write artifact files,
generate manifest bodies, compute metrics, use real data, or claim production
readiness.

## 1. Purpose

The purpose of this document is to define how the artifact body generation API
could later be called from a terminal while preserving the synthetic-only,
metadata-only, no-oracle boundary.

This is not:

- CLI implementation
- artifact writer CLI integration
- Makefile target implementation
- release-quality integration
- artifact file writing
- manifest writer implementation
- manifest body generation
- performance evaluation
- real-data readiness
- production readiness

## 2. Current State

- The artifact body generation API exists in
  `python/learner_state/frozen_policy_generation_artifact_body.py`.
- The artifact body generation unit tests exist.
- The artifact body fixture validator exists.
- The artifact body fixture validator CLI exists.
- The artifact body fixture Makefile target exists.
- Artifact body fixture validation is included in release-quality.
- The artifact body generation CLI does not exist.
- Artifact body file writing does not exist.
- Manifest body generation does not exist.
- Manifest file writing does not exist.

## 3. Proposed Entrypoint

Candidate entrypoints:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body`
- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_cli`

Recommended entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body`

Reasons:

- It connects directly to the existing artifact body generation API module.
- It follows the project style used by nearby safe module CLIs.
- It avoids creating an extra wrapper module before there is a clear need.
- It keeps CLI behavior close to the API that owns the safety audit.

## 4. Proposed Arguments

Minimum future arguments:

- `--request`
- `--pointer`
- `--mode`
- `--json`
- `--help`

`--request` should accept only a synthetic `artifact_body_request.json` path.
The CLI must not print the request body.

`--pointer` should accept only a synthetic
`artifact_writer_result_pointer.json` path. The CLI must not print the pointer
body.

`--mode` should have these initial candidates:

- `suppressed`
- `safe-metadata`

The default mode should be `suppressed`.

`--json` should emit a deterministic, parseable, body-free safe summary. It
must not include artifact body payload content.

`--help` should show usage and exit successfully without reading input files.

## 5. Explicit Non-Goal Arguments

The future CLI should not support these arguments in the initial design:

- `--output`
- `--write-artifact`
- `--write-manifest`
- `--print-body`
- `--include-body`
- `--include-raw`
- `--include-logits`
- `--include-performance`
- `--real-data`

These options would either create files, expose payloads, encourage unsafe
output, or imply unsupported real-data and performance workflows.

## 6. Default Behavior

Default behavior should be equivalent to `--mode suppressed`.

The CLI should:

- require both request and pointer inputs
- call the artifact body generation API
- emit a `summarize_artifact_body_result` style body-free summary
- keep artifact body payload out of stdout and stderr
- write no artifact file
- write no manifest file
- generate no manifest body
- compute no metrics
- use no real data

Even if a body is generated internally in a future mode, default output should
remain summary-only and body-free.

## 7. Safe Metadata Mode Behavior

`--mode safe-metadata` may request safe metadata body generation through the
existing API.

Even in safe metadata mode:

- stdout remains summary-only
- JSON output remains body-free
- `body_status` may be `generated_safe_metadata_body`
- summaries may include safe IDs, status, reason codes, failed checks, safety
  flags, count summary, and file-writing false flags
- artifact body payload must not be printed
- artifact files must not be written
- manifest files must not be written

Safe metadata mode is a body-generation mode, not a body-printing mode.

## 8. Human Output Design

Human output may include:

- mode
- artifact_body_schema_version
- artifact_id
- manifest_id
- body_type
- body_status
- generation_status
- reason_codes
- failed_checks
- safety flags
- count summary
- artifact_file_written=false
- manifest_file_written=false
- safe_summary

Human output must not include:

- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body

## 9. JSON Output Design

JSON output should be:

- deterministic
- parseable
- sorted by key
- summary-only
- body-free

JSON output must not include:

- artifact body payload field
- request body field
- pointer body field
- expected body field
- manifest body field
- generated policy body field
- raw rows field
- logits or probabilities field
- private paths field
- raw learner text field
- performance metric body field

Zero count fields for raw rows, logits, private paths, performance metrics,
request body, pointer body, expected body, and manifest body may be included.

## 10. Exit Code Design

Recommended exit codes:

- `0`: safe generation summary produced
- `2`: usage or input error
- `3`: safety audit fail-closed
- `1`: unexpected internal error

Expected interpretations:

- valid request plus pointer with default suppressed mode exits `0`
- valid request plus pointer with safe metadata mode exits `0`
- missing request exits `2`
- missing pointer exits `2`
- malformed JSON exits `2`
- unsafe payload exits `3`
- unexpected exception exits `1`

Fail-closed invalid content is not a performance failure. It is a safety
boundary result.

## 11. Input Validation

The CLI should require both `--request` and `--pointer`.

Input validation should handle:

- missing request path as usage or input error
- missing pointer path as usage or input error
- malformed JSON as usage or input error
- non-object JSON as usage or input error
- unsupported `--mode` as usage error
- unexpected option as usage error

Unknown request or pointer schema should be treated as input error if the file
cannot be safely interpreted as the intended synthetic input. Unknown artifact
body schema generated internally should fail closed through the safety audit.

Errors must not echo file bodies or payload content.

## 12. No-Body-Leakage Checks For Future CLI Tests

Future CLI tests should verify:

- help exits `0`
- no args exits `2`
- request only exits `2`
- pointer only exits `2`
- unknown mode exits `2`
- unknown option exits `2`
- valid suppressed human output exits `0`
- valid suppressed JSON output exits `0`
- valid safe metadata human output exits `0`
- valid safe metadata JSON output exits `0`
- malformed JSON exits `2`
- unsafe temp payload exits `3`
- stdout and stderr are body-free
- JSON output is parseable
- JSON output is deterministic
- request body is not printed
- pointer body is not printed
- artifact body payload is not printed
- manifest body is not printed
- raw rows are not printed
- logits are not printed
- private paths are not printed
- raw learner text is not printed
- performance metric body is not printed
- output files are not created

## 13. Relation To Existing Artifact Body Fixture Validator CLI

The artifact body fixture validator CLI validates the 18 fixture contracts.
The future generation CLI would generate one safe summary from one synthetic
request and pointer pair.

The validator CLI remains the release-quality target. The generation CLI
should not be added to release-quality until a dedicated CLI implementation,
Makefile target design, runtime smoke design, and release-quality integration
design exist.

The generation CLI does not replace the fixture validator CLI.

## 14. Relation To Artifact Writer CLI

The artifact writer CLI remains body-free. It should not start printing
artifact body payloads as part of this CLI design.

Artifact body generation CLI should remain separate from artifact writer CLI.
Any future artifact writer CLI integration should be designed in a separate
step with its own no-body-leakage checks.

## 15. Relation To Manifest Writer

The future CLI must not generate manifest body content and must not write a
manifest file.

Manifest writer work remains a separate future step. A future manifest may
reference safe artifact body metadata only, not artifact body payload content.

## 16. Future Makefile And Release-Quality Staging

Suggested future staging:

- Step337 artifact body generation CLI implementation
- Step338 artifact body generation Makefile target design
- Step339 Makefile target implementation
- Step340 release-quality integration design
- Step341 wrapper integration
- Step342 remote/manual run record workflow design
- Step343 status marker

Artifact writer CLI integration remains separate from this staging.

## 17. Docs Safety Policy

Docs may include:

- CLI argument names
- safe field names
- exit codes
- high-level behavior
- reason code names
- safety flag names

Docs must not include:

- command output examples
- JSON output examples
- artifact body payload examples
- request body examples
- pointer body examples
- expected result body examples
- raw log examples
- raw learner text
- raw rows
- logits or probability dumps
- private paths
- performance metric bodies

## 18. Beginner-Friendly Explanation

An artifact body generation CLI would be a terminal command for asking the
artifact body generation API to process one synthetic request and one pointer.
The command would not print the artifact body itself by default. Instead, it
would print a small safe summary saying whether generation was suppressed,
safe, or fail-closed.

The CLI design comes after the API because the API owns the core safety
behavior. The CLI should be a thin shell around that behavior, not a second
implementation.

The default should be `suppressed` because the safest terminal behavior is to
avoid body output unless a later mode explicitly requests safe metadata body
generation. Even in safe metadata mode, the CLI should print only the summary
so logs and docs remain public-safe.

File writing and manifest writing are separate because printing a safe summary
is a smaller safety boundary than creating files that may later be shared,
archived, or attached to other workflows.

## 19. What This Does Not Do

This document does not:

- implement the CLI
- write artifact files
- print artifact body payload
- change artifact writer CLI
- add a Makefile target
- integrate release-quality
- change workflow YAML
- change fixture JSON
- use real data
- compute metrics
- claim production readiness

## 20. Step337 Implementation Status

Step337 implements the thin artifact body generation CLI entrypoint in
`python/learner_state/frozen_policy_generation_artifact_body.py`:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body`

The implemented CLI follows this design: `--mode suppressed` remains the
default, `--mode safe-metadata` is summary-only, `--json` emits deterministic
body-free safe metadata, and request/pointer bodies are never printed. The
CLI does not add output-file options, does not write artifact files, does not
generate manifest bodies, does not change the artifact writer CLI, does not
change Makefile or release-quality, does not change workflow YAML, does not
modify fixture JSON, does not use real data, and does not compute metrics.

## 21. Step338 Makefile Target Design Status

Step338 designs a future standalone Makefile target for the implemented CLI:

[Frozen policy generation artifact body generation Makefile target design](frozen_policy_generation_artifact_body_generation_makefile_target_design.md).

The design recommends starting with a default suppressed-mode smoke only. It
does not implement the Makefile target, does not add release-quality
integration, does not change workflow YAML, does not change Python code or
tests, does not change fixture JSON, does not write files, does not generate
manifest bodies, does not use real data, and does not compute metrics.

## 22. Step339 Makefile Target Implementation Status

Step339 implements the standalone default suppressed-mode Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation`

The target is a thin wrapper around this CLI. It does not add a safe-metadata
target, does not add release-quality integration, does not change workflow
YAML, does not change Python code or tests, does not change fixture JSON, does
not write artifact files, does not generate manifest bodies, does not connect
artifact writer CLI, does not use real data, and does not compute metrics.

## 23. Step340 Release-Quality Integration Design Status

Step340 designs a future release-quality integration for the standalone
default suppressed-mode generation target:

[Frozen policy generation artifact body generation release-quality integration design](frozen_policy_generation_artifact_body_generation_release_quality_integration_design.md).

The design keeps this CLI summary-only and body-free. It does not change the
wrapper, workflow YAML, Makefile, Python code or tests, fixture JSON,
safe-metadata target coverage, artifact writer CLI behavior, file writing,
manifest generation, real-data use, or metrics.

## 24. Step341 Release-Quality Wrapper Integration Status

Step341 adds the standalone artifact body generation target to the
release-quality wrapper. The CLI remains default suppressed-mode in the
wrapper, summary-only, and body-free.

Step341 does not change workflow YAML, Makefile, Python code or tests, fixture
JSON, safe-metadata target coverage, artifact writer CLI behavior, file
writing, manifest generation, real-data use, or metrics.

## 25. Step342 Remote Run Record Workflow Design Status

Step342 designs a future public-safe remote/manual Release Quality run record
for the default suppressed-mode artifact body generation CLI smoke:

[Frozen policy generation artifact body generation release-quality remote run record workflow](frozen_policy_generation_artifact_body_generation_release_quality_remote_run_record_workflow.md).

The CLI remains unchanged. The workflow design does not create a status
marker, run GitHub Actions, change workflow YAML, change the release-quality
wrapper, change Makefile, change Python code or tests, change fixture JSON,
add a safe-metadata target, write artifact files, generate manifest bodies,
use real data, or compute metrics.

## 26. Step343 Remote Run Status Marker Status

Step343 creates the public-safe remote/manual Release Quality status marker
for the artifact body generation CLI smoke:

[Learner-state frozen policy generation artifact body generation release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_generation_release_quality_remote_run_status.md).

The CLI remains unchanged. The marker records only body-free safe metadata for
the default suppressed-mode smoke and does not make safe-metadata mode part of
release-quality.

## 27. Step344 Safe-Metadata Makefile Target Design Status

Step344 designs a future standalone Makefile target for this CLI's
safe-metadata mode:

[Frozen policy generation artifact body safe-metadata Makefile target design](frozen_policy_generation_artifact_body_safe_metadata_makefile_target_design.md).

The design keeps the CLI summary-only and body-free. It does not implement a
target, does not add release-quality coverage for safe-metadata mode, does
not change workflow YAML, does not change Makefile, does not change Python
code or tests, does not change fixture JSON, does not print artifact body
payloads, does not write artifact files, does not generate manifest bodies,
does not use real data, and does not compute metrics.

## 28. Step345 Safe-Metadata Makefile Target Implementation Status

Step345 implements the standalone safe-metadata Makefile target for this CLI:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The target runs `--mode safe-metadata` on the existing synthetic
safe-metadata request/pointer pair and emits only the CLI's body-free safe
summary. It is not added to release-quality in this step. Step345 does not
change workflow YAML, Python code or tests, fixture JSON, artifact writer CLI
behavior, artifact file writing, manifest generation, real-data use, or
metrics.

## 29. Step346 Safe-Metadata Release-Quality Integration Design Status

Step346 designs a future release-quality wrapper integration for the
standalone safe-metadata target:

[Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md).

The CLI remains summary-only and body-free. The design does not change the
wrapper, workflow YAML, Makefile, Python code or tests, fixture JSON, artifact
writer CLI behavior, artifact file writing, manifest generation, real-data
use, or metrics.
