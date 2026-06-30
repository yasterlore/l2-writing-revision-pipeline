# Full Technical Specification External Review Checklist

This checklist supports external review of
`docs/full_technical_specification.md` after Step-pretec-doc5 hardening. It is
a review aid, not an implementation change, not a production readiness
certification, not a real-data readiness certification, and not model
performance evidence.

The checklist should be used with:

- `docs/full_technical_specification_source_inventory.md`
- `docs/full_technical_specification.md`
- `docs/full_technical_specification_coverage_validation.md`
- `docs/full_technical_specification_final_safety_review.md`
- repository evidence in `Makefile`, `.github/workflows/`, `scripts/`,
  `python/`, `crates/`, `apps/logger-web/`, `tests/fixtures/`, and
  `docs/status/`

## 1. Review Scope

Confirm that the full technical specification is treated as a consolidated
technical specification draft based on repository scan evidence. It should not
be treated as an absolute guarantee of no omissions.

Reviewers should verify:

- source inventory coverage is traceable
- implementation status is explicit
- non-proofs are explicit
- unresolved or unconfirmed areas are marked as `not yet confirmed from
  repository scan` or `next step verification required`
- no implementation, workflow, fixture, or runtime behavior is inferred beyond
  repository evidence

## 2. Coverage Against Inventory

Check the full specification against the source inventory:

- root files and package/workspace metadata
- README and SECURITY posture
- Makefile targets
- release-quality wrapper labels
- GitHub Actions workflows
- Python module CLIs and validators
- Rust crates and CLI
- logger-web TypeScript/Vite app
- fixture root families and fixture READMEs
- schema/version families
- docs/status marker families
- safety and no-oracle policies

Any missing component should be recorded as a coverage follow-up, not silently
filled by inference.

## 3. Implementation Status Matrix

Confirm that each major component is categorized correctly:

- implemented
- fixture-only
- validator-only
- standalone Makefile target
- release-quality integrated
- remote status recorded
- docs-only
- not implemented
- future work

Pay special attention that the following remain marked with their current
implementation boundaries:

- artifact writer CLI integration runtime: initial metadata-only runtime
  module exists after Step489, with a Step491 standalone Makefile smoke target
  and no release-quality runtime wrapper integration yet
- artifact body generation CLI integration
- manifest writer integration
- manifest body generation
- production readiness review
- real-data readiness review

## 4. Non-Proofs

Confirm that the specification does not claim:

- production readiness
- real-data readiness
- model performance
- F1 achievement
- accuracy achievement
- ECE achievement
- AURCC achievement
- learner-state estimator correctness
- generated policy quality
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- privacy/legal/IRB readiness

## 5. Public-Safe Documentation Review

Confirm that public docs do not contain:

- raw GitHub Actions logs
- full job output
- fixture JSON body examples
- request body examples
- pointer body examples
- expected body examples
- written file JSON body examples
- manifest body examples
- artifact body payload examples
- generated policy body examples
- raw rows
- logits or probabilities
- private path examples
- absolute local path examples
- raw learner text
- real participant data
- screenshots containing raw logs

Field names, schema names, target names, status labels, reason-code names, and
safe count-only summaries may be used when they remain body-free.

## 6. CLI / Makefile / CI Coverage

Confirm that the specification covers:

- Python module CLI argument families
- Rust `kslog` CLI command families
- shell script checks
- npm scripts for logger-web
- Makefile target command mapping
- release-quality wrapper order
- CI workflow setup and action versions
- Release Quality workflow setup and action versions

Reviewers should verify that command examples remain command-level only and do
not include raw logs or body payload examples.

## 7. Fixture / Validator / Schema Coverage

Confirm that the specification covers:

- fixture root family purpose and counts where safely confirmed
- validator module and CLI relation
- Makefile target relation
- release-quality inclusion where confirmed
- schema/result/validation version families
- separation between stable schema names and synthetic invalid markers
- no-oracle, synthetic-only, metadata-only, and body-free restrictions

Fixture JSON bodies must not be copied into the specification or checklist.

## 8. Status Marker Review

Confirm that status markers are summarized as public-safe records:

- marker path
- related component
- status type
- raw logs stored: no
- what the marker proves
- what the marker does not prove

Run identities may be referenced only when already recorded in public-safe
marker docs and should not be expanded with raw logs.

## 9. Logger-Web Review

Confirm logger-web coverage against repository evidence:

- TypeScript and Vite package metadata
- npm scripts
- raw event helper tests
- in-memory synthetic event recording
- download behavior
- no server send / no localStorage / no console text logging statements in
  repository docs
- limitations and non-readiness claims

Do not treat logger-web checks as deployment readiness or real participant
collection readiness.

## 10. Rust Crate Review

Confirm Rust coverage against workspace and crate evidence:

- `kslog_schema`
- `kslog_validate`
- `kslog_replay`
- `kslog_extract`
- `kslog_micro_episode`
- `kslog_no_oracle_audit`
- `kslog_cli`

Review crate roles, tests/checks, CLI relation, and no-oracle/safe-view
relation. Do not infer API signatures that are not confirmed by source or
README files.

## 11. Final Review Notes

Before treating the specification as external-review-ready, confirm:

- high and medium coverage gaps remain closed or explicitly reopened
- low-priority hardening is summarized at external-review level
- the final safety and non-proof review has been read
- no raw payloads or raw logs are introduced during review
- unresolved items remain listed
- future runtime integration work remains separate

This checklist does not itself prove production readiness, real-data readiness,
model performance, or legal/privacy readiness.
