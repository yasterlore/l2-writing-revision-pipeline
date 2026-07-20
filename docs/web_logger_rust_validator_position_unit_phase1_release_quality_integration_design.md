# Rust Validator Position Unit Phase 1 Release Quality Integration Design

## 1. Title

Rust Validator Position Unit Phase 1 Release Quality Integration Design

## 2. Scope

This is a release-quality-integration-design / docs-only step.

This step makes no release-quality wrapper changes, no Makefile changes, no
Rust code changes, no TypeScript code changes, no Python code changes, no test
changes, no fixture JSON changes, no CI workflow changes, no Cargo.toml /
Cargo.lock changes, and no package.json changes.

This step also makes no validator behavior changes, no schema behavior
changes, no replay behavior changes, no extract / micro_episode behavior
changes, no event durability implementation, no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-043 accepted the fixture contract validation boundary for the
fixed 17-case synthetic Web logger position_unit fixture matrix.

Step-web-logger-045 implemented the Rust schema field and parser/accessor
boundary for `position_unit`.

Step-web-logger-047 implemented Rust validator Phase 1 `position_unit`
enforcement for presence, value, and schema-version gating.

Step-web-logger-049 added the focused Makefile target
`check-web-logger-rust-validator-position-unit-phase1`.

This document designs release-quality integration only. It does not modify the
wrapper, does not add a status marker, and does not implement Phase 2 UTF-16
numeric metadata validation.

## 4. Current Makefile Target Review

The current target is `check-web-logger-rust-validator-position-unit-phase1`.

Help text:

`Run Rust validator position_unit Phase 1 policy tests`

Command:

`cargo test -p kslog_validate position_unit_phase1`

Step-web-logger-059 corrects this command from the broader `position_unit`
filter to the Phase 1-only `position_unit_phase1` filter.

The target is placed after `check-web-logger-position-unit-fixtures` and
before `check-web-logger-rust-utf16-offset-conversion`. It is listed in
`.PHONY` and appears in `make help`.

Step-web-logger-049 observed 9 focused tests passing through this target. The
target runs focused Rust validator Phase 1 tests only. It does not run full
validator tests, workspace tests, the Python fixture validator, replay checks,
extract / micro_episode checks, fixture mutation, expected-value regeneration,
or release-quality wrapper integration.

The target proves only that the focused Rust validator Phase 1 tests pass in
the audited environment. It does not prove Phase 2 UTF-16 numeric metadata
validation, replay correctness, TypeScript logger compatibility, hash
compatibility, event durability, production readiness, real-data readiness, or
model performance.

## 5. Current Release-Quality Wrapper Review

The current release-quality wrapper includes these Web logger checks in order:

- `release_quality_check: web logger unicode hash vector fixture validation`
- `release_quality_check: web logger position_unit fixture contract validation`
- `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

The wrapper calls Makefile targets for these checks rather than duplicating
their underlying commands. It does not yet call
`check-web-logger-rust-validator-position-unit-phase1`.

The learner-state target group starts after the Web logger checks and can
remain unchanged. Current release-quality still passes without this new Rust
validator Phase 1 target.

## 6. Recommended Release-Quality Label

Recommended label:

`release_quality_check: web logger Rust validator position_unit Phase 1 policy`

This label is intentionally narrow. It is Web logger scoped, Rust validator
scoped, position_unit scoped, and Phase 1 scoped. It does not imply Phase 2
UTF-16 numeric metadata validation, replay correctness, extract /
micro_episode integration, TypeScript compatibility, event durability,
production readiness, real-data readiness, or model performance.

Rejected broader labels:

- `release_quality_check: web logger position_unit validation`
- `release_quality_check: web logger schema position_unit policy`
- `release_quality_check: web logger Rust position_unit complete`
- `release_quality_check: web logger Unicode correctness`
- `release_quality_check: web logger production validation`

These labels are too broad because they blur the boundary between focused Rust
validator Phase 1 behavior, fixture contract validation, future Phase 2 UTF-16
numeric checks, replay behavior, TypeScript compatibility, and production
evidence.

## 7. Recommended Command

Recommended command:

`make check-web-logger-rust-validator-position-unit-phase1`

The wrapper should call the Makefile target and should not duplicate
the Cargo command directly. The Makefile target remains the command source of
truth.

The command should not run full validator tests, workspace tests, the Python
fixture validator, replay, extract / micro_episode checks, fixture mutation,
expected-value regeneration, or fallback checks.

## 8. Recommended Insertion Point

Recommended insertion point in `scripts/check_release_quality.sh`:

- after `release_quality_check: web logger position_unit fixture contract validation`
- before `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

This keeps the Web logger position_unit checks grouped. The fixture contract
check should run before the Rust validator Phase 1 focused tests, and the Rust
validator Phase 1 focused tests should run before the replay-focused UTF-16
integration check. This preserves learner-state target order and does not move
unrelated checks.

## 9. Expected Release-Quality Output After Future Integration

Expected output after future integration should include:

- `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
- `command: make check-web-logger-rust-validator-position-unit-phase1`
- underlying focused Cargo command after Step059:
  `cargo test -p kslog_validate position_unit_phase1`
- pass status for the focused Rust validator tests
- expected focused test count: 9
- final `release_quality_check: ok`

Allowed summaries are label, command, package, test filter, pass status,
focused test count when visible, and final ok.

Docs and future status markers must not copy raw Cargo output, full job
output, raw GitHub Actions log blocks, raw fixture bodies, full fixture JSON
bodies, raw event JSON, raw source / selected / inserted / deleted text,
private paths, absolute local paths, real participant data, raw learner text,
logits / probabilities, or performance metric bodies.

## 10. Expected Failure Semantics

Release-quality should fail if the Makefile target exits nonzero, the focused
Cargo command fails, Phase 1 valid cases no longer pass, Phase 1 invalid cases
no longer fail with expected reason codes, legacy missing position_unit gating
changes unexpectedly, diagnostics start printing raw bodies or raw text, or
the code no longer compiles.

The wrapper should not repair fixtures, rewrite fixture files, regenerate
expected values, fallback to weaker checks, suppress target failures, or
duplicate the target command directly.

## 11. Proposed Future Step-web-logger-051 Scope

Step-web-logger-051 should be the implementation step. It should modify only
`scripts/check_release_quality.sh` as needed, add one label,
`release_quality_check: web logger Rust validator position_unit Phase 1 policy`,
and add one command,
`make check-web-logger-rust-validator-position-unit-phase1`.

Step051 should preserve the insertion point, avoid Makefile changes, avoid
Rust code changes, avoid test changes, avoid fixture JSON changes, avoid
TypeScript / Python changes, and avoid CI workflow changes. It should update
README and full technical specification related docs because release-quality
visible behavior changes.

Step051 should run `make check-web-logger-rust-validator-position-unit-phase1`,
`cargo test -p kslog_validate`, `cargo test --workspace`,
`make check-web-logger-position-unit-fixtures`, and `make check-release-quality`.
It should confirm that the new label appears, the command appears, final
`release_quality_check: ok` appears, and output remains public-safe.

## 12. Future Run Record / Status Marker Staging

Recommended later steps:

- Step-web-logger-052: Rust validator position_unit Phase 1 release-quality remote/manual run record workflow design
- Step-web-logger-053: Rust validator position_unit Phase 1 release-quality status marker
- Step-web-logger-054: Rust validator position_unit Phase 1 release-quality final safety review

A status marker should not be created before release-quality integration
exists. Remote GitHub Actions metadata should be preferred, and local/manual
fallback should be explicitly marked if remote metadata is unavailable. The
final safety review should accept only bounded Rust validator Phase 1
enforcement, not Phase 2 numeric validation.

## 13. Relationship to Step049 Makefile Target

Step049 added the Makefile target. Release-quality integration should call
that target, should not duplicate the Cargo command directly, and should keep
the Makefile target as command source of truth. Integration does not expand
validator scope.

## 14. Relationship to Step047 Validator Implementation

Step047 implemented Rust validator Phase 1 behavior. Release-quality
integration only runs focused tests through Makefile. A future release-quality
pass will not prove Phase 2 UTF-16 numeric validation, replay correctness,
extract integration, or micro_episode integration.

## 15. Relationship to Step043 Accepted Fixture Contract Boundary

Step043 accepted the fixture contract validation boundary. Rust validator
Phase 1 is a newer and separate chain. Fixture contract pass supports the Rust
validator work, but it is not equivalent to Rust validator enforcement. This
design does not create a new accepted boundary.

## 16. Relationship to Step045 Schema Boundary

Step045 schema parser/accessor boundary supports Step047 validator
enforcement. The future release-quality target tests validator behavior, not
only schema parser behavior. The schema boundary remains prerequisite but not
equivalent to validator enforcement.

## 17. Relationship to Phase 2 UTF-16 Numeric Metadata Validation

This release-quality target is Phase 1 only. It does not enforce doc_len
UTF-16 mismatches, offsets beyond UTF-16 length, surrogate-pair internal
offsets, or invalid UTF-16 boundary cases. Shared helper strategy remains
future work.

## 18. Relationship to Step031 Replay Integration

Step031 replay integration is separate. The Phase 1 validator target does not
call replay. Replay correctness does not prove validator policy, and validator
Phase 1 pass does not prove replay correctness.

## 19. Relationship to TypeScript Logger

This target does not modify TypeScript. It assumes future Web logger events
emit explicit `position_unit=utf16_code_unit`, but TypeScript emission and
compatibility review remain future work.

## 20. Relationship to SHA-256 Hash Compatibility

This target does not implement a SHA-256 helper, does not run TypeScript/Rust
hash vector checks, and does not prove current TypeScript and Rust hashes
match.

## 21. Relationship to Event Durability

This target does not implement event durability. Queueing, IndexedDB
persistence, acknowledgement, retry, deduplication, server-side idempotency,
event_id deduplication, ordering, and delivery guarantees remain future work.

## 22. No-Oracle / Synthetic-Only Boundary

The focused tests use synthetic fixtures. They do not use real participant
data, raw learner text, final_text, observed_after_text, gold labels,
post-hoc annotation, model performance validation, or test-set tuning.
No-oracle constraints are not relaxed.

## 23. Non-Equivalence Cautions

- Release-quality integration design is not wrapper implementation.
- Future release-quality pass is not production readiness.
- Synthetic-only validation is not real-data readiness.
- Rust validator Phase 1 pass is not Phase 2 UTF-16 numeric validation.
- Rust validator Phase 1 pass is not replay correctness.
- Rust validator Phase 1 pass is not extract integration.
- Rust validator Phase 1 pass is not micro_episode integration.
- Rust validator Phase 1 pass is not TypeScript compatibility.
- Rust validator Phase 1 pass is not hash compatibility.
- Rust validator Phase 1 pass is not event durability.
- Final acceptance still requires status marker and final safety review.

## 24. Non-Claims

This document does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, Phase 2 UTF-16 numeric
validation, hash compatibility completion, TypeScript/Rust vector check
completion, current TypeScript/Rust hash equality, event durability, data
collection readiness, or deployment readiness.

## 25. Recommended Next Step

Recommended next step:

Step-web-logger-051: integrate Rust validator position_unit Phase 1 target into
release-quality wrapper

Step051 should be an implementation step. It should modify
`scripts/check_release_quality.sh`, add one label / command pair, call
`make check-web-logger-rust-validator-position-unit-phase1`, avoid Makefile
changes, avoid Rust code changes, avoid test changes, avoid fixture JSON
changes, avoid TypeScript / Python changes, and update README plus full
technical specification related docs because release-quality visible behavior
changes. It should not claim Phase 2 numeric validation, production readiness,
or real-data readiness.

## 26. Step-web-logger-051 Implementation Status

Step-web-logger-051 implements this release-quality integration design.

Added release-quality label:

`release_quality_check: web logger Rust validator position_unit Phase 1 policy`

Added command:

`make check-web-logger-rust-validator-position-unit-phase1`

The check is inserted after
`release_quality_check: web logger position_unit fixture contract validation`
and before
`release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`.
The wrapper calls the Makefile target and does not duplicate
the Cargo command directly.

This is release-quality integration for Rust validator Phase 1 focused tests
only. It does not change Makefile, Rust code, tests, fixtures, TypeScript,
Python, Phase 2 UTF-16 numeric metadata validation, extract / micro_episode
integration, status marker evidence, final safety review acceptance, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 27. Recommended Next Step After Step-web-logger-051

Recommended next step:

Step-web-logger-052: Rust validator position_unit Phase 1 release-quality run
record workflow design

Step052 should be run-record-workflow-design / docs-only. It should define
remote/manual evidence collection, metadata-only output handling, status
marker fields, local fallback rules, safety checklist, and Step053 handoff
without creating a status marker yet and without claiming Phase 2 numeric
validation, production readiness, or real-data readiness.

## 28. Step-web-logger-052 Run Record Workflow Design

Step-web-logger-052 adds
[Rust validator position_unit Phase 1 release-quality remote/manual run record workflow](web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_record_workflow.md).

The workflow design keeps Step051 release-quality integration as prerequisite
evidence and defines what future Step053 should record as public-safe
metadata. It does not create a status marker, does not create final safety
review acceptance, and does not claim Phase 2 UTF-16 numeric validation,
production readiness, real-data readiness, or model performance evidence.

## 29. Step-web-logger-053 Remote Status Marker

Step-web-logger-053 created
[Rust validator position_unit Phase 1 release-quality remote run status](status/web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_status.md).
It records remote GitHub Actions Release Quality evidence for the Step051
wrapper integration with `local_fallback_used=no`, the observed Rust validator
Phase 1 label, command `make check-web-logger-rust-validator-position-unit-phase1`,
focused 9-test target summary, and final `release_quality_check: ok`.

This status marker keeps the integration evidence bounded to Rust validator
Phase 1 presence / value / schema-version gating. It does not create final
safety review acceptance and does not claim Phase 2 UTF-16 numeric metadata
validation, replay correctness, extract / micro_episode integration,
TypeScript/Rust compatibility, event durability, production readiness,
real-data readiness, or model performance evidence.

## 30. Step-web-logger-054 Final Safety Review

Step-web-logger-054 created
[Rust validator position_unit Phase 1 release-quality chain final safety review](web_logger_rust_validator_position_unit_phase1_release_quality_chain_final_safety_review.md).
The review accepts the Step047 through Step053 chain only for
release-quality-integrated, remote-status-recorded Rust validator Phase 1
presence / value / schema-version gating.

The accepted boundary does not include Phase 2 UTF-16 numeric metadata
validation, replay correctness, extract / micro_episode integration,
TypeScript logger compatibility, SHA-256 compatibility, event durability,
production readiness, real-data readiness, or model performance evidence.

## 31. Step-web-logger-055 Phase 2 Design

Step-web-logger-055 created
[Rust validator Phase 2 UTF-16 numeric metadata validation design](web_logger_rust_validator_phase2_utf16_numeric_metadata_validation_design.md).
The design keeps the Phase 1 release-quality label and target scoped to
presence / value / schema-version gating and plans a separate future chain for
UTF-16 numeric metadata validation.

Step055 does not alter the wrapper, Makefile, Rust tests, release-quality
ordering, or status marker, and it does not claim Phase 2 implementation.

## 32. Step-web-logger-058 Phase 1 Filter Correction Design Follow-Up

Step-web-logger-058 records that the existing Phase 1 Makefile target command
now runs a broader focused set after Step057 because `position_unit` also
matches `position_unit_phase2` test names. The recommended future correction is
to change the Makefile target command to
`cargo test -p kslog_validate position_unit_phase1`.

The release-quality wrapper can keep calling
`make check-web-logger-rust-validator-position-unit-phase1`; after the Makefile
command is corrected, the existing Phase 1 release-quality label is accurate
again without wrapper changes. Phase 2 wrapper integration remains a separate
future chain.

## 33. Step-web-logger-059 Makefile Correction Follow-Up

Step-web-logger-059 corrects the Makefile target command. The wrapper command
remains `make check-web-logger-rust-validator-position-unit-phase1`, but that
target now runs `cargo test -p kslog_validate position_unit_phase1`.

This restores the Phase 1 release-quality label to Phase 1-only coverage
without changing `scripts/check_release_quality.sh`. The new Phase 2 target is
not called by release-quality yet.
