# Frozen Policy Generation Manifest Writer Runtime File Writing Smoke Makefile Target Design

## 1. Purpose

This document fixes the docs-only design for a future standalone Makefile
target that smoke-tests manifest writer metadata-only runtime file writing.

This is a Makefile target design only. It does not implement the Makefile
target, integrate release-quality, change workflow YAML, change runtime code,
change Python tests, change fixtures JSON, connect artifact writer CLI, run
artifact body generation CLI, generate manifest bodies, compute metrics, use
real data, or claim production readiness.

## 2. Current State

- Runtime file writing exists from Step441.
- `--manifest-out` exists.
- `--allow-overwrite` exists.
- The default no-file runtime remains unchanged.
- Focused runtime file writing tests exist.
- The production file writing fixture validator exists and is included in
  release-quality.
- The runtime file writing smoke Makefile target does not exist.
- Runtime file writing release-quality integration does not exist.
- Artifact writer CLI integration does not exist.

## 3. Target Name

Future target name:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing`

## 4. Target Command

The target should be a narrow smoke wrapper around the existing manifest writer
runtime. It should use the existing synthetic metadata-only runtime fixture
inputs and write only to a target-owned smoke subdirectory under the controlled
manifest output root.

Recommended future command sequence:

```bash
rm -rf tmp/frozen_policy_generation_manifest/smoke
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer \
  --request tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/manifest_writer_request.json \
  --artifact-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_writer_result_pointer.json \
  --artifact-body-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_body_generation_result_pointer.json \
  --manifest-out smoke/manifest.json
python3 -c 'exec("""import json
import pathlib
import sys
path = pathlib.Path("tmp/frozen_policy_generation_manifest/smoke/manifest.json")
forbidden = {"manifest_body", "manifest_json_body", "artifact_body_payload", "generated_policy_body", "request_body", "pointer_body", "expected_body", "raw_rows", "logits", "probabilities", "private_path", "absolute_path", "raw_learner_text", "final_text", "observed_after_text", "gold_label", "scoring_feedback", "real_participant_data", "performance_metric_body"}
data = json.loads(path.read_text(encoding="utf-8"))
seen = set()
stack = [data]
while stack:
    item = stack.pop()
    if isinstance(item, dict):
        seen.update(str(key) for key in item)
        stack.extend(item.values())
    elif isinstance(item, list):
        stack.extend(item)
sys.exit(1 if forbidden & seen else 0)
""")'
rm -rf tmp/frozen_policy_generation_manifest/smoke
test ! -e tmp/frozen_policy_generation_manifest/smoke
```

The target should not pass `--allow-overwrite` by default. Deterministic rerun
behavior should come from deleting the target-owned smoke directory before the
runtime command. This keeps the smoke close to the default overwrite policy:
existing outputs are not silently overwritten unless a future separate target
explicitly tests overwrite behavior.

If the inline Python check becomes too unwieldy during implementation, a small
dedicated helper script or module may be designed separately. That helper
would still need to emit only body-free metadata and must not print the written
file body.

## 5. Help Text

Future `make help` text:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing  Smoke test manifest writer metadata-only runtime file writing`

## 6. Expected Target Output

The target output should remain body-free and count-only. The runtime summary
should include:

- `mode=manifest_writer`
- `result_schema_version=learner_state_frozen_policy_generation_manifest_writer_result_v0.1`
- `writer_status=pass`
- `manifest_writer_mode=metadata_only_file`
- `runtime_writer_executed=true`
- `manifest_file_written=true`
- `written_file_count=1`
- `manifest_output_path_available=true`
- `manifest_body_available=false`
- `manifest_body_suppressed=true`
- `file_writing_checked=true`
- `output_path_safety_checked=true`
- `content_policy_checked=true`
- `no_manifest_body=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `release_quality_ready=false`
- `safe_summary=metadata_only_manifest_writer_result`

The target must not print the written file body or the absolute resolved output
path.

## 7. Written File Validation

The future target should verify:

- the written file exists during smoke validation
- the written file is parseable JSON
- the written file contains only metadata-safe fields
- no manifest body is present
- no artifact body payload is present
- no generated policy body is present
- no request, pointer, or expected body is present
- no raw rows are present
- no logits or probabilities are present
- no private paths are present
- no absolute path values are present
- no raw learner text is present
- no `final_text`, `observed_after_text`, or `gold_label` is present
- no scoring feedback is present
- no performance metric body is present
- no real participant data is present

The validation should inspect field names and safe metadata values only. It
must not print or copy the written JSON body into logs or docs.

## 8. Cleanup Policy

- Remove `tmp/frozen_policy_generation_manifest/smoke` before the runtime
  command.
- Remove `tmp/frozen_policy_generation_manifest/smoke` after written-file
  validation.
- Final residue under `tmp/frozen_policy_generation_manifest/smoke` must be 0.
- The target must not delete unrelated output outside its own `smoke`
  subdirectory.
- The target must not require pre-existing output files.

## 9. Expected Failure Behavior

The future target should fail if:

- the runtime exits nonzero
- `manifest_file_written` is not true
- `written_file_count` is not 1
- the written file is missing
- the written file is malformed JSON
- the written file contains a forbidden field or value
- stdout or stderr contains the written file body
- stdout or stderr contains an absolute resolved output path
- the output path escapes the safe root
- cleanup fails
- smoke residue remains
- artifact writer CLI is invoked unexpectedly
- artifact body generation CLI is invoked unexpectedly

## 10. Relation To Existing No-File Runtime Smoke

The existing runtime smoke target checks the default metadata-only no-file
runtime behavior.

The future runtime file writing smoke target should check only the opt-in
`metadata_only_file` behavior. Both targets should remain separate because
they guard different runtime modes.

## 11. Relation To Production Fixture Validator

The production file writing fixture validator is static contract validation.
It does not write files.

The future runtime file writing smoke target will actually write one
metadata-only file under the controlled smoke path, parse it, scan it, and
remove it. This is runtime smoke evidence, not production readiness evidence.

## 12. Relation To Isolated Write Validation

Isolated write validation writes inside a validator-owned temporary isolated
root. The future runtime file writing smoke target writes inside a
project-controlled smoke path under the controlled manifest output root.

Both are separate safety layers. Isolated validation remains harness-level
validation, while the future smoke target checks the runtime path introduced
in Step441.

## 13. Relation To Release-Quality

The intended staging is:

- standalone Makefile target first
- release-quality integration design later
- release-quality wrapper integration later
- remote/manual run record workflow later
- remote status marker later

This Step442 design does not add the target to release-quality.

## 14. Docs Safety Policy

Docs may include:

- command names
- the safe relative smoke path
- field names
- count names
- flag names
- policy names

Docs must not include:

- JSON body examples
- written output examples
- raw logs
- full job output
- fixture JSON bodies
- request, pointer, or expected bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw rows
- logits
- private path examples
- absolute path examples
- raw learner text
- real participant data

## 15. Future Implementation Tests

Future Step443 should verify:

- `make help` shows the target
- the target exits 0
- the written file exists during smoke validation and is removed afterward
- output summary says `manifest_file_written=true`
- output summary says `written_file_count=1`
- stdout and stderr are body-free
- public output contains no absolute output path
- forbidden field scan passes
- smoke residue is 0
- Makefile diff is the only implementation diff outside docs
- release-quality wrapper diff is empty
- workflow diff is empty
- Python code/tests diff is empty
- fixtures JSON diff is empty

## 16. What This Does Not Do

This Step442 design does not:

- implement the Makefile target
- integrate release-quality
- modify workflow YAML
- modify runtime code
- modify Python tests
- modify fixtures JSON
- connect artifact writer CLI
- call artifact body generation CLI
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness

## 17. Next Recommended Steps

- Step443 Makefile target implementation
- Step444 release-quality runtime integration design
- Step445 wrapper integration
- Step446 remote/manual run record workflow design
- Step447 remote status marker
- artifact writer CLI integration remains separate

## 18. Related Documents

- [Frozen policy generation manifest writer runtime file writing implementation plan](frozen_policy_generation_manifest_writer_runtime_file_writing_implementation_plan.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Frozen policy generation manifest writer production file writing design](frozen_policy_generation_manifest_writer_production_file_writing_design.md)
- [Frozen policy generation manifest writer production file writing fixture validator design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_validator_design.md)
