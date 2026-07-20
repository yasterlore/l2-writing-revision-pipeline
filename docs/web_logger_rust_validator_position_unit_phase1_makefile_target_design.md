# Rust Validator Position Unit Phase 1 Makefile Target Design

## 1. Title

Rust Validator Position Unit Phase 1 Makefile Target Design

## 2. Scope

This is a Makefile-target-design / docs-only step.

This step makes no Makefile changes, no release-quality wrapper changes, no
Rust code changes, no TypeScript code changes, no Python code changes, no test
changes, no fixture JSON changes, no CI workflow changes, no `Cargo.toml` /
`Cargo.lock` changes, and no `package.json` changes.

This step makes no validator behavior changes, no schema behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-043 accepted only the fixture contract validation chain for
the fixed 17-case synthetic Web logger position-unit fixture matrix.

Step-web-logger-045 implemented the Rust schema field and parser/accessor
boundary in `kslog_schema`. Step-web-logger-046 designed the Rust validator
fixture mapping. Step-web-logger-047 implemented bounded Rust validator Phase
1 `position_unit` enforcement in `kslog_validate`.

This document designs Makefile target exposure only. It does not add the
target, does not add release-quality integration, and does not create a new
accepted evidence boundary. Phase 2 UTF-16 numeric metadata validation remains
future work.

## 4. Current Rust Validator Phase 1 Audit

Step-web-logger-047 changed `crates/kslog_validate/src/lib.rs`.

Focused command:

`cargo test -p kslog_validate position_unit`

Step-web-logger-047 observed 9 focused tests for the `position_unit` filter.
The full validator test command `cargo test -p kslog_validate` also passed.

Phase 1 policy:

- fixture-targeted Web logger v0.2-style records require
  `position_unit=utf16_code_unit`
- missing values fail with `missing_position_unit`
- unsupported `byte_index` and `code_point` values fail with
  `unsupported_position_unit`
- schema mismatch fails with `position_unit_schema_mismatch`
- unknown schema version fails with `unknown_schema_version`
- legacy missing-position-unit behavior is explicitly gated

Handled Phase 1 reason codes:

- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `unknown_schema_version`

Phase 2 deferred cases include UTF-16 document length mismatch, offset beyond
UTF-16 length, surrogate-pair internal offset, detectable byte-index misuse,
and validator-specific mapping for numeric boundary failures.

The existing fixture contract validator target still passes with 17 cases and
24 records. The existing release-quality wrapper also passes through its
current checks. Step047 does not prove Phase 2 UTF-16 numeric validation,
replay correctness, extract / micro_episode integration, TypeScript logger
compatibility, hash compatibility, event durability, production readiness,
real-data readiness, or model performance.

Diagnostics remain body-free and public-safe: test output records command
metadata, test names, counts, and pass/fail status, not fixture payloads or
learner-authored content.

## 5. Existing Makefile Target Audit

Current Web logger Makefile targets include:

- `check-web-logger-unicode-hash-vector-fixtures`
- `check-web-logger-position-unit-fixtures`
- `check-web-logger-rust-utf16-offset-conversion`

The help text uses one `@echo` line per target. `.PHONY` entries are listed at
the top of the Makefile, and target bodies are grouped with related Web logger
checks before learner-state target groups.

The existing position-unit fixture target runs the Python fixture contract
validator. The Unicode/hash target follows the same fixture-validator style.
The Rust UTF-16 target runs a focused Rust test filter through Cargo. A new
Rust validator Phase 1 target should follow the same Web logger grouping and
focused-command style.

## 6. Recommended Target Name

Recommended target:

`check-web-logger-rust-validator-position-unit-phase1`

Why this name is safest:

- clearly Web logger scoped
- clearly Rust validator scoped
- clearly `position_unit` scoped
- clearly Phase 1 scoped
- does not imply Phase 2 UTF-16 numeric validation
- does not imply replay correctness
- does not imply extract / micro_episode integration
- does not imply TypeScript compatibility
- does not imply production readiness

Rejected alternatives:

- `check-web-logger-position-unit-validator`: too ambiguous about Python
  fixture validator versus Rust validator.
- `check-rust-position-unit`: too broad and not Web logger scoped.
- `check-web-logger-position-unit-phase1`: does not clearly identify Rust
  validator behavior.
- `check-web-logger-rust-position-unit`: omits Phase 1 and could imply the
  full policy.
- `check-web-logger-schema-position-unit`: too easy to confuse with schema
  parser behavior or fixture contract validation.

## 7. Recommended Help Text

Recommended help text:

`Run Rust validator position_unit Phase 1 policy tests`

The help text should mention Rust validator and Phase 1. It should not mention
full schema-level policy completion, UTF-16 numeric validation, production
validation, or release-quality status.

## 8. Recommended Command

Recommended command:

`cargo test -p kslog_validate position_unit`

The command should run the focused Rust validator tests only. It should not run
the full workspace, run the Python fixture validator, run replay, run extract
/ micro_episode, mutate fixtures, regenerate expected values, require network
access, or fall back to weaker checks. The output should remain public-safe.

## 9. Target Placement

Recommended placement in the Makefile:

- near existing Web logger validation targets
- after `check-web-logger-position-unit-fixtures`
- before `check-web-logger-rust-utf16-offset-conversion`

Rationale:

- fixture contract validation should precede Rust validator Phase 1 focused
  tests
- Rust validator Phase 1 should precede replay-focused UTF-16 checks in the
  Web logger block
- Web logger checks remain grouped
- learner-state target ordering remains unchanged
- existing target commands remain unchanged

## 10. Should Target Run Full Validator Tests?

Preferred recommendation: the target should run only the focused command:

`cargo test -p kslog_validate position_unit`

Full `cargo test -p kslog_validate` remains part of broader Rust checks and
implementation-step verification. The release-quality wrapper already has a
broader Rust block. Keeping this target focused avoids duplicate full
validator runs and keeps output smaller.

Step-web-logger-049 should still run full validator tests during verification.
The Makefile target itself should remain focused.

## 11. Expected Target Output

Expected target output:

- Cargo runs `kslog_validate` tests filtered by `position_unit`
- Phase 1 focused tests pass
- expected focused test count from Step047: 9 tests
- no event payload is printed
- no source / selected / inserted / deleted text is printed
- no fixture payload is printed
- no private or machine-specific paths are copied into docs
- no production / real-data / performance claims are made

Cargo output may include standard local or CI build metadata. Documentation
and later status markers should not copy unbounded Cargo output. Status
evidence should record metadata and counts only.

## 12. Failure Semantics

The target should fail nonzero if:

- any Phase 1 focused validator test fails
- reason-code mapping changes unexpectedly
- valid position-unit cases no longer pass
- Phase 1 invalid cases no longer fail with expected reason codes
- legacy missing-position-unit gating changes unexpectedly
- diagnostics start printing event payloads or learner-authored content
- compile fails

The target should not repair fixtures, rewrite fixture files, regenerate
expected values, fall back to weaker checks, or suppress failures.

## 13. Proposed Future Step-web-logger-049 Scope

Step-web-logger-049 should:

- modify Makefile only as needed
- add `.PHONY` entry for
  `check-web-logger-rust-validator-position-unit-phase1`
- add help text `Run Rust validator position_unit Phase 1 policy tests`
- add command `cargo test -p kslog_validate position_unit`
- place the target after `check-web-logger-position-unit-fixtures` and before
  `check-web-logger-rust-utf16-offset-conversion`
- not modify Rust code
- not modify tests
- not modify fixtures
- not modify TypeScript or Python code
- not modify the release-quality wrapper
- update README and full technical specification related docs because
  Makefile-visible behavior changes
- run `make help`
- run `make check-web-logger-rust-validator-position-unit-phase1`
- run `cargo test -p kslog_validate`
- run `cargo test --workspace`
- run `cargo fmt --all -- --check`
- run `cargo clippy --workspace -- -D warnings`
- run `make check-web-logger-position-unit-fixtures`
- run focused Python fixture validator tests
- optionally run `make check-release-quality`

## 14. Future Release-Quality Staging

Recommended later steps:

- Step-web-logger-050: Rust validator position_unit Phase 1 release-quality
  integration design
- Step-web-logger-051: release-quality wrapper integration
- Step-web-logger-052: remote/manual run record workflow design
- Step-web-logger-053: status marker
- Step-web-logger-054: final safety review

Do not add release-quality integration in Step049. Do not create a status
marker before release-quality integration exists. Future release-quality labels
should remain Phase 1 scoped.

## 15. Future Release-Quality Label Preview

Tentative future label:

`release_quality_check: web logger Rust validator position_unit Phase 1 policy`

Tentative future command:

`make check-web-logger-rust-validator-position-unit-phase1`

Tentative future insertion point:

- after `release_quality_check: web logger position_unit fixture contract validation`
- before `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

This is only a preview for a later design step. Step048 does not modify the
wrapper.

## 16. Relationship to Step047 Implementation

Step047 implemented validator behavior. Step048 designs Makefile exposure for
that behavior. The future Makefile target must not expand validator scope. A
target pass will not prove Phase 2 UTF-16 numeric validation or replay
correctness.

## 17. Relationship to Step043 Accepted Boundary

Step043 accepted the fixture contract validation chain. Step047 implemented
Rust validator Phase 1 after that chain. Step048 does not create a new
accepted boundary. A future release-quality / status / final-review chain is
still needed for Rust validator Phase 1 evidence.

## 18. Relationship to Step045 Schema Boundary

Step045 parser/accessor behavior supports Step047 validator enforcement. The
future target will test validator behavior, not only schema parser behavior.
The schema boundary remains a prerequisite, not an equivalent substitute.

## 19. Relationship to Phase 2 UTF-16 Numeric Metadata Validation

The target is Phase 1 only. It does not test UTF-16 document-length mismatch
enforcement, offset-beyond-length enforcement, surrogate-pair internal-offset
enforcement, or detectable byte-index misuse. Shared helper strategy remains
future work.

## 20. Relationship to Step031 Replay Integration

Step031 replay integration is separate. The Phase 1 validator target does not
call replay. Replay correctness does not prove validator policy, and validator
Phase 1 pass does not prove replay correctness.

## 21. Relationship to TypeScript Logger

The target does not modify TypeScript. It assumes future Web logger events
emit explicit `position_unit=utf16_code_unit`. TypeScript emission and
compatibility review remain future work.

## 22. Relationship to SHA-256 Hash Compatibility

The target does not implement a SHA-256 helper, does not run TypeScript/Rust
hash vector checks, and does not prove current TypeScript and Rust hashes
match. Hash compatibility remains a separate chain.

## 23. Relationship to Event Durability

The target does not implement event durability. Queueing, IndexedDB,
acknowledgement, retry, deduplication, server-side idempotency, and event ID
deduplication remain unimplemented.

## 24. No-Oracle / Synthetic-Only Boundary

Tests use synthetic fixtures. They must not introduce participant-origin data,
learner-authored raw content, future/observed text snapshots, label fields,
after-the-fact annotations, model performance validation, or test-set tuning.
No-oracle constraints are not relaxed.

## 25. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Focused target pass is not release-quality integration.
- Rust validator Phase 1 pass is not Phase 2 UTF-16 numeric validation.
- Rust validator Phase 1 pass is not replay correctness.
- Rust validator Phase 1 pass is not extract integration.
- Rust validator Phase 1 pass is not micro_episode integration.
- Rust validator Phase 1 pass is not TypeScript compatibility.
- Rust validator Phase 1 pass is not hash compatibility.
- Rust validator Phase 1 pass is not event durability.
- Synthetic-only validation is not real-data readiness.
- Release-quality pass is not production readiness.

## 26. Non-Claims

This document does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, Phase 2 UTF-16 numeric
validation implementation, hash compatibility implementation completion,
TypeScript/Rust vector check implementation, current TypeScript/Rust hash
equality, event durability implementation, data collection readiness, or
deployment readiness.

## 27. Recommended Next Step

Recommended next step:

Step-web-logger-049: add Rust validator position_unit Phase 1 Makefile target

Step049 should be an implementation step. It should modify Makefile only as
needed, add the focused target, keep Rust code / tests / fixtures / TypeScript
/ Python / release-quality wrapper unchanged, and update README plus full
technical specification related docs because Makefile-visible behavior
changes. It should not claim release-quality integration, production
readiness, or real-data readiness.

## 28. Step-web-logger-049 Implementation Status

Step-web-logger-049 implements this target design in Makefile.

Added target:

`check-web-logger-rust-validator-position-unit-phase1`

Help text:

`Run Rust validator position_unit Phase 1 policy tests`

Command:

`cargo test -p kslog_validate position_unit`

The target is placed after `check-web-logger-position-unit-fixtures` and
before `check-web-logger-rust-utf16-offset-conversion`. It runs focused Rust
validator Phase 1 tests only. It does not run full validator tests, workspace
tests, the Python fixture contract validator, replay checks, extract /
micro_episode checks, or release-quality wrapper integration.

Release-quality integration remains future work for Step-web-logger-050 and
later. Phase 2 UTF-16 numeric metadata validation, TypeScript logger changes,
SHA-256 helper work, TypeScript/Rust vector checks, event durability,
production readiness, real-data readiness, and model performance evidence
remain outside Step049.

## 29. Recommended Next Step After Step-web-logger-049

Recommended next step:

Step-web-logger-050: Rust validator position_unit Phase 1 release-quality
integration design

Step050 should be release-quality-integration-design / docs-only. It should
design the future wrapper label, command, insertion point, public-safe output
boundary, failure semantics, and later remote/status/final-review staging for
the new Makefile target. It should not modify the wrapper yet and should not
claim Phase 2 UTF-16 numeric validation, production readiness, or real-data
readiness.

## 30. Step-web-logger-050 Release-Quality Integration Design

Step-web-logger-050 adds
[Rust validator position_unit Phase 1 release-quality integration design](web_logger_rust_validator_position_unit_phase1_release_quality_integration_design.md).

The design recommends future wrapper label
`release_quality_check: web logger Rust validator position_unit Phase 1 policy`
and command `make check-web-logger-rust-validator-position-unit-phase1`.
It keeps this Makefile target as command source of truth, recommends insertion
after position_unit fixture contract validation and before Rust UTF-16 replay
integration, and remains docs-only without wrapper, Makefile, Rust code, test,
fixture, Phase 2 UTF-16 numeric validation, production readiness, real-data
readiness, or model performance changes.

## 31. Step-web-logger-051 Release-Quality Integration

Step-web-logger-051 adds the Step049 target to `scripts/check_release_quality.sh`
with label `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
and command `make check-web-logger-rust-validator-position-unit-phase1`.

The wrapper calls the Makefile target and does not duplicate the Cargo command
directly. Makefile remains unchanged in Step051. Phase 2 UTF-16 numeric
validation, status marker evidence, final safety review acceptance,
production readiness, real-data readiness, and model performance evidence
remain future work.

## 32. Step-web-logger-052 Run Record Workflow Design

Step-web-logger-052 designs the future run-record workflow for the
release-quality check that now calls this target. Future status evidence should
record the Makefile target command and focused 9-test result as public-safe
metadata only.

This design does not modify Makefile and does not create status marker
evidence, final safety review acceptance, Phase 2 UTF-16 numeric validation,
production readiness, real-data readiness, or model performance evidence.

## 33. Step-web-logger-053 Remote Status Marker

Step-web-logger-053 created
[Rust validator position_unit Phase 1 release-quality remote run status](status/web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_status.md).
The marker records that release-quality invoked the Step049 Makefile target via
`make check-web-logger-rust-validator-position-unit-phase1` and observed the
focused 9-test Rust validator Phase 1 summary and final
`release_quality_check: ok`.

The status marker does not broaden this Makefile target design: the target
remains focused on `cargo test -p kslog_validate position_unit` and does not
run full validator tests, workspace tests, Python fixture validation, replay,
extract / micro_episode, fixture regeneration, Phase 2 UTF-16 numeric metadata
validation, or production / real-data / model-performance checks.

## 34. Step-web-logger-054 Final Safety Review

Step-web-logger-054 created
[Rust validator position_unit Phase 1 release-quality chain final safety review](web_logger_rust_validator_position_unit_phase1_release_quality_chain_final_safety_review.md).
The final review accepts the release-quality-integrated target chain only for
focused Rust validator Phase 1 policy tests.

This does not change the target command, does not expand the target to full
validator or workspace tests, and does not add Phase 2 UTF-16 numeric metadata
validation, replay, extract / micro_episode, TypeScript compatibility, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 35. Step-web-logger-055 Phase 2 Design

Step-web-logger-055 created
[Rust validator Phase 2 UTF-16 numeric metadata validation design](web_logger_rust_validator_phase2_utf16_numeric_metadata_validation_design.md).
The design recommends keeping the Step049 Makefile target focused on Phase 1
and adding a separate future Phase 2 target after implementation.

Step055 does not change Makefile and does not relabel the Phase 1 target as a
full `position_unit` policy target.

## 36. Step-web-logger-058 Filter Scope Follow-Up

Step-web-logger-058 identifies a post-Step057 scope drift in the implemented
Phase 1 Makefile target. The target command `cargo test -p kslog_validate
position_unit` now matches both `position_unit_phase1` and
`position_unit_phase2` tests because Cargo test filtering is substring based.

The future correction should keep target
`check-web-logger-rust-validator-position-unit-phase1` and help text
`Run Rust validator position_unit Phase 1 policy tests`, but change the command
to `cargo test -p kslog_validate position_unit_phase1`. The same future Step
should add the separate Phase 2 target designed in
[Rust validator Phase 2 UTF-16 numeric metadata Makefile target design](web_logger_rust_validator_phase2_utf16_numeric_metadata_makefile_target_design.md).

## 37. Step-web-logger-059 Filter Correction Implementation

Step-web-logger-059 applies the correction described above. The Phase 1 target
name and help text are unchanged, and the command is now
`cargo test -p kslog_validate position_unit_phase1`.

Step059 also adds the separate Phase 2 target
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric` with
command `cargo test -p kslog_validate position_unit_phase2`. The Phase 1
target should be interpreted as Phase 1-only again; Phase 2 release-quality
integration remains future work.

## 38. Step-web-logger-060 Release-Quality Design Follow-Up

Step-web-logger-060 designs future release-quality wrapper integration for the
separate Phase 2 target. The Phase 1 Makefile target remains unchanged by that
design and should continue to mean Phase 1-only focused tests.

## 39. Step-web-logger-061 Release-Quality Integration Follow-Up

Step-web-logger-061 adds the separate Phase 2 target to the release-quality
wrapper while preserving the Phase 1 Makefile target name, help text, command,
and wrapper label/command. The Phase 1 target still runs
`cargo test -p kslog_validate position_unit_phase1`.

## 40. Step-web-logger-062 Phase 2 Run Record Workflow Design Follow-Up

Step-web-logger-062 designs future status recording for the Phase 2 wrapper
check. It does not change the Phase 1 Makefile target or the Phase 1-only
focused-test boundary.

## 41. Step-web-logger-063 Phase 2 Status Marker Follow-Up

Step-web-logger-063 records public-safe remote status metadata for the
separate Phase 2 wrapper check. It does not change the Phase 1 Makefile target,
the corrected `position_unit_phase1` filter, or the Phase 1-only focused-test
boundary.
