# Schema-Level Position Unit Fixture Validator Release Quality Integration Design

## 1. Title

Schema-Level Position Unit Fixture Validator Release Quality Integration Design

## 2. Scope

This is a release-quality-integration-design / docs-only step.

This step makes no release-quality wrapper changes, no Makefile changes, no
Rust code changes, no TypeScript code changes, no Python code changes, no
tests changes, no fixture JSON changes, no CI workflow changes, and no
`package.json` / `Cargo.toml` / `Cargo.lock` changes.

This step makes no schema behavior changes, no validator behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-034 created the schema-level `position_unit` fixture root.
Step-web-logger-036 implemented the Python-first fixture validator.
Step-web-logger-038 added the Makefile target, and that target currently
passes.

This document designs release-quality integration only. It does not modify
`scripts/check_release_quality.sh`. Rust `kslog_schema` / `kslog_validate`
position-unit behavior remains future work.

## 4. Current Makefile Target Audit

Current Makefile target:

- target name: `check-web-logger-position-unit-fixtures`
- help text: `Run Web logger position_unit fixture contract validation`
- command:
  `PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
- placement: near the existing Web logger fixture validation targets
- output boundary: public-safe summary-only key=value metadata
- Step-web-logger-038 direct target result: pass

Observed validator counts:

- `total_cases=17`
- `valid_cases=5`
- `invalid_cases=11`
- `legacy_cases=1`
- `jsonl_record_count=24`
- `matched_cases=17`
- `mismatched_cases=0`

The target validates fixture contracts only. It does not prove Rust schema
behavior, Rust validator behavior, replay correctness, extract /
micro_episode behavior, TypeScript/Rust compatibility, event durability,
production readiness, real-data readiness, or model performance.

## 5. Current Release-Quality Wrapper Audit

Current Web logger release-quality checks:

- `release_quality_check: web logger unicode hash vector fixture validation`
- `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

Current relative order:

1. Web logger Unicode/hash fixture validation
2. Rust UTF-16 offset conversion and replay integration
3. learner-state target group

The wrapper currently calls Makefile targets rather than duplicating the
underlying Python or Cargo commands. The learner-state target group starts
after the Web logger checks.

The wrapper does not yet call `check-web-logger-position-unit-fixtures`.

## 6. Recommended Release-Quality Label

Recommended label:

`release_quality_check: web logger position_unit fixture contract validation`

This label is intentionally narrow:

- clearly identifies Web logger scope
- clearly identifies the `position_unit` fixture contract
- does not imply Rust schema implementation
- does not imply Rust validator implementation
- does not imply validate / extract / micro_episode integration
- does not imply TypeScript/Rust compatibility
- does not imply event durability
- does not imply production readiness

Rejected labels:

- `release_quality_check: web logger schema validation`: too broad; it could
  be read as Rust schema behavior.
- `release_quality_check: web logger position_unit implementation`: too broad;
  it could be read as completed runtime or schema behavior.
- `release_quality_check: web logger Unicode correctness`: too broad; this
  fixture contract does not cover all Unicode behavior.
- `release_quality_check: web logger production validation`: too broad; this
  check is not production validation.

## 7. Recommended Command

Recommended command:

`make check-web-logger-position-unit-fixtures`

The wrapper should call the Makefile target and should not duplicate the
Python command directly. The Makefile target remains the command source of
truth.

The command should not run focused tests, run Rust schema validation, run
replay, run extract / micro_episode, mutate fixtures, regenerate metadata, or
fall back to weaker checks.

## 8. Recommended Insertion Point

Recommended placement in `scripts/check_release_quality.sh`:

- after `release_quality_check: web logger unicode hash vector fixture validation`
- before `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`

Rationale:

- keeps Web logger fixture contract checks grouped
- validates the schema-level fixture contract before the replay-focused Rust
  UTF-16 check
- preserves the Web logger block before learner-state checks
- does not move unrelated learner-state chains
- does not remove existing checks
- does not reorder unrelated checks

Repository inspection shows this is the safest nearby placement because the
wrapper already groups the Unicode/hash fixture check and Rust UTF-16 replay
check before learner-state checks.

## 9. Proposed Future Step-web-logger-040 Scope

Step-web-logger-040 should:

- modify only `scripts/check_release_quality.sh` as needed for wrapper
  integration
- add one label:
  `release_quality_check: web logger position_unit fixture contract validation`
- add one command:
  `make check-web-logger-position-unit-fixtures`
- preserve insertion point
- not modify Makefile
- not modify Python validator
- not modify focused tests
- not modify fixtures
- not modify Rust code
- not modify TypeScript code
- not modify CI workflow
- update README and full technical specification related docs because
  release-quality visible behavior changes
- run `make check-web-logger-position-unit-fixtures`
- run `make check-release-quality`
- confirm the new label appears
- confirm the command appears
- confirm final `release_quality_check: ok`
- confirm output remains public-safe summary-only

## 10. Expected Release-Quality Output After Future Integration

Expected release-quality output should include:

- `release_quality_check: web logger position_unit fixture contract validation`
- `command: make check-web-logger-position-unit-fixtures`
- `mode=web_logger_position_unit_fixture_validation`
- `validation_status=pass`
- `total_cases=17`
- `valid_cases=5`
- `invalid_cases=11`
- `legacy_cases=1`
- `jsonl_record_count=24`
- `matched_cases=17`
- `mismatched_cases=0`
- `position_unit_policy_checked=true`
- `content_suppressed=true`
- `fixture_body_suppressed=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- private and machine-local path counts at 0
- payload / learner-text / real-data-marker / logits / probabilities /
  performance-body counts at 0
- production / real-data / performance claims false
- final `release_quality_check: ok`

## 11. Expected Failure Semantics

Release-quality should fail if:

- Makefile target exits nonzero
- case index JSON is invalid
- JSONL is invalid
- fixture file is missing
- case ID is duplicated
- fixture path escapes the fixture root
- count mismatch is detected
- expected reason-code mismatch is detected
- forbidden no-oracle field is detected
- private or machine-local path marker is detected
- unredacted job-log marker is detected
- logits / probabilities marker is detected
- performance metric body marker is detected
- position-unit policy mismatch is detected
- UTF-16 metadata mismatch is detected

The wrapper should not repair fixtures, rewrite fixture files, regenerate
metadata, fall back to weaker checks, suppress target failures, or print raw
fixture bodies.

## 12. Public-Safe Output Boundary

Allowed output:

- label
- command
- validator mode
- schema / fixture version
- case counts
- reason-code counts
- status
- boolean safety flags
- zero-count safety scans

Forbidden output:

- raw event JSON body
- full fixture JSON body
- source text
- selected text
- inserted/deleted text by default
- private paths
- absolute paths
- learner-originated raw text
- participant-originated data
- logits / probabilities
- performance metric body
- copied job-log blocks
- full job output
- Cargo log bodies

## 13. Future Run Record / Status Marker Staging

Recommended later staging:

- Step-web-logger-041: schema-level position_unit fixture validator
  release-quality remote/manual run record workflow design
- Step-web-logger-042: schema-level position_unit fixture validator
  release-quality status marker
- Step-web-logger-043: schema-level position_unit fixture validator
  release-quality final safety review

Status marker creation should wait until release-quality integration exists.
Remote GitHub Actions metadata should be preferred. Local/manual fallback
should be marked explicitly if remote metadata is unavailable. Final safety
review should accept only bounded fixture-contract validation, not Rust schema
implementation.

## 14. Relationship To Step-web-logger-038 Makefile Target

Step-web-logger-038 added the Makefile target. Release-quality integration
should call that target, not duplicate the Python command. The Makefile target
remains the command source of truth. Release-quality integration does not
expand validator scope.

## 15. Relationship To Step-web-logger-036 Validator Implementation

Step-web-logger-036 implemented the fixture contract validator.
Release-quality integration only runs the validator through Makefile.
Release-quality pass will not prove Rust schema behavior, Rust validator
behavior, or replay correctness.

## 16. Relationship To Step-web-logger-034 Fixture Root

The fixture root remains unchanged. The release-quality target validates the
fixture contract. The wrapper should not mutate the fixture root or regenerate
fixture metadata. Synthetic-only / no-oracle / public-safe boundaries remain
unchanged.

## 17. Relationship To Step-web-logger-031 Replay Integration

Step-web-logger-031 accepted the `kslog_replay` focused replay boundary.
Position-unit fixture validation is a schema fixture contract boundary. Replay
pass does not prove fixture contract, and fixture validation pass does not
prove replay correctness. These boundaries remain distinct.

## 18. Relationship To Future Rust Schema / Validator Implementation

Release-quality integration validates fixture contract only. Rust
`kslog_schema` / `kslog_validate` implementation remains future work.
Release-quality pass should not be described as completed schema-level policy
behavior. The fixture target can become a prerequisite for future Rust
validator implementation.

## 19. Relationship To TypeScript / Rust Hash/Helper Work

This release-quality integration design does not implement a Rust SHA-256
helper, a TypeScript SHA-256 helper, or TypeScript/Rust vector checks. It does
not prove current TypeScript and Rust hashes match. Hash compatibility remains
separate.

## 20. Relationship To Event Durability

This release-quality integration design does not implement event durability.
Queue / IndexedDB / acknowledgement / retry / dedup remain unimplemented.
Server-side idempotency / event_id dedup remains unimplemented. Ordering and
delivery durability are not solved.

## 21. Relationship To No-Oracle And Synthetic-Only Boundaries

The release-quality target validates the synthetic-only / no-oracle fixture
contract. It must not introduce participant-originated data, must not print
learner-originated raw text, must not introduce final/observed-after text
fields, must not introduce gold-label or post-hoc annotation fields, and must
not perform model performance validation. No-oracle constraints are not
relaxed.

## 22. Non-Equivalence Cautions

- Release-quality integration design is not wrapper implementation.
- Release-quality target pass will not prove Rust schema implementation.
- Release-quality target pass will not prove Rust validator implementation.
- Release-quality target pass will not prove replay correctness.
- Release-quality target pass will not prove extract integration.
- Release-quality target pass will not prove micro_episode integration.
- Release-quality target pass will not prove TypeScript/Rust compatibility.
- Release-quality target pass will not prove hash compatibility.
- Release-quality target pass will not prove event durability.
- Synthetic-only fixture validation is not real-data readiness.
- Release-quality pass is not production readiness.

## 23. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- validate integration completion
- extract integration completion
- micro_episode integration completion
- completed schema-level position-unit policy behavior
- release-quality wrapper integration for this position-unit fixture target
- Rust schema position-unit behavior
- Rust validator position-unit behavior
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 24. Recommended Next Codex Step

Recommended next step:

Step-web-logger-040: integrate schema-level position_unit fixture validator
into release-quality wrapper

Clarification:

- Step-web-logger-040 should be an implementation step.
- It should modify `scripts/check_release_quality.sh`.
- It should add one label / command pair.
- It should call `make check-web-logger-position-unit-fixtures`.
- It should not modify Makefile.
- It should not modify Python validator.
- It should not modify focused tests.
- It should not modify fixture JSON.
- It should not modify Rust code.
- It should not modify TypeScript code.
- It should update README and full technical specification related docs because
  release-quality visible behavior changes.
- It should not claim Rust schema / validator implementation.
- It should not claim production readiness or real-data readiness.

## 25. Step-web-logger-040 Implementation Note

Step-web-logger-040 implements this design by adding the release-quality check
to `scripts/check_release_quality.sh`.

Implemented release-quality check:

- label:
  `release_quality_check: web logger position_unit fixture contract validation`
- command: `make check-web-logger-position-unit-fixtures`
- insertion point: after Web logger Unicode/hash fixture validation and before
  Rust UTF-16 offset conversion and replay integration

The wrapper calls the Makefile target and does not duplicate the Python
validator command. This integration remains bounded to fixture contract
validation and does not modify Makefile, Python validator, focused tests,
fixture JSON, Rust schema / validator behavior, validate / extract /
micro_episode behavior, status markers, final safety review, event durability,
production readiness, real-data readiness, or model performance evidence.

## 26. Step-web-logger-041 Run Record Workflow Design

Step-web-logger-041 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote/Manual Run Record Workflow](web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_record_workflow.md).

The workflow design specifies how future Step-web-logger-042 should record
public-safe release-quality evidence for this wrapper integration. It does not
create a status marker, create a final safety review, modify the wrapper,
modify Makefile, modify validator code, modify tests, modify fixtures, or
implement Rust schema / validator behavior.

## 27. Step-web-logger-042 Remote Status Marker

Step-web-logger-042 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote Run Status](status/web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_status.md).

The marker records public-safe remote release-quality metadata for this
integration: observed label, command, final ok label, 17-case / 24-record
validator summary, reason-code counts, unavailable metadata, and safety flags.
It does not create a final safety review, modify the wrapper, modify Makefile,
modify validator code, modify tests, modify fixtures, or implement Rust schema
/ validator behavior.

## 28. Step-web-logger-043 Final Safety Review

Step-web-logger-043 adds
[Schema-Level Position Unit Fixture Validator Release Quality Chain Final Safety Review](web_logger_schema_position_unit_fixture_validator_release_quality_chain_final_safety_review.md).

The review accepts only the release-quality-integrated and remote-status-recorded
fixture contract validation boundary for the fixed 17-case synthetic matrix. It
does not modify the wrapper, Makefile, validator code, tests, fixtures, or
Rust schema / validator behavior.
