# Rust UTF-16 Offset Conversion Helper Release Quality Integration Design

## 1. Title

Rust UTF-16 Offset Conversion Helper Release Quality Integration Design

## 2. Scope

This is a release-quality-integration-design / docs-only step.

This step makes no release-quality wrapper changes, no Makefile changes, no Rust code changes, no TypeScript code changes, no Python code changes, no tests changes, no fixture JSON changes, no CI workflow changes, and no package.json / Cargo.toml / Cargo.lock changes.

This step does not add broader replay / validate / extract / micro_episode runtime integration. It does not add event durability implementation, production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

This doc designs future release-quality integration for the Rust UTF-16 offset conversion helper focused test target.

This doc does not modify `scripts/check_release_quality.sh`.

The Makefile target already exists from Step-web-logger-017:

```text
check-web-logger-rust-utf16-offset-conversion
```

The Rust UTF-16 helper and focused tests already exist from Step-web-logger-015. Release-quality integration remains future work until Step-web-logger-019.

This design does not claim TypeScript/Rust hash compatibility and does not claim broader replay runtime integration.

## 4. Proposed Release-Quality Label

Proposed label:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

The label should be unique and should clearly identify the Rust UTF-16 offset conversion helper focused tests. It should not replace the existing Web logger Unicode/hash vector fixture validation, should not replace existing Rust checks, and should not imply broader replay integration, TypeScript compatibility, or production readiness.

## 5. Proposed Release-Quality Command

Proposed command:

```text
make check-web-logger-rust-utf16-offset-conversion
```

The release-quality wrapper should call the Makefile target rather than duplicating the Cargo command. The Makefile target remains the source of truth.

The command should be focused and deterministic. It should not require network access, should not require real data, should not modify fixture JSON, should not print raw `source_text`, should not print selected raw text, should not print the full fixture JSON body, and should fail if the focused Rust tests fail.

## 6. Proposed Insertion Point in scripts/check_release_quality.sh

The current wrapper has this relevant order:

- `release_quality_check: python checks`
- `release_quality_check: web logger unicode hash vector fixture validation`
- `release_quality_check: learner-state audit fixtures`

Recommended insertion point:

- after `release_quality_check: web logger unicode hash vector fixture validation`
- before `release_quality_check: learner-state audit fixtures`

This keeps both Web logger Unicode/hash checks together while preserving the existing Python checks and learner-state chains. Step-web-logger-019 should not move existing Python checks, move existing learner-state chains, replace existing Rust checks, remove unrelated checks, or reorder unrelated checks.

## 7. Expected Release-Quality Output

Expected label:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

Expected command line:

```text
command: make check-web-logger-rust-utf16-offset-conversion
```

Expected target behavior:

- runs `cargo test -p kslog_replay utf16`
- focused UTF-16 helper tests pass
- shared vector fixture reuse remains covered by focused Rust tests
- raw source text is not printed in normal output
- selected raw text is not printed in normal output
- full fixture JSON body is not printed in normal output

Expected public-safe summary in future final reports:

- `target_status=pass`
- `crate=kslog_replay`
- `test_filter=utf16`
- `shared_vector_fixture_reused=yes`
- `fixture_json_modified=no`
- `content_suppressed_boundary=maintained`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

Cargo test output may include test names and pass/fail counts. It must not include raw `source_text`, selected text, the full fixture JSON body, private paths, or real participant data.

## 8. Expected Failure Semantics

The wrapper should fail if the Makefile target exits nonzero.

Expected failure categories:

- helper test failure fails release-quality
- invalid shared vector expectations fail release-quality
- Rust compile error fails release-quality
- Cargo invocation failure fails release-quality
- fixture file missing during focused tests fails release-quality
- unsupported environment fails rather than silently skipping

The wrapper should not repair fixture data, regenerate shared vectors, rewrite expected offsets, fallback to weaker tests, or duplicate the Cargo command outside Makefile.

## 9. Preconditions for Step-web-logger-019

Already satisfied from Step-web-logger-015 and Step-web-logger-017:

- Rust helper exists
- focused Rust tests exist
- shared vectors are reused by focused tests
- Makefile target exists
- Makefile target passes
- `cargo test -p kslog_replay utf16` passes
- `cargo test -p kslog_replay` passes
- `cargo fmt --all -- --check` passes
- `cargo clippy -p kslog_replay -- -D warnings` passes
- `cargo test --workspace` passes
- fixture JSON unchanged
- Cargo.toml / Cargo.lock unchanged
- target output is public-safe

Step-web-logger-019 should still verify:

- `make help` includes the target
- `make check-web-logger-rust-utf16-offset-conversion` passes
- `cargo test -p kslog_replay utf16` passes
- `cargo test -p kslog_replay` passes
- `cargo fmt --all -- --check` passes
- `cargo clippy -p kslog_replay -- -D warnings` passes
- `scripts/check_release_quality.sh` diff is limited to one label and one command
- `make check-release-quality` passes after integration
- release-quality output remains public-safe
- forbidden claims are not introduced

## 10. Proposed Step-web-logger-019 Implementation Scope

Step-web-logger-019 should:

- update `scripts/check_release_quality.sh` only as needed
- add the release-quality label
- call `make check-web-logger-rust-utf16-offset-conversion`
- update minimal docs
- run `make check-release-quality`
- not modify Makefile
- not modify Rust helper code
- not modify focused tests
- not modify fixture JSON
- not modify TypeScript / Python code
- not add broader replay / validate / extract integration
- not add Rust SHA-256 helper
- not add TypeScript SHA-256 helper
- not add event durability

## 11. Relationship to Step-web-logger-017 Makefile Target

Step-web-logger-017 added the Makefile target. Step-web-logger-018 only designs wrapper integration and does not change the target.

Step-web-logger-019 may call the target from the wrapper. The Makefile target remains the command source of truth.

## 12. Relationship to Step-web-logger-015 Rust Helper Implementation

Step-web-logger-015 implemented the Rust helper and focused tests. Release-quality integration will reuse the focused test target through Makefile.

This design does not alter helper behavior and does not alter tests. The helper remains focused on UTF-16 offset to UTF-8 byte offset conversion. It does not compute hashes and does not prove TypeScript compatibility.

## 13. Relationship to Python Validator Chain

The Python validator release-quality chain is already release-quality-integrated and remote-status-recorded for the fixed 15-vector fixture contract.

The Rust UTF-16 helper target is separate. The Python validator target and Rust helper target are complementary. Passing the Python validator target does not prove Rust helper correctness. Passing the Rust helper target does not prove Python validator correctness.

Future release-quality should contain both checks when the Rust helper check is integrated.

## 14. Relationship to Broader Replay / Validate / Extract Integration

Release-quality integration of the focused helper target does not integrate the helper into replay runtime behavior, schema validation, revision extraction, or micro_episode context slicing.

Broader runtime integration should be a separate future chain. Focused helper tests passing is not broader Unicode correctness completion.

## 15. Relationship to TypeScript / Rust Hash/Helper Work

Release-quality integration of the Rust UTF-16 helper does not add a Rust SHA-256 helper, does not add a TypeScript SHA-256 helper, does not add TypeScript/Rust hash compatibility checks, and does not prove current TypeScript and Rust hashes match.

Future TypeScript/Rust vector checks should be separate targets and release-quality checks.

## 16. Relationship to Event Durability

This release-quality integration design does not add event durability. It does not add queue / IndexedDB / ack / retry / dedup. It does not add server-side idempotency / event_id dedup. It does not solve ordering or delivery durability.

Event durability remains a separate P0 chain.

## 17. Relationship to No-Oracle and Synthetic-Only Boundaries

Shared vectors are synthetic-only. No real participant data is used. No raw learner text is used.

No `final_text`, `observed_after_text`, gold labels, or post-hoc annotation are used. No model performance validation is performed. No-oracle constraints are not relaxed.

## 18. Public-Safe Diagnostics

Allowed diagnostics:

- release-quality label
- command
- test names
- pass/fail counts
- reason_code
- numeric UTF-16 offset metadata
- numeric UTF-8 byte offset metadata
- vector_id / case_id when needed
- count summary

Forbidden diagnostics:

- raw `source_text`
- raw selected text
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 19. Non-Equivalence Cautions

- Release-quality integration design is not release-quality integration implementation.
- Focused Rust helper target is not broader replay integration.
- Rust helper pass is not TypeScript compatibility.
- Rust helper pass is not Rust SHA-256 compatibility.
- Rust helper pass is not TypeScript logger hash correctness.
- Rust helper pass is not event durability.
- Shared vector reuse is not exhaustive Unicode coverage.
- Synthetic-only tests are not real-data readiness.
- Release-quality pass, once integrated, is not production readiness.

## 20. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness implementation completion
- hash compatibility implementation completion
- TypeScript / Rust vector checks
- TypeScript / Rust helper compatibility
- event durability implementation completion
- current TypeScript and Rust hashes match
- data collection readiness
- deployment readiness

## 21. Recommended Next Codex Step

Recommended next step:

Step-web-logger-019: integrate Rust UTF-16 offset conversion helper into release-quality wrapper

Clarification:

- Step-web-logger-019 should modify `scripts/check_release_quality.sh` only as needed.
- Step-web-logger-019 should add one label and one command.
- Step-web-logger-019 should update minimal docs.
- Step-web-logger-019 should run `make check-release-quality`.
- Step-web-logger-019 should not modify Makefile.
- Step-web-logger-019 should not modify Rust helper code.
- Step-web-logger-019 should not modify tests.
- Step-web-logger-019 should not modify fixture JSON.
- Step-web-logger-019 should not add broader replay integration.
- Step-web-logger-019 should not add TypeScript/Rust hash checks.
- Step-web-logger-019 should not add event durability.

## 22. Step-web-logger-019 Integration Status

Step-web-logger-019 adds the wrapper check:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

The wrapper command is:

```text
make check-web-logger-rust-utf16-offset-conversion
```

The check is inserted after `release_quality_check: web logger unicode hash vector fixture validation` and before `release_quality_check: learner-state audit fixtures`. It calls the Makefile target as the command source of truth and does not duplicate the Cargo command in the wrapper.

This status update records wrapper integration only. It does not change Makefile, Rust helper code, focused Rust tests, fixture JSON, CI workflow, broader replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust cross-language vector checks, or event durability.

## 23. Step-web-logger-020 Remote/Manual Run Record Workflow Design

Step-web-logger-020 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_record_workflow.md).

The workflow design plans a future public-safe status marker for the Step-web-logger-019 wrapper check. It does not create the status marker, change the wrapper, change Makefile, change Rust code or tests, change fixture JSON, change CI workflow, add broader runtime integration, add TypeScript/Rust hash work, or add event durability.
