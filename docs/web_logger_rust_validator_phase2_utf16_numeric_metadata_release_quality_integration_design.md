# Rust Validator Phase 2 UTF-16 Numeric Metadata Release Quality Integration Design

## 1. Title

Rust Validator Phase 2 UTF-16 Numeric Metadata Release Quality Integration
Design

## 2. Scope

This is a release-quality-integration-design / docs-only Step. It makes no
release-quality wrapper changes in this Step, no Makefile changes in this
Step, no Rust code changes, no TypeScript code changes, no Python code
changes, no tests changes, no fixture JSON / JSONL changes, no CI workflow
changes, no Cargo.toml / Cargo.lock changes, and no package.json changes.

This Step changes no validator behavior. It creates no status marker, creates
no final safety review, adds no extract / micro_episode integration,
implements no TypeScript logger compatibility, implements no SHA-256
compatibility, implements no event durability, and provides no production
readiness, real-data readiness, or model performance proof.

## 3. Design Status

Step-web-logger-054 accepted the Phase 1 release-quality chain with the
explicit boundary for Web logger v0.2-style `position_unit` presence / value /
schema-version gating. Step-web-logger-056 extracted the shared UTF-16 helper
into `kslog_schema`. Step-web-logger-057 implemented Phase 2 validator
behavior. Step-web-logger-059 added the Phase 2 Makefile target and corrected
the Phase 1 filter.

Step-web-logger-060 designs Phase 2 release-quality integration only. Phase 2
is not release-quality-integrated yet, not remote-status-recorded yet, and not
final-reviewed yet.

## 4. Current Makefile Target Review

Corrected Phase 1 target:

- target: `check-web-logger-rust-validator-position-unit-phase1`
- command: `cargo test -p kslog_validate position_unit_phase1`
- expected focused count: 9 tests
- scope: Phase 1 presence / value / schema-version gating only

Phase 2 target:

- target: `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
- help text:
  `Run Rust validator position_unit Phase 2 UTF-16 numeric metadata tests`
- command: `cargo test -p kslog_validate position_unit_phase2`
- expected focused count: 8 tests
- `.PHONY` entry: present

Current Makefile placement is:

1. `check-web-logger-position-unit-fixtures`
2. `check-web-logger-rust-validator-position-unit-phase1`
3. `check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
4. `check-web-logger-rust-utf16-offset-conversion`

The Phase 2 target runs focused validator tests only. It does not run full
validator tests, workspace tests, the Python fixture validator, replay tests,
extract / micro_episode checks, fixture mutation, expected-value regeneration,
or network-dependent commands. The Phase 2 target is not yet invoked by the
release-quality wrapper.

## 5. Current Release-Quality Wrapper Review

The current Web logger release-quality block includes these labels:

1. `release_quality_check: web logger unicode hash vector fixture validation`
2. `release_quality_check: web logger position_unit fixture contract validation`
3. `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
4. `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

The current Phase 1 command is:

- `make check-web-logger-rust-validator-position-unit-phase1`

Because Step-web-logger-059 corrected the Makefile target, the wrapper now
indirectly runs `cargo test -p kslog_validate position_unit_phase1` for the
Phase 1 label. The wrapper does not yet call
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.

The release-quality wrapper still passes after Step-web-logger-059. Phase 2
release-quality integration remains future work, and learner-state checks
should remain untouched.

## 6. Recommended Phase 2 Release-Quality Label

Recommended label:

`release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`

This label is clearly Web logger scoped, Rust validator scoped,
`position_unit` scoped, Phase 2 scoped, and UTF-16 numeric metadata scoped. It
does not imply full Unicode correctness, replay correctness, extract /
micro_episode integration, TypeScript compatibility, production readiness, or
real-data readiness.

Rejected labels:

- `release_quality_check: web logger UTF-16 validation`: too broad and could
  be confused with replay UTF-16 checks.
- `release_quality_check: web logger position_unit full validation`: implies
  complete policy coverage.
- `release_quality_check: web logger Unicode correctness`: too broad.
- `release_quality_check: web logger Rust validator complete`: implies full
  validator completion.
- `release_quality_check: web logger production validation`: implies a
  production boundary this chain does not establish.

## 7. Recommended Command

Recommended command:

`make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

The wrapper should call the Makefile target and should not duplicate
`cargo test -p kslog_validate position_unit_phase2` directly. The Makefile
target remains the command source of truth.

The command should not run full validator tests, workspace tests, the Python
validator, replay, extract / micro_episode checks, fixture mutation,
expected-value regeneration, or fallback checks.

## 8. Recommended Insertion Point

Recommended insertion point in `scripts/check_release_quality.sh`:

- after `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
- before `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

Rationale:

- fixture contract validation should run before Rust validator checks
- Phase 1 gating should run before Phase 2 numeric validation
- Phase 2 numeric validation should run before replay-focused UTF-16
  integration
- Web logger position_unit checks remain grouped
- learner-state target order is preserved
- unrelated checks are not removed or reordered

Expected Web logger order after future integration:

1. `release_quality_check: web logger unicode hash vector fixture validation`
2. `release_quality_check: web logger position_unit fixture contract validation`
3. `release_quality_check: web logger Rust validator position_unit Phase 1 policy`
4. `release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
5. `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

## 9. Expected Release-Quality Output After Future Integration

Expected output should include:

- `release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
- `command: make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`
- underlying command: `cargo test -p kslog_validate position_unit_phase2`
- focused test result: pass
- expected focused test count: 8
- final `release_quality_check: ok`

Allowed summaries:

- label
- command
- test package
- test filter
- pass status
- focused test count if visible
- final ok

Forbidden to copy into docs/status:

- raw Cargo output body
- full job output
- raw GitHub Actions log blocks
- raw fixture body
- full fixture JSON body
- raw event JSON
- raw source / selected / inserted / deleted text
- private paths
- absolute local paths
- real participant data
- raw learner text
- logits / probabilities
- performance metric body

## 10. Expected Failure Semantics

Release-quality should fail if:

- the Phase 2 Makefile target exits nonzero
- `cargo test -p kslog_validate position_unit_phase2` fails
- the five valid cases no longer pass
- doc_len before / after mismatch checks regress
- `start > end` checking regresses
- offset beyond UTF-16 length checking regresses
- surrogate-pair internal offset checking regresses
- detectable byte-index misuse boundary regresses
- diagnostics become bodyful
- compilation fails

The wrapper should not repair fixtures, rewrite fixture files, regenerate
expected values, fallback to weaker checks, suppress target failures, or
duplicate the target command directly.

## 11. Relationship To Phase 1 Release-Quality Chain

The Phase 1 chain remains accepted by Step-web-logger-054. Step-web-logger-059
corrected the Phase 1 target filter to restore Phase 1-only scope.

Phase 2 release-quality integration should be separate and additive. The Phase
2 label should not rename or broaden the Phase 1 label. A future Phase 2 pass
should not retroactively expand the Phase 1 accepted boundary.

## 12. Relationship To Step057 Phase 2 Implementation

Step-web-logger-057 implemented Phase 2 validator behavior. Step-web-logger-060
designs wrapper integration only.

Future release-quality integration will run the focused Phase 2 tests through
Makefile. A release-quality pass will not expand validator behavior, prove
replay correctness, prove extract / micro_episode integration, or prove
TypeScript compatibility.

## 13. Relationship To Shared UTF-16 Helper And Replay

Phase 2 validator behavior uses `kslog_schema::utf16_offsets`. The Phase 2
wrapper target should not call replay tests. The replay target remains
separate, replay correctness remains separate, and a Phase 2 pass does not
prove replay correctness.

## 14. Relationship To TypeScript Logger

The Phase 2 target does not modify TypeScript. It does not prove that the
TypeScript logger emits all required fields. TypeScript/Rust compatibility
remains separate.

## 15. Relationship To SHA-256 Hash Compatibility

The Phase 2 target does not implement a SHA-256 helper, does not run
TypeScript/Rust hash vector checks, and does not prove current TS/Rust hashes
match.

## 16. Relationship To Event Durability

The Phase 2 target does not implement event durability. Queue / IndexedDB /
ack / retry / dedup remain future work. Server-side idempotency / event_id
dedup remains future work. Ordering and delivery durability remain open.

## 17. No-Oracle / Synthetic-Only Boundary

The tests use synthetic fixtures. They do not introduce real participant data,
raw learner text, final_text / observed_after_text / gold labels / post-hoc
annotation, model performance validation, or test-set tuning. No-oracle
constraints are not relaxed.

## 18. Public-Safe Diagnostics Design

The wrapper should record labels and commands only. The Makefile target may
produce standard Cargo test output, but docs/status should not copy raw Cargo
output. Future status markers should record metadata/count-only summaries.

Docs should not copy raw test output blocks, raw fixture bodies, full fixture
JSON bodies, or raw source / selected / inserted / deleted text. Reason-code
and count summaries are acceptable. Private and absolute local paths must not
be copied into docs.

Raw remote logs may contain CI runner paths, so status docs should use
metadata-only summaries.

## 19. Proposed Future Step-web-logger-061 Scope

Step-web-logger-061 should be an implementation Step. It should modify only
`scripts/check_release_quality.sh` as needed to add one label/command pair:

- label:
  `release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`
- command:
  `make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

The insertion point should be after the Phase 1 label and before the Rust
UTF-16 replay integration label.

Step061 should not modify Makefile, Rust code, Rust tests, fixture JSON,
TypeScript/Python code, or CI workflow. It should update README and full
technical specification related docs because release-quality visible behavior
changes.

Recommended Step061 checks:

- Phase 1 target
- Phase 2 target
- full validator tests
- schema/replay regressions
- workspace/fmt/clippy
- position_unit fixture contract validator
- `make check-release-quality`
- new Phase 2 label appears
- new Phase 2 command appears
- final `release_quality_check: ok`
- Phase 2 target appears after Phase 1 label and before replay label
- output remains public-safe

## 20. Future Run Record / Status Marker Staging

Recommended later steps:

- Step-web-logger-062: Phase 2 release-quality remote/manual run record
  workflow design
- Step-web-logger-063: Phase 2 release-quality status marker
- Step-web-logger-064: Phase 2 release-quality final safety review

The status marker should not be created before release-quality integration
exists. Remote GitHub Actions metadata should be preferred. Local/manual
fallback should be explicitly marked if remote metadata is unavailable. The
final safety review should accept only bounded Phase 2 UTF-16 numeric metadata
validation, not replay correctness or TypeScript compatibility.

## 21. Future Status Marker Fields Preview

Future status marker should record:

- evidence_source
- local_fallback_used
- remote_metadata_available
- release-quality label observed
- command observed
- final `release_quality_check: ok` observed
- target command
- underlying command
- focused test count=8
- failed test count=0
- phase2_utf16_numeric_validation_checked=true
- doc_len_before_utf16_mismatch_checked=true
- doc_len_after_utf16_mismatch_checked=true
- start_greater_than_end_checked=true
- offset_beyond_utf16_length_checked=true
- offset_inside_surrogate_pair_checked=true
- invalid_utf16_boundary_checked=true
- detectable_byte_index_misuse_boundary_checked=true
- replay_invoked=false
- extract_integration_checked=false
- micro_episode_integration_checked=false
- typescript_logger_checked=false
- hash_compatibility_checked=false
- event_durability_checked=false
- production_readiness_claimed=false
- real_data_readiness_claimed=false
- performance_claims_present=false

## 22. Non-Equivalence Cautions

- release-quality integration design is not wrapper implementation
- Phase 2 release-quality integration will not prove production readiness
- Phase 2 release-quality pass will not prove replay correctness
- Phase 2 release-quality pass will not prove extract integration
- Phase 2 release-quality pass will not prove micro_episode integration
- Phase 2 release-quality pass will not prove TypeScript compatibility
- Phase 2 release-quality pass will not prove hash compatibility
- Phase 2 release-quality pass will not prove event durability
- synthetic-only validation is not real-data readiness

## 23. Non-Claims

This design does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, hash compatibility
implementation completion, TypeScript/Rust vector check implementation,
current TypeScript/Rust hash equality, event durability implementation, data
collection readiness, or deployment readiness.

## 24. Recommended Next Step

Recommended next step:

`Step-web-logger-061: integrate Rust validator Phase 2 UTF-16 numeric metadata target into release-quality wrapper`

Step061 should be an implementation Step. It should modify
`scripts/check_release_quality.sh`, add one label/command pair, and call
`make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.

Step061 should not modify Makefile, Rust code/tests, fixture JSON,
TypeScript/Python code, or CI workflow. It should update README and full
technical specification docs because release-quality visible behavior changes,
but it should not create a status marker or claim production or real-data
readiness.
