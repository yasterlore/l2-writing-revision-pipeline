# Milestone 05 Final Docs-Only Release Review

This document reviews the Milestone 05 Makefile orchestration documentation
before public release.

It is docs review documentation only. It does not change the Makefile, Makefile
targets, shell scripts, GitHub Actions workflows, tests, implementation logic,
scorer logic, scoring formula, tie-break behavior, manifest schema, fixtures,
or weights. It is not a performance evaluation.

## 1. Purpose

The purpose of this review is to confirm that the Milestone 05 documentation is
ready as public-facing docs-only release material.

This review checks that the shell orchestration modernization and Makefile
adoption docs are linked, internally consistent, and safe to publish. It also
checks that the external critique response remains appropriately scoped and
does not overclaim production quality, research validity, or model performance.

## 2. Review Scope

The review scope covers Step 145 through Step 152:

- orchestration modernization design
- shell script inventory and task categories
- task-runner selection
- Makefile thin entrypoint implementation
- Makefile safety review
- parallel execution and shared `tmp/` safety
- sequential guidance
- Milestone 05 recap

This review does not cover scorer, model, real-data, manifest schema, fixture,
workflow, CI trigger, or test-code changes.

## 3. Docs Inventory

Milestone 05 documents:

- [Orchestration modernization design](orchestration_modernization_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)

Related navigation and checklist documents:

- [Documentation index](README.md)
- [Public release checklist](public_release_checklist.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)

The documentation path is intentionally layered: modernization design, script
inventory, task-runner selection, Makefile adoption review, parallel/tmp safety
design, recap, and this final docs-only review.

## 4. Current Makefile State Check

Current Makefile state:

- the Makefile exists
- the default target is `help`
- the Makefile is a thin command menu
- `check-release-quality` calls the existing release-quality wrapper
- `check-summary-flow` preserves the required order:
  `summary -> manifest sync -> diagnostic distribution`
- `check-all` delegates to `check-release-quality`
- `.NOTPARALLEL` is present
- the Makefile does not cat raw generated bodies
- existing shell scripts remain the compatibility layer and source of behavior

The Makefile is not presented as a replacement pipeline implementation.

## 5. Public Release Checklist Alignment

The public release checklist aligns with Milestone 05 by:

- linking to the orchestration modernization design
- linking to the shell script inventory and task-runner selection docs
- naming `scripts/check_release_quality.sh` and `make check-release-quality`
  as normal release-quality entrypoints
- linking to the Makefile entrypoint safety review
- linking to the parallel/tmp safety design
- recommending `make check-summary-flow` instead of parallel summary-related
  targets
- linking to the Milestone 05 recap

The checklist continues to forbid raw logs, JSONL bodies, summary bodies,
marker bodies, diagnostic bodies, config bodies, and candidate score rows. It
does not treat Makefile success as research performance. It also explains the
Airflow / Dagster non-adoption as a stage-appropriate decision rather than an
ignored concern.

## 6. Safety Review

The Milestone 05 docs preserve these safety boundaries:

- no real participant data
- no raw JSONL body
- no summary, marker, diagnostic, or config body
- no candidate score rows
- no expected action details used as scoring feedback
- no F1, accuracy, calibration, learner-state estimation, or performance
  metrics
- no production readiness or data-collection readiness claim

The docs describe command organization and orchestration risk only.

## 7. Implementation Non-Change Review

Milestone 05 docs do not claim or require changes to:

- scorer logic
- scoring formula
- tie-break behavior
- manifest schema
- summary hash behavior
- per-case diagnostic consistency
- actual config fixtures
- existing shell script behavior
- GitHub Actions workflows
- CI triggers or job structure
- E2E summary generator logic

The Makefile adoption is framed as a thin entrypoint and not as a semantic
pipeline rewrite.

## 8. External Critique Response Review

The external critique response is appropriately scoped:

- valid concerns about shell orchestration are acknowledged
- dependency visibility, retry behavior, failure classification, and structured
  logging are treated as real future concerns
- immediate Airflow or Dagster adoption is avoided
- existing shell scripts remain as a compatibility layer
- Makefile thin entrypoints provide a low-risk improvement
- future Python or Rust orchestration remains an option
- no claim is made that the orchestration is production-grade

The response is neither dismissive nor overbuilt.

## 9. Known Remaining Items

Known remaining items:

- direct script parallel execution can still race on shared `tmp/` output
- stage metadata and failure classification remain lightweight
- Markdown link check remains a manual note inside the release-quality wrapper
- lock file and per-run temp directory isolation are not implemented
- CI Makefile adoption is not decided
- Python or Rust orchestration helper is not implemented

These are non-blocking follow-ups for the current docs-only milestone.

## 10. Release Readiness Judgment

Judgment: Milestone 05 docs are ready as docs-only release material.

Blockers:

- none identified in this review

Non-blocking follow-ups:

- formalize a Markdown link checker command
- decide whether CI should call Makefile targets later
- add structured stage summaries if script output becomes hard to classify
- revisit lock files or per-run temp isolation if shared `tmp/` races recur
- consider a Python or Rust orchestrator if Makefile and shell wrappers become
  too complex

Must not be claimed publicly:

- model validation
- research readiness
- production readiness
- data-collection readiness
- performance improvement
- F1, accuracy, calibration, or learner-state estimation
- proof that Makefile success validates research quality

## 11. Beginner Notes

A docs-only release review checks whether documentation is clear, linked, and
safe to publish. It does not certify research quality or production readiness.

Makefile adoption is treated as a milestone because it changes how developers
discover and run commands, even though it does not change the underlying
pipeline logic.

Shell scripts remain because they are the current working compatibility layer.
The Makefile calls them instead of copying or replacing their behavior.

Makefile success means the configured commands passed. It does not prove model
quality or research performance.

Airflow and Dagster are not used yet because the project is still
synthetic-only and local/CI-oriented. Heavy orchestration should wait until
production-like scheduling, durable run history, and monitoring are real
requirements.

## Related Documents

- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Orchestration modernization design](orchestration_modernization_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md)
- [Public release checklist](public_release_checklist.md)
