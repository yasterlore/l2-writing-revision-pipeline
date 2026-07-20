# Rust Validator Phase 2 UTF-16 Numeric Metadata Makefile Target Design

## 1. Title

Rust Validator Phase 2 UTF-16 Numeric Metadata Makefile Target Design

## 2. Scope

This is a Makefile-target-design / docs-only Step. It makes no Makefile
changes, no release-quality wrapper changes, no Rust code changes, no
TypeScript code changes, no Python code changes, no tests changes, no fixture
JSON / JSONL changes, no CI workflow changes, no Cargo.toml / Cargo.lock
changes, and no package.json changes.

This Step changes no validator behavior. It adds no Phase 2 release-quality
integration, creates no status marker, creates no final safety review, adds no
extract / micro_episode integration, implements no TypeScript logger
compatibility, implements no SHA-256 compatibility, implements no event
durability, and provides no production readiness, real-data readiness, or
model performance proof.

## 3. Design Status

Step-web-logger-054 accepted the Phase 1 release-quality chain with an explicit
boundary for Web logger v0.2-style `position_unit` presence / value /
schema-version gating. Step-web-logger-056 extracted the shared UTF-16 helper
into `kslog_schema`. Step-web-logger-057 implemented Phase 2 validator behavior
in `kslog_validate`.

Step-web-logger-058 designs Makefile exposure for Phase 2 and a correction to
the current Phase 1 Makefile target filter. Phase 2 is not
release-quality-integrated yet, not remote-status-recorded yet, and not
final-reviewed yet.

## 4. Step057 Phase 2 Implementation Recap

Step-web-logger-057 changed `crates/kslog_validate/src/lib.rs`. Phase 2 applies
only after Phase 1 accepts a Web logger v0.2-style event with
`position_unit=utf16_code_unit`.

The implementation uses `kslog_schema::utf16_offsets` and adds no
`kslog_validate -> kslog_replay` dependency. It checks UTF-16 doc length
metadata, cursor / selection offsets, `start > end`, surrogate-pair internal
offsets, invalid boundaries, and detectable byte-index misuse when the supplied
metadata contradicts UTF-16 length or scalar boundaries.

Stable Phase 2 reason codes are:

- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`

Focused command audit:

- `cargo test -p kslog_validate position_unit_phase2`
- observed focused count after Step057: 8 tests

Full validator audit:

- `cargo test -p kslog_validate`
- observed full validator count after Step057: 30 tests

Step057 proves bounded validator behavior and focused test coverage only. It
does not prove replay correctness, extract / micro_episode integration,
TypeScript compatibility, SHA-256 compatibility, event durability, production
readiness, real-data readiness, or model performance.

## 5. Current Phase 1 Target Scope Drift

The existing Phase 1 Makefile target is:

- `check-web-logger-rust-validator-position-unit-phase1`

Its current command is:

- `cargo test -p kslog_validate position_unit`

Cargo test filtering is substring based. Step057 added tests whose names begin
with `position_unit_phase2`, so `cargo test -p kslog_validate position_unit`
now matches both Phase 1 and Phase 2 tests.

Current observed behavior after Step057:

- `cargo test -p kslog_validate position_unit`: 17 matching tests
- `make check-web-logger-rust-validator-position-unit-phase1`: 17 matching
  tests

The target still passes, but it no longer means Phase 1-only. The target name,
help text, and release-quality label still describe Phase 1 policy tests, while
the invoked command currently runs a broader focused set. This should be
corrected before adding Phase 2 release-quality integration.

## 6. Recommended Phase 1 Target Correction

Future Makefile implementation should keep the target name:

- `check-web-logger-rust-validator-position-unit-phase1`

It should keep the help text:

- `Run Rust validator position_unit Phase 1 policy tests`

It should change the command from:

- `cargo test -p kslog_validate position_unit`

to:

- `cargo test -p kslog_validate position_unit_phase1`

This is a scope-restoration correction. It should not change Rust code, tests,
fixtures, or the release-quality wrapper. The existing release-quality wrapper
can continue calling the same Makefile target; after the Makefile command is
corrected, the existing Phase 1 release-quality label becomes accurate again.

Direct `cargo test -p kslog_validate position_unit` may remain useful for
manual broader position-unit regression, but it should not be used as the
Phase 1-only target command.

Audit result: current Phase 1 tests are consistently filterable by
`position_unit_phase1`, and `cargo test -p kslog_validate position_unit_phase1`
currently runs 9 tests.

## 7. Recommended Phase 2 Target Name

Recommended target name:

- `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

This name is Web logger scoped, Rust validator scoped, `position_unit` scoped,
Phase 2 scoped, and explicitly UTF-16 numeric metadata scoped. It does not
imply replay correctness, extract / micro_episode integration, TypeScript
compatibility, release-quality acceptance, production readiness, or real-data
readiness.

Rejected alternatives:

- `check-web-logger-rust-validator-position-unit-phase2`: too vague about the
  UTF-16 numeric metadata boundary.
- `check-web-logger-rust-validator-utf16`: too broad and could be confused
  with replay helper tests.
- `check-web-logger-position-unit-full`: implies broader or complete policy
  coverage.
- `check-web-logger-unicode-validation`: too broad and may imply broader
  Unicode correctness.

## 8. Recommended Phase 2 Help Text

Recommended help text:

- `Run Rust validator position_unit Phase 2 UTF-16 numeric metadata tests`

The help text should mention Rust validator, Phase 2, and UTF-16 numeric
metadata. It should not imply full Unicode correctness, replay correctness, or
release-quality acceptance.

## 9. Recommended Phase 2 Command

Recommended command:

- `cargo test -p kslog_validate position_unit_phase2`

The target should run focused Phase 2 validator tests only. It should not run
full validator tests, workspace tests, the Python fixture validator, replay,
extract, micro_episode, fixture regeneration, or any network-dependent command.

Current expected focused count after Step057: 8 tests.

## 10. Target Placement

Recommended Makefile order:

1. `check-web-logger-position-unit-fixtures`
2. `check-web-logger-rust-validator-position-unit-phase1`
3. `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
4. `check-web-logger-rust-utf16-offset-conversion`

Fixture contract validation should precede Rust validator tests. Phase 1
presence / value / schema-version gating should precede Phase 2 numeric
validation. Phase 2 numeric validation should precede replay-focused UTF-16
conversion / replay integration. This keeps Web logger checks grouped and does
not reorder learner-state checks.

## 11. `.PHONY` Design

Future Step-web-logger-059 should add:

- `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

to `.PHONY`.

No new `.PHONY` entry is needed for the Phase 1 target because it already
exists.

## 12. Expected Target Outputs

Corrected Phase 1 target:

- command: `cargo test -p kslog_validate position_unit_phase1`
- expected status: pass
- expected count from audit: 9 tests
- expected scope: Phase 1-only tests

New Phase 2 target:

- command: `cargo test -p kslog_validate position_unit_phase2`
- expected status: pass
- expected count from audit: 8 tests
- expected failures: 0 failed

Docs and status markers should record metadata/count summaries only. They
should not copy raw Cargo output or raw test output blocks.

## 13. Failure Semantics

The Phase 2 target should fail nonzero if:

- `cargo test -p kslog_validate position_unit_phase2` fails
- the five valid fixtures no longer pass
- doc_len before / after mismatch checks regress
- `start > end` checking regresses
- offset beyond UTF-16 length checking regresses
- surrogate-pair internal offset checking regresses
- detectable byte-index misuse boundary regresses
- diagnostics become bodyful
- compilation fails

The corrected Phase 1 target should fail nonzero if:

- Phase 1 reason codes regress
- legacy missing gating regresses
- diagnostics become bodyful
- compilation fails

Targets should not repair fixtures, rewrite fixture JSON, regenerate expected
values, suppress failures, or fallback silently to broader filters.

## 14. Proposed Future Step-web-logger-059 Scope

Step-web-logger-059 should be an implementation Step. It should modify
Makefile only as needed to:

- correct existing Phase 1 target command to
  `cargo test -p kslog_validate position_unit_phase1`
- add `.PHONY` for
  `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
- add help text
  `Run Rust validator position_unit Phase 2 UTF-16 numeric metadata tests`
- add target command
  `cargo test -p kslog_validate position_unit_phase2`
- place the new target after Phase 1 and before Rust UTF-16 replay target

Step059 should not modify Rust code, tests, fixture JSON, TypeScript, Python,
or release-quality wrapper. It should update README and full technical
specification related docs because Makefile-visible behavior changes.

Recommended checks for Step059:

- `make help`
- corrected Phase 1 target
- new Phase 2 target
- `cargo test -p kslog_validate`
- schema/replay regressions
- workspace/fmt/clippy
- existing fixture contract validator
- `make check-release-quality`

The existing Phase 1 release-quality label should still appear and final
release-quality should still finish ok. Phase 2 should not be described as
release-quality-integrated unless a later wrapper Step adds it.

## 15. Future Release-Quality Staging

Recommended later steps:

- Step-web-logger-060: Phase 2 release-quality integration design
- Step-web-logger-061: Phase 2 release-quality wrapper integration
- Step-web-logger-062: Phase 2 remote/manual run record workflow design
- Step-web-logger-063: Phase 2 status marker
- Step-web-logger-064: Phase 2 final safety review

Step059 should not add wrapper integration.

## 16. Future Release-Quality Label Preview

Tentative future label:

- `release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`

Tentative future command:

- `make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

Expected insertion point:

- after Phase 1 release-quality label
- before Rust UTF-16 offset conversion and replay integration label

This is a preview only. Step058 does not modify the wrapper.

## 17. Relationship To Phase 1 Final-Reviewed Chain

The Phase 1 chain remains accepted by Step-web-logger-054. The Phase 1 target
command correction is a scope-restoration maintenance change. The Phase 1
accepted boundary should not be broadened to include Phase 2.

Phase 2 needs its own Makefile, release-quality, status, and final review
chain.

## 18. Relationship To Step057 Phase 2 Implementation

Step057 implemented Phase 2 validator behavior. Step058 designs Makefile
exposure only. A Makefile target does not expand validator behavior.

Phase 2 target pass will not prove replay correctness, extract /
micro_episode integration, TypeScript compatibility, SHA-256 compatibility,
event durability, production readiness, real-data readiness, or model
performance.

## 19. Relationship To Shared UTF-16 Helper And Replay

Step056 shared helper extraction supports Phase 2 validator implementation.
The Phase 2 target should not run replay tests. Replay correctness remains
separate, and the replay target remains:

- `check-web-logger-rust-utf16-offset-conversion`

## 20. Relationship To TypeScript Logger

The Phase 2 target does not modify TypeScript. It does not prove that the
TypeScript logger emits all required fields. TypeScript/Rust compatibility
remains separate.

## 21. Relationship To SHA-256 Hash Compatibility

The Phase 2 target does not implement a SHA-256 helper, does not run
TypeScript/Rust hash vector checks, and does not prove current TypeScript and
Rust hashes match.

## 22. Relationship To Event Durability

The Phase 2 target does not implement event durability. Queue / IndexedDB /
ack / retry / dedup remain future work. Server-side idempotency / event_id
dedup remains future work. Ordering and delivery durability remain open.

## 23. No-Oracle / Synthetic-Only Boundary

The focused tests use synthetic fixtures. They do not introduce real
participant data, raw learner text, final_text / observed_after_text / gold
labels / post-hoc annotation, model performance validation, or test-set
tuning. No-oracle constraints are not relaxed.

## 24. Public-Safe Diagnostics Design

Makefile targets should not print raw event JSON beyond normal Rust test names
and summary. Docs should not copy raw Cargo output, raw test output blocks, raw
fixture bodies, full fixture JSON bodies, or raw source / selected / inserted /
deleted text.

Reason-code and count summaries are acceptable. Private paths and absolute
local paths must not be copied into docs. Raw remote logs may contain CI runner
paths, so future status docs should use metadata-only summaries.

## 25. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Phase 2 Makefile target pass is not release-quality integration.
- Future Phase 2 release-quality pass is not production readiness.
- Phase 2 validator pass is not replay correctness.
- Phase 2 validator pass is not extract integration.
- Phase 2 validator pass is not micro_episode integration.
- Phase 2 validator pass is not TypeScript compatibility.
- Phase 2 validator pass is not hash compatibility.
- Phase 2 validator pass is not event durability.
- Synthetic-only validation is not real-data readiness.

## 26. Non-Claims

This design does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, hash compatibility
implementation completion, TypeScript/Rust vector check implementation,
current TypeScript/Rust hash equality, event durability implementation, data
collection readiness, or deployment readiness.

## 27. Recommended Next Step

Recommended next step:

`Step-web-logger-059: add Rust validator Phase 2 UTF-16 numeric metadata Makefile target and correct Phase 1 filter`

Step059 should be an implementation Step. It should modify Makefile only as
needed, correct the Phase 1 target command to `position_unit_phase1`, add the
Phase 2 target using `position_unit_phase2`, and update README and full
technical specification docs because Makefile-visible behavior changes.

Step059 should not modify Rust code, tests, fixture JSON, TypeScript, Python,
or release-quality wrapper. It should not claim Phase 2 release-quality
integration, production readiness, or real-data readiness.

## 28. Step-web-logger-059 Implementation Note

Step-web-logger-059 implements this Makefile target design. It corrects
`check-web-logger-rust-validator-position-unit-phase1` to run
`cargo test -p kslog_validate position_unit_phase1`, restoring Phase 1-only
target scope. It also adds
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric` with help
text `Run Rust validator position_unit Phase 2 UTF-16 numeric metadata tests`
and command `cargo test -p kslog_validate position_unit_phase2`.

The Phase 2 target is placed after the corrected Phase 1 target and before
`check-web-logger-rust-utf16-offset-conversion`. Step059 does not change the
release-quality wrapper, Rust code/tests, fixture JSON, TypeScript/Python
code, status markers, or Phase 2 release-quality acceptance.

## 29. Step-web-logger-060 Release-Quality Integration Design Follow-Up

Step-web-logger-060 adds
[Rust validator Phase 2 UTF-16 numeric metadata release-quality integration design](web_logger_rust_validator_phase2_utf16_numeric_metadata_release_quality_integration_design.md).
It recommends adding the Phase 2 target to the wrapper with label
`release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
and command
`make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.

Step060 is docs-only. It does not change the wrapper, Makefile, Rust code/tests,
fixtures, status markers, or Phase 2 release-quality acceptance.

## 30. Step-web-logger-061 Release-Quality Integration Follow-Up

Step-web-logger-061 integrates the Phase 2 target into
`scripts/check_release_quality.sh` with label
`release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
and command
`make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.

The Makefile target remains unchanged and remains the command source of truth.
Step061 does not change Rust code/tests, fixtures, or Phase 2 status/final
review evidence.

## 31. Step-web-logger-062 Run Record Workflow Design Follow-Up

Step-web-logger-062 designs the future status-marker workflow for recording
the Phase 2 target after release-quality wrapper integration. The Makefile
target remains unchanged and still runs
`cargo test -p kslog_validate position_unit_phase2`.

Step062 does not create a status marker and does not change Makefile, wrapper,
Rust code/tests, fixtures, or final-review evidence.

## 32. Step-web-logger-063 Status Marker Follow-Up

Step-web-logger-063 records public-safe remote metadata for the Phase 2 target
after release-quality wrapper integration. The status marker path is
`docs/status/web_logger_rust_validator_phase2_utf16_numeric_metadata_release_quality_remote_run_status.md`.

This does not change the Makefile target, the corrected Phase 1 target
filter, Rust code/tests, fixtures, wrapper behavior, replay behavior, or Phase
2 final-review evidence.

## 33. Step-web-logger-064 Final Safety Review Follow-Up

Step-web-logger-064 final-reviews the Phase 2 chain through remote status
marker evidence. It accepts only the bounded release-quality-integrated and
remote-status-recorded Phase 2 validator UTF-16 numeric metadata boundary.

This does not change the Makefile target, the corrected Phase 1 target
filter, Rust code/tests, fixtures, wrapper behavior, replay behavior, extract
/ micro_episode integration, TypeScript compatibility, hash compatibility, or
event durability.
