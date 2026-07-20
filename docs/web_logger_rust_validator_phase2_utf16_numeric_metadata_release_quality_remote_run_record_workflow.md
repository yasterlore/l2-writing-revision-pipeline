# Rust Validator Phase 2 UTF-16 Numeric Metadata Release Quality Remote/Manual Run Record Workflow

## 1. Title

Rust Validator Phase 2 UTF-16 Numeric Metadata Release Quality Remote/Manual
Run Record Workflow

## 2. Scope

This is a run-record-workflow-design / docs-only Step. It creates no status
marker in this Step, creates no final safety review in this Step, changes no
release-quality wrapper, changes no Makefile, changes no Rust code, changes no
TypeScript code, changes no Python code, changes no tests, changes no fixture
JSON / JSONL, changes no CI workflow, changes no Cargo.toml / Cargo.lock, and
changes no package.json.

This Step changes no validator behavior, schema behavior, replay behavior,
extract / micro_episode behavior, or event durability behavior. It provides no
production readiness proof, no real-data readiness proof, and no model
performance proof.

## 3. Design Status

Step-web-logger-054 accepted the Phase 1 release-quality chain for Web logger
v0.2-style `position_unit` presence / value / schema-version gating. That
accepted boundary remains Phase 1 only.

Step-web-logger-057 implemented Phase 2 UTF-16 numeric metadata validator
behavior. Step-web-logger-059 added the Phase 2 Makefile target. Step-web-
logger-061 integrated that Phase 2 target into the release-quality wrapper.

This document designs the future run-record workflow only. It does not create
a status marker. Phase 2 is release-quality-integrated locally after Step-web-
logger-061, but it is not remote-status-recorded unless future remote metadata
is provided. Phase 2 final safety review remains future work.

## 4. Evidence Hierarchy

Future Step-web-logger-063 should use this evidence hierarchy:

1. Remote GitHub Actions Release Quality run public-safe metadata after
   Step-web-logger-061 wrapper integration.
2. Local/manual `make check-release-quality` summary after Step-web-logger-061
   wrapper integration.
3. Standalone
   `make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
   summary only if full release-quality evidence is unavailable.

Remote GitHub Actions metadata is preferred. Local/manual fallback is allowed
only when remote metadata is unavailable and must be marked with
`local_fallback_used=yes`. If remote metadata is available, the status marker
should mark `local_fallback_used=no`.

Standalone target summary is weaker than full release-quality evidence. Do not
infer missing metadata. Do not copy raw logs, full job output, raw Cargo
output, or full Cargo output into docs.

## 5. Future Status Marker Path

Future Step-web-logger-063 should create:

`docs/status/web_logger_rust_validator_phase2_utf16_numeric_metadata_release_quality_remote_run_status.md`

Do not create that file in Step-web-logger-062.

If a docs/status index update is needed, Step-web-logger-063 may update
`docs/status/README.md` minimally. Step-web-logger-062 only designs this
behavior.

## 6. Public-Safe Metadata To Record In Future Step-web-logger-063

Future status marker should record these fields when public-safe metadata is
available:

- `evidence_source`
- `local_fallback_used`
- `remote_metadata_available`
- `workflow_name`
- `job_name`
- `repository`
- `branch`
- `commit_full_hash`
- `commit_short_hash`
- `runner_version`
- `runner_os`
- `runner_image`
- `runner_image_version`
- `python_version`
- `rust_version`
- `node_version`
- `npm_version`
- `run_start_timestamp`
- `release_quality_script_start_timestamp`
- `rust_validator_phase2_utf16_numeric_check_start_timestamp`
- `release_quality_completed_timestamp`
- `final_release_quality_check_ok_timestamp`
- `approximate_duration_from_runner_start_to_release_quality_ok_seconds`
- `approximate_duration_from_script_start_to_release_quality_ok_seconds`
- `approximate_duration_from_phase2_utf16_numeric_check_start_to_release_quality_ok_seconds`
- `run_status`
- `job_status`
- `release_quality_check_result`
- `final_release_quality_check_ok_observed`
- `artifacts_recorded`
- `raw_logs_stored_in_docs`
- `full_job_output_stored_in_docs`
- `raw_cargo_output_copied_to_docs`
- `full_cargo_output_copied_to_docs`
- `workflow_yaml_changed`
- `run_trigger_type`
- `target_output_seen`

For unavailable fields, use exactly:

`not available from provided public-safe metadata`

Do not infer missing metadata.

## 7. Release-Quality Labels To Record In Future Step-web-logger-063

Future status marker should record whether these labels and commands were
observed:

- `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
- `command: make check-web-logger-rust-validator-position-unit-phase1`
- `release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
- `command: make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
- final `release_quality_check: ok`

Expected relative order:

- Phase 2 label appears after the Phase 1 validator label.
- Phase 2 label appears before
  `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`.
- Existing fixture contract validation label remains before Phase 1 and Phase
  2 validator labels.

Do not infer labels or order that are not shown in public-safe metadata.

## 8. Target Summary To Record In Future Step-web-logger-063

Required target identity:

- `target_command_observed=yes`
- `target_status=pass`
- `target_command=make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
- `underlying_command=cargo test -p kslog_validate position_unit_phase2`
- `crate=kslog_validate`
- `test_filter=position_unit_phase2`
- `phase=Phase 2`
- `policy_scope=utf16_numeric_metadata_validation`
- `summary_only=not applicable for Cargo test output`

Required result summary:

- `focused_test_status=pass`
- `focused_test_count=8`
- `failed_test_count=0`
- `phase2_utf16_numeric_validation_checked=true`
- `doc_len_before_utf16_mismatch_checked=true`
- `doc_len_after_utf16_mismatch_checked=true`
- `start_greater_than_end_checked=true`
- `offset_beyond_utf16_length_checked=true`
- `offset_inside_surrogate_pair_checked=true`
- `invalid_utf16_boundary_checked=true`
- `detectable_byte_index_misuse_boundary_checked=true`
- `phase1_gating_prerequisite_checked=true`
- `shared_utf16_helper_used=true`
- `kslog_validate_depends_on_kslog_replay=false`
- `replay_invoked=false`
- `extract_integration_checked=false`
- `micro_episode_integration_checked=false`
- `typescript_logger_checked=false`
- `hash_compatibility_checked=false`
- `event_durability_checked=false`
- `production_readiness_claimed=false`
- `real_data_readiness_claimed=false`
- `performance_claims_present=false`

Optional public-safe fields if visible:

- `phase1_target_status`
- `phase1_focused_test_count=9`
- `full_validator_test_status`
- `full_validator_test_count=30`
- `schema_utf16_helper_test_status`
- `replay_utf16_compatibility_test_status`
- `workspace_test_status`
- `position_unit_fixture_contract_validator_status`
- `position_unit_fixture_contract_case_count=17`
- `position_unit_fixture_contract_jsonl_record_count=24`
- `position_unit_fixture_contract_matched_cases=17`
- `position_unit_fixture_contract_mismatched_cases=0`
- `final_release_quality_check_ok_observed`

Status-step mutation fields:

- `rust_code_modified_in_status_step=no`
- `rust_tests_modified_in_status_step=no`
- `makefile_modified_in_status_step=no`
- `wrapper_modified_in_status_step=no`
- `fixture_json_modified_in_status_step=no`
- `python_validator_modified_in_status_step=no`

Do not record raw Cargo output, raw test output blocks, raw fixture bodies, raw
source text, selected text, full event payload body, private paths, absolute
paths, real participant data, raw learner text, logits/probabilities, or
performance metric body.

## 9. Critical Safety Note About Raw Cargo Output

Raw local/manual or remote release-quality output may include standard Cargo
output and local or CI paths.

For future status marker safety flags, do not claim that raw full output
contains no absolute paths. Use this safer and accurate boundary:

- `raw_logs_stored_in_docs=no`
- `full_job_output_stored_in_docs=no`
- `raw_cargo_output_copied_to_docs=no`
- `full_cargo_output_copied_to_docs=no`
- `private_path_copied_to_docs=no`
- `absolute_local_path_copied_to_docs=no`

If target or validator tests report public-safe diagnostics, record only
metadata/counts.

## 10. Future Status Marker Template

Future status marker should use these sections:

- Title
- Scope
- Evidence source
- Remote/manual run metadata
- Release-quality labels observed
- Rust validator Phase 2 target summary
- Overall release-quality result
- Safety boundary
- Missing / unavailable metadata
- Relationship to Step-web-logger-061 wrapper integration
- Relationship to Step-web-logger-059 Makefile target
- Relationship to Step-web-logger-057 Phase 2 validator implementation
- Relationship to Step-web-logger-056 shared UTF-16 helper
- Relationship to Step-web-logger-054 Phase 1 final-reviewed boundary
- Relationship to Step-web-logger-031 replay integration
- Relationship to TypeScript logger
- Relationship to SHA-256 hash compatibility
- Relationship to event durability
- Relationship to no-oracle / synthetic-only boundaries
- Failure interpretation
- Non-equivalence cautions
- Non-claims
- Public-safe checklist
- Recommended next step

## 11. Validation Rules For Future Step-web-logger-063 Status Marker

Future status marker should satisfy:

- includes only public-safe metadata
- does not copy raw logs
- does not copy full job output
- does not copy raw Cargo output
- does not copy raw test output blocks
- does not copy raw fixture body
- does not copy full fixture JSON body
- does not copy raw source text
- does not copy selected raw text
- does not copy raw event payload body
- does not include private paths
- does not include absolute local paths
- does not include real participant data
- does not include raw learner text
- does not include logits / probabilities
- does not include performance metric body
- records unavailable metadata as
  `not available from provided public-safe metadata`
- does not infer missing metadata
- does not claim production readiness
- does not claim real-data readiness
- does not claim model performance
- does not claim replay correctness
- does not claim extract / micro_episode integration
- does not claim TypeScript/Rust hash compatibility
- does not claim event durability implementation

## 12. Handling Missing Metadata

Missing workflow name, run status, job status, trigger type, artifacts, or
workflow YAML status should not be guessed. Use:

`not available from provided public-safe metadata`

If the Phase 2 label is not visible in public-safe metadata, record it as not
available rather than assuming. If final `release_quality_check: ok` is not
visible, record it as not available rather than assuming.

If only local/manual summary is available, mark `local_fallback_used=yes`. If
remote metadata is available, mark `local_fallback_used=no`.

Missing metadata does not imply failure by itself. It means the evidence
boundary remains limited.

## 13. Relationship To Step-web-logger-061 Wrapper Integration

Step-web-logger-061 integrated the Phase 2 Makefile target into the
release-quality wrapper. Step-web-logger-062 only designs run record workflow
and does not revise the wrapper.

Future Step-web-logger-063 should record whether the Phase 2 label is observed
in remote/manual release-quality output. Future status marker evidence does
not itself prove replay correctness or TypeScript compatibility.

## 14. Relationship To Step-web-logger-059 Makefile Target

Step-web-logger-059 added
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.
The Makefile target command runs
`cargo test -p kslog_validate position_unit_phase2`.

The target validates focused Rust validator Phase 2 UTF-16 numeric metadata
tests only. Step-web-logger-062 does not modify Makefile.

## 15. Relationship To Step-web-logger-057 Validator Implementation

Step-web-logger-057 implemented Rust validator Phase 2 UTF-16 numeric metadata
validation. Release-quality status evidence means focused tests ran through
the wrapper.

It does not mean replay correctness, extract / micro_episode integration, or
TypeScript compatibility. Step-web-logger-062 does not modify Rust validator
code or tests.

## 16. Relationship To Step-web-logger-056 Shared UTF-16 Helper

Step-web-logger-056 extracted `kslog_schema::utf16_offsets`. Phase 2 validator
uses the shared helper. Future status marker should record shared helper usage
as metadata.

Shared helper extraction is not equivalent to validator Phase 2
release-quality evidence.

## 17. Relationship To Step-web-logger-054 Phase 1 Final-Reviewed Boundary

Step-web-logger-054 accepted the Phase 1 release-quality chain. Phase 2
release-quality chain is newer and separate. Phase 2 pass should not broaden
the Phase 1 accepted boundary.

Future final safety review should keep Phase 1 and Phase 2 boundaries
separate.

## 18. Relationship To Step-web-logger-031 Replay Integration

Step-web-logger-031 replay integration remains separate. Rust validator Phase
2 target does not call replay. Replay correctness does not prove validator
policy. Validator Phase 2 pass does not prove replay correctness.

## 19. Relationship To TypeScript Logger

Rust validator Phase 2 target does not modify TypeScript. TypeScript emission
of explicit `position_unit=utf16_code_unit` and required text metadata remains
future work if not already implemented. TypeScript/Rust compatibility remains
separate.

## 20. Relationship To SHA-256 Hash Compatibility

Rust validator Phase 2 target does not implement a SHA-256 helper. It does not
run TypeScript/Rust hash vector checks. It does not prove TypeScript/Rust hash
equality.

## 21. Relationship To Event Durability

Rust validator Phase 2 target does not implement event durability. Queue /
IndexedDB / ack / retry / dedup remain unimplemented. Server-side idempotency /
event_id dedup remains unimplemented. Ordering / delivery durability remains
open.

## 22. Relationship To No-Oracle And Synthetic-Only Boundaries

Tests use synthetic fixtures. No real participant data is used. No raw learner
text is used. No final_text / observed_after_text / gold labels / post-hoc
annotation are used. No test-set tuning is introduced. No model performance
validation is performed. No-oracle constraints are not relaxed.

## 23. Failure Interpretation

Missing remote metadata does not imply failure. Local/manual fallback does not
equal remote-status-recorded.

Target pass means focused Rust validator Phase 2 tests passed. It does not
prove replay correctness, extract integration, micro_episode integration,
TypeScript compatibility, Rust SHA-256 compatibility, TypeScript logger hash
correctness, or event durability.

Release-quality success is not production readiness. Synthetic-only pass is
not real-data readiness.

## 24. Non-Equivalence Cautions

- workflow design is not status marker
- status marker is not raw evidence
- status marker is not full job output
- release-quality pass is not production readiness
- synthetic-only pass is not real-data readiness
- Rust validator Phase 2 pass is not replay correctness
- Rust validator Phase 2 pass is not extract integration
- Rust validator Phase 2 pass is not micro_episode integration
- Rust validator Phase 2 pass is not TypeScript compatibility
- Rust validator Phase 2 pass is not Rust SHA-256 compatibility
- Rust validator Phase 2 pass is not TypeScript logger hash correctness
- Rust validator Phase 2 pass is not event durability
- future status marker does not authorize real data collection

## 25. Non-Claims

This design does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, hash compatibility
implementation completion, TypeScript/Rust vector check implementation,
TypeScript/Rust hash equality, event durability implementation, data
collection readiness, or deployment readiness.

## 26. Public-Safe Checklist

Future status marker should include checklist items:

- no raw logs
- no full job output
- no copied GitHub log blocks
- no raw Cargo output copied
- no full Cargo output copied
- no raw test output blocks copied
- no raw fixture body
- no full fixture JSON body
- no raw source text
- no raw selected text
- no raw event payload body
- no private paths copied
- no absolute local paths copied
- no raw learner text
- no real participant data
- no logits / probabilities
- no performance metric body
- no performance claims
- no production readiness claims
- no real-data readiness claims
- no replay correctness claims
- no extract / micro_episode integration claims
- no TypeScript/Rust compatibility claims
- no event durability claims

## 27. Future Staging

Recommended future steps:

- Step-web-logger-063: Rust validator Phase 2 UTF-16 numeric metadata
  release-quality status marker
- Step-web-logger-064: Rust validator Phase 2 UTF-16 numeric metadata
  release-quality final safety review

Later separate chains:

- `kslog_extract` integration
- `kslog_micro_episode` integration
- TypeScript logger explicit `position_unit` emission and metadata
  compatibility review
- Rust SHA-256 helper
- TypeScript SHA-256 helper
- TypeScript/Rust vector checks
- event durability queue / IndexedDB / ack / retry / dedup

Do not recommend moving directly to real data collection.

## 28. Recommended Next Codex Step

Recommended:

`Step-web-logger-063: Rust validator Phase 2 UTF-16 numeric metadata release-quality status marker`

Step-web-logger-063 should be status-marker-only / docs-only. It should use
remote GitHub Actions metadata if available and local/manual fallback only if
remote metadata is unavailable. It should not alter wrapper, Makefile, Rust /
TypeScript / Python code, tests, fixture JSON, or workflow. It should not
claim replay correctness, extract / micro_episode integration, TypeScript/Rust
compatibility, production readiness, or real-data readiness.
