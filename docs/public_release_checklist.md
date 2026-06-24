# Public Release Checklist

This checklist is for reviewing the repository as public GitHub research software.

It does not authorize real-data processing or public dataset release.

## 1. Data Safety

Confirm before public release:

- no real participant data is tracked
- no real raw event JSONL is tracked
- no private/manual/tmp output is tracked
- no private/local observation notes are tracked
- no participant text appears in docs
- no JSONL rows are pasted into docs
- no summary CSV bodies, diagnostic summary bodies, config bodies, or candidate
  score rows are pasted into docs
- `examples/` contains synthetic examples only
- `tests/fixtures/` contains synthetic fixtures only
- invalid fixtures are clearly synthetic and intentionally unsafe only for tests

Useful path checks:

```bash
git status --short
git ls-files
git ls-files | grep -E 'manual_outputs|tmp|private_data|real_data|participant_data|private_notes|local_notes|\.real\.jsonl|\.private\.jsonl'
```

Note: documentation filenames such as `private_real_data_readiness_checklist.md`
may contain the string `real_data`; that is a documentation path, not a data
file. Review grep hits by path and file type.

For path-derived false positives in forbidden-term checks, see
[forbidden-term path-safety test hardening design](forbidden_term_path_safety_test_hardening_design.md).
For follow-up helper adoption boundaries, see
[safe output scan helper adoption audit](safe_output_scan_helper_adoption_audit.md).
For diagnostic distribution smoke ordering, run the no-config summary first;
see [synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md).
For future atomic-write and completion-marker hardening, see
[synthetic E2E summary atomic write design](synthetic_e2e_summary_atomic_write_design.md).
For the future no-config summary marker or run-id manifest design, see
[synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md).
For checker-side marker validation, see
[synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md).
For future manifest schema hardening, see
[summary manifest schema hardening design](summary_manifest_schema_hardening_design.md).
For future strict manifest allowed-key validation, see
[summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md).
The current no-config manifest includes a required `manifest_schema_version`
checked by the diagnostic distribution smoke, and unknown manifest keys fail
closed for the current manifest schema.
The generator and checker share the current manifest schema constants from
`scripts/lib/summary_manifest_schema.sh`.
For a future schema constants sync check, see
[summary manifest schema sync check design](summary_manifest_schema_sync_check_design.md).
Run `scripts/check_summary_manifest_schema_sync.sh` after generating the
no-config summary manifest.
For release-quality ordering and future CI placement of that command, see
[summary manifest sync check release integration design](summary_manifest_sync_check_release_integration_design.md).
For a broader future release-quality command bundle order, see
[release-quality command bundle design](release_quality_command_bundle_design.md).
For a staged response to shell-script orchestration risk, see
[orchestration modernization design](orchestration_modernization_design.md);
do not introduce a task runner or scheduler without a separate implementation
step.
Before designing a Makefile or justfile target set, review
[shell script inventory and task category design](shell_script_inventory_task_category_design.md).
Before implementing a task runner, review
[task runner selection design](task_runner_selection_design.md).
For the current normal success-path wrapper, run
`scripts/check_release_quality.sh` or the thin Makefile alias
`make check-release-quality`; Markdown link check remains manual unless a
dedicated project command is added later.
Before expanding Makefile usage, review
[Makefile entrypoint safety review](makefile_entrypoint_safety_review.md).
For summary-flow parallel execution and shared `tmp/` output guidance, review
[Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md).
Use `make check-summary-flow` rather than parallel summary-related targets.
For the consolidated Step 145-151 Makefile adoption and orchestration
modernization checkpoint, see
[Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md).
Before treating Milestone 05 docs as release-ready, review
[Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md).
Before creating a short public-safe Milestone 05 marker, review
[Milestone 05 status marker design](milestone_05_status_marker_design.md).
For the short public-safe Milestone 05 marker, see
[Milestone 05 status](status/milestone_05_status.md).
Before returning to research-pipeline implementation after Makefile adoption,
review the
[research pipeline next-phase plan](research_pipeline_next_phase_plan.md).
Before implementing any learner-state estimator, review the
[learner-state input representation design](learner_state_input_representation_design.md).
Before implementing a learner-state sequence exporter, review the
[synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md).
Before implementing learner-state sequence schema code or exporter files, review
the
[learner-state sequence schema design](learner_state_sequence_schema_design.md).
Before implementing learner-state sequence audit code or trusting exporter
output, review the
[learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md).
Before creating learner-state sequence audit fixture files or audit result
schemas, review the
[learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md).
Before adding learner-state sequence audit fixture directories or files, review
the
[learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md).
For future CI integration of that wrapper, see
[release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md).
For a future manual GitHub Actions workflow option, see
[release-quality manual workflow design](release_quality_manual_workflow_design.md).
The current manual workflow is `.github/workflows/release-quality.yml` and can
run the release-quality wrapper from GitHub Actions on demand.
Before relying on its first remote run, use the
[release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md).
After the first remote run, record only safe high-level status with the blank
[release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md).
If the remote run succeeds with a GitHub Actions Node runtime warning, track it
with
[GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
before changing workflow files.
Before editing action versions, use the
[release-quality action version update plan](release_quality_action_version_update_plan.md).
After action-version updates, rerun the manual workflow and record only the safe
warning status summary.
Before adding any public note about that rerun, use
[release-quality action update remote-run record workflow](release_quality_action_update_remote_run_record_workflow.md).
Before changing existing push/pull-request CI action versions, use
[existing CI action versions audit design](existing_ci_action_versions_audit_design.md).
The current existing CI checkout action has been minimally updated; confirm the
next remote CI or PR run with a safe warning-status summary only.
Before adding any public note about that remote CI run, use
[existing CI checkout update remote-run record workflow](existing_ci_checkout_update_remote_run_record_workflow.md).
For the consolidated CI maintenance checkpoint, see
[milestone 04 CI maintenance recap](milestone_04_ci_maintenance_recap.md).
Before treating Milestone 04 docs as release-ready, review
[milestone 04 final docs-only release review](milestone_04_final_docs_only_release_review.md).
For the short public-safe Milestone 04 status marker, see
[milestone 04 status](status/milestone_04_status.md). Its design is
[milestone 04 status marker design](milestone_04_status_marker_design.md).
The marker must not include raw logs, run URLs with private context, or
performance claims.

## 2. Ignore Rules

Confirm `.gitignore` blocks:

- `manual_outputs/`
- `tmp/`
- `private_data/`
- `real_data/`
- `participant_data/`
- `private_notes/`
- `local_notes/`
- `*.real.jsonl`
- `*.private.jsonl`
- local `.env` and secret-looking files

Use placeholder paths only:

```bash
git check-ignore tmp/<placeholder>.jsonl
git check-ignore manual_outputs/<placeholder>.jsonl
git check-ignore private_data/<placeholder>.real.jsonl
git check-ignore real_data/<placeholder>.private.jsonl
```

## 3. README and Docs

Confirm README explains:

- project purpose
- language architecture
- current pipeline
- synthetic-only policy
- no-oracle policy
- quick start commands
- what is implemented
- what is not implemented
- security and privacy notice
- license placeholder status

Confirm docs link to:

- `docs/milestone_01_pipeline_recap.md`
- `docs/milestone_02_synthetic_evaluation_recap.md`
- `docs/milestone_03_config_aware_diagnostic_infrastructure_recap.md`
- `docs/milestone_03_final_docs_only_release_review.md`
- `docs/milestone_04_ci_maintenance_recap.md`
- `docs/milestone_04_final_docs_only_release_review.md`
- `docs/milestone_04_status_marker_design.md`
- `docs/status/milestone_04_status.md`
- `docs/private_real_data_readiness_checklist.md`
- `docs/observation_note_storage_and_review_workflow.md`
- `docs/filled_observation_note_public_sharing_checklist.md`
- `docs/synthetic_e2e_pipeline.md`
- `docs/evaluation_spec.md`
- `docs/03_no_oracle_policy.md`
- `SECURITY.md`

## 4. License

`LICENSE` is currently a placeholder, not a final open-source license.

The Milestone 03
[final docs-only release review](milestone_03_final_docs_only_release_review.md)
is an internal checkpoint and does not resolve this license placeholder.

Before public release:

- choose the final project license
- replace the placeholder with the complete license text
- make the README license notice match the final LICENSE file
- confirm dependency license compatibility if needed
- confirm whether repository citation metadata is needed
- if citation metadata is added later, make it match the chosen release policy

Until this is resolved, do not present the repository as fully licensed and do
not imply that reuse, redistribution, or modification terms are finalized.

## 4.1 Repository Metadata TODO

Before formal public release, decide whether to add or update:

- repository description
- topics / keywords
- citation metadata such as `CITATION.cff`
- release notes
- authorship and acknowledgement wording
- funding or institutional metadata, if applicable

Any metadata should match the final license, data policy, and release policy.

## 5. Security

Confirm:

- `SECURITY.md` matches current policy
- no secrets are present
- no API keys, tokens, passwords, or private identifiers are present
- JSONL input is treated as untrusted
- no network access is introduced without documentation
- unsafe Rust, unsafe DOM APIs, `eval`, `exec`, and pickle loading are avoided
- config support remains explicit-only
- no hidden config loading or environment-variable config loading is introduced

## 6. No-Oracle Policy

Confirm docs state that candidate generation, scoring, ranking, and learner-state work must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- answer key
- future edits
- post-hoc annotations
- `local_context_after_observed`

Synthetic expected actions must be used only after scoring for evaluation wiring.

Configs must not be tuned from expected actions. Config-enabled E2E and
config-enabled summaries must remain explicit and separate from no-config
summaries.

For learner-state sequence audit fixtures, confirm that
[`tests/fixtures/learner_state_sequence_audit/`](../tests/fixtures/learner_state_sequence_audit/README.md)
remains synthetic-only and that public docs describe fixture case names,
categories, and reason codes without copying JSONL rows, manifest bodies, raw
text, or label contents.

Before adding learner-state sequence audit code, review the
[learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
and confirm that future output remains safe, count-only, and fail-closed.
After audit code is present, run the learner-state sequence audit fixture tests
through the normal Python test command and confirm they do not print JSONL row
bodies, manifest bodies, raw text, private paths, or label contents.
Before adding a learner-state sequence audit CLI, review the
[learner-state sequence audit CLI design](learner_state_sequence_audit_cli_design.md)
and confirm stdout, JSON output, and exit codes remain safe and count-only.
After CLI implementation, run CLI smoke tests through the normal Python test
command and confirm CLI stdout/stderr do not include JSONL rows, manifest
bodies, label contents, raw text, private paths, or expected action bodies.
Before connecting the CLI to Makefile, release-quality, or CI, review the
[learner-state sequence audit CLI integration design](learner_state_sequence_audit_cli_integration_design.md)
and confirm staged integration keeps logs safe and count-only.
Before adding the learner-state audit Makefile target to the release-quality
wrapper, review the
[learner-state sequence audit release-quality integration design](learner_state_sequence_audit_release_quality_integration_design.md)
and confirm wrapper logs remain safe and count-only.
After wrapper integration, confirm `scripts/check_release_quality.sh` runs the
learner-state audit fixture check through the Makefile target without printing
JSONL rows, manifest bodies, label bodies, private paths, or expected action
bodies.
Before recording any remote/manual release-quality result after this wrapper
integration, review the
[learner-state audit release-quality remote-run record workflow](learner_state_audit_release_quality_remote_run_record_workflow.md)
and record only safe high-level status. Do not paste raw workflow logs,
fixture rows, label bodies, manifest bodies, private paths, expected action
bodies, or performance claims into public docs.
The public-safe remote/manual status marker is
[learner-state audit release-quality remote run status](status/learner_state_audit_release_quality_remote_run_status.md);
it records workflow success and learner-state audit fixture inclusion without
copying raw logs or output bodies.
For the broader learner-state audit infrastructure recap, review
[Milestone 06 learner-state audit infrastructure recap](milestone_06_learner_state_audit_infrastructure_recap.md)
and confirm it does not claim model performance, learner-state estimator
correctness, real-data readiness, production data collection validity, or new
metric evidence.
Before implementing a learner-state sequence exporter, review
[learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
and confirm the future exporter keeps features, labels, and manifests separate,
runs the learner-state sequence audit, uses past-only windows, and emits only
safe/count-only summaries.
Before creating exporter input fixture files, review
[learner-state sequence exporter input fixture design](learner_state_sequence_exporter_input_fixture_design.md)
and confirm the fixture contract keeps safe episode inputs, candidate scores,
diagnostics, synthetic labels, grouping metadata, and expected output contracts
separate without copying fixture bodies into docs.
After creating exporter input fixtures, confirm
[`tests/fixtures/learner_state_sequence_exporter/`](../tests/fixtures/learner_state_sequence_exporter/README.md)
remains synthetic-only and contains no raw learner text, private paths,
real participant data, future fields, or label fields in feature-side inputs.
After implementing the minimal exporter module, run the normal Python tests and
confirm generated exporter outputs are written only to temporary or explicit
output directories, pass the learner-state sequence audit, and do not print
generated JSONL rows, labels, manifest bodies, or private paths.
Before adding exporter edge-case fixtures or tests, review
[learner-state sequence exporter edge fixture design](learner_state_sequence_exporter_edge_fixture_design.md)
and confirm planned cases remain synthetic-only, safe-failing, no-oracle, and
do not copy fixture rows or generated output bodies into docs.
After adding exporter edge-case fixtures, confirm
[`tests/fixtures/learner_state_sequence_exporter/`](../tests/fixtures/learner_state_sequence_exporter/README.md)
contains only synthetic fixture material, keeps intentional invalid cases
narrow, and does not introduce raw learner text, private paths, real participant
data, or public fixture body dumps.
After adding exporter edge-case tests, confirm invalid fixtures fail closed with
safe reason codes, valid edge fixtures pass audit, failure summaries do not
print raw row bodies or malformed-line contents, and generated outputs remain in
temporary or explicit caller-provided directories.
Before implementing an exporter CLI, review
[learner-state sequence exporter CLI design](learner_state_sequence_exporter_cli_design.md)
and confirm the future command requires safe output handling, explicit output
directory policy, audit-after-export, safe exit codes, and no generated body
logging.
After implementing the exporter CLI, confirm
`python -m learner_state.sequence_exporter` supports only synthetic fixture
input mode for now, writes to explicit safe output directories, reports only
safe human or JSON summaries, fails closed for invalid fixtures and unsafe
output paths, and does not print generated JSONL rows, label bodies, manifest
bodies, malformed-line contents, private paths, or raw logs.
Before adding an exporter CLI Makefile target, review
[learner-state sequence exporter Makefile target design](learner_state_sequence_exporter_makefile_target_design.md)
and confirm the target remains standalone initially, writes only under a
dedicated `tmp/` smoke output root, avoids fixture roots and private/real-data
paths, does not cat generated files, and is not added directly to
release-quality or CI before log safety review.
After adding `make check-learner-state-exporter-cli`, confirm it writes only
under
`tmp/learner_state_sequence_exporter_smoke/`, prints only exporter CLI safe
summaries, does not cat generated feature/label/manifest files, and is not
called directly by CI workflows.
Before integrating the exporter CLI target into release-quality, review
[learner-state sequence exporter release-quality integration design](learner_state_sequence_exporter_release_quality_integration_design.md)
and confirm the wrapper will call `make check-learner-state-exporter-cli`
rather than duplicating CLI arguments, will keep `tmp/` cleanup narrow, will not
cat generated files, and will not change CI workflows directly in the first
integration step.
After integrating the exporter CLI target into the release-quality wrapper,
confirm the wrapper calls `make check-learner-state-exporter-cli` after the
learner-state audit fixture check, keeps cleanup scoped to the Makefile
target's narrow `tmp/learner_state_sequence_exporter_smoke/` root, does not cat
generated files, and leaves CI workflows unchanged.
Before recording a remote/manual Release Quality run after exporter CLI smoke
wrapper integration, review
[learner-state exporter release-quality remote run record workflow](learner_state_exporter_release_quality_remote_run_record_workflow.md)
and confirm the public record will include only metadata, will not paste raw
GitHub Actions logs, will not include generated feature/label/manifest bodies,
will note artifact presence, and will avoid performance or real-data readiness
claims.
After recording the exporter CLI smoke remote/manual Release Quality run,
confirm the status marker
[learner-state exporter release-quality remote run status](status/learner_state_exporter_release_quality_remote_run_status.md)
records only high-level metadata, confirms learner-state audit fixture and
exporter CLI smoke inclusion, keeps generated output bodies out of docs, and
does not make model-performance or real-data readiness claims.
For the Milestone 07 recap, review
[learner-state sequence exporter infrastructure recap](milestone_07_learner_state_sequence_exporter_infrastructure_recap.md)
and confirm it summarizes exporter infrastructure with public-safe metadata
only, does not paste raw workflow logs or generated output bodies, and does not
claim model performance, estimator correctness, production readiness, or
real-data readiness.
Before implementing any learner-state estimator input loader, training loop,
selective prediction, or calibration work, review
[learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
and confirm it keeps features and labels separated, treats expected action as
evaluation/training target only, forbids future leakage and raw text, avoids
generated output bodies in docs, and does not claim performance or real-data
readiness.
Before creating estimator input fixture files, review
[learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
and confirm the fixture plan is synthetic-only, uses exported-shape
feature/label/manifest files, keeps expected validation results count-only,
avoids row body examples, and tests join, sequence, split, and leakage
boundaries without making performance or real-data readiness claims.
After creating estimator input fixture files, review the
[learner-state estimator input fixture root](../tests/fixtures/learner_state_estimator_input/README.md)
and confirm all cases are synthetic-only, JSON/JSONL parseable, expected
validation result files are count/reason-code only, invalid forbidden-field
cases are intentional, and no generated body or real participant data is added
to docs.
Before implementing an estimator input validator or loader, review
[learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
and confirm validation order, safe result schema, reason-code mapping,
fixture expected-result matching, split checks, and no-oracle checks are
documented without adding model training, metrics, calibration, or real-data
readiness claims.
After implementing the minimal estimator input validator/loader, review
`python/learner_state/estimator_input.py` and
`python/learner_state/tests/test_estimator_input.py`; confirm they return only
safe count/reason-code metadata, exercise all Step193 fixture contracts, do not
print JSONL row bodies or manifest bodies, and do not add estimator training,
metrics, calibration, or real-data readiness claims.
Before implementing an estimator input validator CLI, review
[learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md)
and confirm the CLI plan uses fixture-root expected-result matching, safe human
and JSON summaries, stable exit codes, path safety, no raw row or manifest
body output, and no Makefile/release-quality connection in the design step.
After implementing the minimal estimator input validator CLI, run
`PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input`
and the CLI unittest. Confirm stdout/stderr contain only safe statuses, counts,
reason codes, and matched-case summaries; do not add generated row bodies,
Makefile targets, release-quality integration, model training, metrics,
calibration, or real-data readiness claims.
Before adding an estimator input validator Makefile target, review
[learner-state estimator input validator Makefile target design](learner_state_estimator_input_validator_makefile_target_design.md)
and confirm the target will call fixture-root validation with safe human
summary output, will not create tmp outputs, will not cat feature/label or
manifest bodies, and will remain standalone until a separate release-quality
integration review.
After adding the estimator input validator Makefile target, run
`make check-learner-state-estimator-input` and confirm it reports 9 matched
synthetic fixture cases, prints only safe count/reason-code summaries, creates
no tmp output, and remains outside the release-quality wrapper and GitHub
Actions workflows.
Before integrating the estimator input validator target into release-quality,
review
[learner-state estimator input release-quality integration design](learner_state_estimator_input_release_quality_integration_design.md)
and confirm the wrapper will call `make check-learner-state-estimator-input`
after the learner-state audit and exporter CLI checks, will not add tmp cleanup
or artifacts, will not cat fixture files, and will leave GitHub Actions
workflows unchanged in the first integration step.
After integrating the estimator input validator target into release-quality,
run `make check-release-quality` and confirm the wrapper calls
`make check-learner-state-estimator-input` after the learner-state audit and
exporter CLI checks, reports 9 matched synthetic estimator input fixture cases,
prints only safe count/reason-code summaries, creates no estimator-input tmp
output, and leaves GitHub Actions workflows unchanged.
Before recording any remote/manual Release Quality result after estimator input
validation wrapper integration, review
[learner-state estimator input release-quality remote run record workflow](learner_state_estimator_input_release_quality_remote_run_record_workflow.md)
and record only public-safe metadata: workflow/job name, branch, commit short
hash, status, duration if available, artifact presence, inclusion of audit,
exporter, and estimator input validation checks, count-only matched-case
summary if visible, and log safety review status. Do not paste raw GitHub
Actions logs, JSONL rows, fixture row contents, generated output bodies, label
or manifest bodies, expected action bodies, private paths, or performance
metrics.
After recording the estimator input validation remote/manual Release Quality
run, review
[learner-state estimator input release-quality remote run status](status/learner_state_estimator_input_release_quality_remote_run_status.md)
and confirm it includes only high-level metadata, count-only audit/exporter/
estimator input summaries, log safety review status, scope limitations, and
non-goals. It must not include raw logs, JSONL row bodies, feature or label
rows, generated manifest bodies, expected action bodies, private paths, or
performance metrics.
After completing the estimator input validation infrastructure milestone,
review
[Milestone 08 learner-state estimator input validation infrastructure recap](milestone_08_learner_state_estimator_input_validation_infrastructure_recap.md)
and confirm it summarizes only public-safe components, safe/count-only remote
status, synthetic-only boundaries, no-oracle constraints, non-goals, and next
research/development candidates. It must not claim estimator correctness,
model performance, calibration quality, real-data readiness, or production
data-collection readiness.
Before implementing any selective prediction, calibration, confidence
thresholding, ECE, AURCC, F1, or learner-state estimator prototype, review
[selective prediction and calibration design](selective_prediction_calibration_design.md)
and confirm validation labels, test labels, confidence, temperature scaling,
threshold selection, ECE, AURCC, risk-coverage reporting, split policy, and
no-oracle boundaries are documented. The design step must not add metric
computation, estimator training, model code, real-data handling, generated row
bodies, raw learner text, raw GitHub Actions logs, or performance claims.
Before creating any calibration or selective prediction fixture files, review
[selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
and confirm the fixture root, case structure, prediction row policy, label row
policy, split metadata, calibration policy config, expected validation result
fields, failure reason codes, and no-test-tuning boundaries are documented.
The fixture design step must not create fixture files, implement calibration,
compute ECE/AURCC/F1/accuracy, paste logits or probability row dumps, paste
JSONL row bodies, expose expected action bodies, use real data, or claim
performance.
After creating calibration / selective prediction fixture files, review the
[selective prediction fixture root](../tests/fixtures/learner_state_selective_prediction/README.md)
and confirm it is synthetic-only, separates prediction rows from label rows,
keeps expected actions label-side except intentional invalid leakage cases,
uses count-only split metadata and expected validation results, includes no
real participant data or private paths, and does not claim model performance.
Before implementing any calibration / selective prediction fixture validator,
review
[selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
and confirm validation order, safe result schema, failure reason codes,
expected-result matching, prediction/label joins, split validation,
calibration policy checks, test tuning leakage checks, no-oracle checks, and
safe output policy are documented. The validation design step must not
implement validator code, calibration, selective prediction, model training,
metric computation, real-data handling, or performance claims.
After implementing the minimal calibration / selective prediction fixture
validator, confirm `python/learner_state/selective_prediction_validation.py`
and `python/learner_state/tests/test_selective_prediction_validation.py`
exercise the synthetic fixture root with safe count/reason-code metadata only,
match all expected validation results, avoid row/policy/split body output, and
do not implement calibration, selective prediction, model training, metric
computation, real-data handling, or performance claims.
Before implementing a calibration / selective prediction validator CLI,
review
[selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
and confirm CLI modes, exit codes, fixture-root expected-result matching, safe
human output, safe JSON output, path safety, and future Makefile/release-quality
staging are documented. The CLI design step must not implement the CLI, add a
Makefile target, change release-quality, compute metrics, expose row/logit or
policy bodies, use real data, or claim performance.
After implementing the minimal calibration / selective prediction validator
CLI, confirm `python -m learner_state.selective_prediction_validation` supports
fixture-case, fixture-root, and safe JSON modes; reports 8 matched fixture
cases for the synthetic fixture root; exits `0` for intentional invalid
fixtures when expected results match; exits safely for usage/input/mismatch
cases; avoids row, label, policy, split, logits, and probability body output;
and does not add a Makefile target or release-quality integration yet.
Before adding a selective prediction calibration validator Makefile target,
review
[selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
and confirm the target name, fixture-root command, safe human output,
exit-code behavior, no-tmp-output policy, relation to existing learner-state
targets, and release-quality staging are documented. The design step must not
change Makefile, release-quality, workflows, fixtures, validator code, tests,
or compute calibration metrics.
After adding the selective prediction calibration validator Makefile target,
run `make check-learner-state-selective-prediction` and confirm the target
reports 8 matched fixture cases, prints safe human summary only, creates no
tmp output, avoids row/logit/probability/policy/split body output, and remains
outside the release-quality wrapper and GitHub workflows until a separate
integration step.
Before integrating the selective prediction calibration validator target into
release-quality, review
[selective prediction calibration release-quality integration design](selective_prediction_calibration_release_quality_integration_design.md)
and confirm wrapper placement, command choice, section label, failure
interpretation, output/logging safety, runtime impact, and remote/manual run
record policy are documented. The design step must not change the wrapper,
workflow, Makefile, scripts, code, tests, fixtures, or compute calibration
metrics.
After integrating the selective prediction calibration validator target into
release-quality, run `make check-release-quality` and confirm the wrapper
includes `release_quality_check: learner-state selective prediction
calibration validation`, calls
`make check-learner-state-selective-prediction`, reports 8 matched synthetic
fixture cases, emits safe summary only, creates no tmp output for this target,
and avoids row/logit/probability/policy/split body output or performance
metrics.
Before recording a remote/manual Release Quality run that includes selective
prediction calibration validation, review
[selective prediction release-quality remote run record workflow](selective_prediction_release_quality_remote_run_record_workflow.md)
and confirm the record will include only high-level metadata, count-only
fixture summaries, included-check flags, and log-safety review results. The
record workflow design step must not create a status marker, change workflows,
paste raw GitHub Actions logs, include row/policy/split/logits bodies, or make
performance or real-data readiness claims.
After recording the selective prediction calibration validation remote/manual
Release Quality result, confirm the public-safe status marker
[learner-state selective prediction release-quality remote run status](status/learner_state_selective_prediction_release_quality_remote_run_status.md)
contains only metadata and count-only summaries, records 8 matched selective
prediction fixture cases, excludes raw logs and full job output, excludes
prediction/label/policy/split/logits bodies, and does not claim model
performance, calibration quality, or real-data readiness.
For the Milestone 09 recap, review
[milestone 09 selective prediction validation infrastructure recap](milestone_09_selective_prediction_validation_infrastructure_recap.md)
and confirm it summarizes the selective prediction/calibration validation
infrastructure, remote run status, safety boundaries, non-goals, and next
research/development candidates without raw logs, row bodies, policy/split
bodies, logits dumps, performance claims, or real-data readiness claims.
Before implementing any selective prediction / calibration scaffold, review
[selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
and confirm the future scaffold will consume only validator-passed synthetic
fixtures, use validation-only temperature/threshold selection, freeze policy
metadata before test evaluation, emit safe summaries only, and avoid raw rows,
label bodies, logits dumps, policy/split bodies, metric claims, real data, or
production readiness claims.
Before creating any frozen selective prediction policy artifact or validator,
review
[frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
and confirm the future artifact schema records validation-only temperature and
threshold provenance, requires explicit schema versioning, excludes raw rows,
label bodies, logits/probability dumps, policy/split body dumps, test-derived
tuning traces, private paths, performance claims, real data, and production
readiness claims.
Before creating frozen selective prediction policy fixture files, review
[frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
and confirm the planned fixture root, valid and invalid cases, expected
validation result contract, failure reason codes, and future validation checks
remain synthetic-only and exclude frozen artifact bodies, raw rows, logits
dumps, label bodies, policy/split bodies, private paths, performance claims,
real data, and production readiness claims.
For Step222, confirm the initial synthetic frozen policy fixture root
`tests/fixtures/learner_state_frozen_selective_prediction_policy/` contains
only fixture artifacts and safe expected validation result metadata, with no
validator implementation, no calibration scaffold, no raw rows, no logits
dumps except the intentional invalid fixture, no private path except the
intentional invalid fixture, and no performance claim except the intentional
invalid fixture.
Before implementing a frozen selective prediction policy validator, review
[frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
and confirm the future validator will fail closed on unsafe paths, malformed
JSON, unknown schema versions, missing required fields, recursive forbidden
fields, test-derived temperature or threshold, unsafe safety booleans,
invalid split policy, invalid count summaries, and performance claims while
emitting only safe metadata.
For Step224, confirm
`python/learner_state/frozen_policy_validation.py` and
`python/learner_state/tests/test_frozen_policy_validation.py` validate only
synthetic frozen policy fixtures, return safe metadata, suppress policy
bodies, do not implement a CLI or Makefile target, do not compute calibration
or metrics, and do not claim model performance or real-data readiness.
Before implementing a frozen policy validator CLI, review
[frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
and confirm fixture-case/root modes, expected-result matching, exit codes,
human output, JSON output, and path-safety behavior remain safe and do not
print policy bodies, logits dumps, private path values, raw rows, metric
bodies, raw learner text, or performance claims.
For Step226, confirm
`python/learner_state/frozen_policy_validation.py` exposes only a safe
fixture-focused CLI, `python/learner_state/tests/test_frozen_policy_validation_cli.py`
exercises usage errors, expected-result matching, and safe JSON output, and
no Makefile target, release-quality wrapper, workflow, calibration scaffold,
metric computation, or frozen policy generation is added.
Before implementing a frozen policy validator Makefile target, review
[frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
and confirm the future target will call only the safe fixture-root CLI, print
human count/reason-code summary only, avoid `tmp/` and `manual_outputs/`, and
not modify release-quality, workflows, calibration, selective prediction,
estimator code, or metric computation in the target implementation step.
For Step228, confirm `make check-learner-state-frozen-policy` exists, reports
12 matched synthetic frozen policy fixture cases, emits safe human summary
only, creates no `tmp/` output, and leaves release-quality wrapper, workflows,
scripts, fixtures, validator code, calibration, selective prediction,
estimator code, and metric computation unchanged.
Before integrating the frozen policy validator target into release-quality,
review
[frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md)
and confirm the future wrapper placement, Makefile target command, log safety
policy, failure interpretation, remote/manual run record policy, and
synthetic-only/no-oracle boundary are documented.
For Step230, confirm `make check-release-quality` includes
`release_quality_check: learner-state frozen policy validation`, reports
12 matched synthetic frozen policy fixture cases through the target, emits
safe human summary only, and leaves workflows, Makefile, Python code, tests,
fixtures, calibration, selective prediction, frozen policy generation,
estimator code, and metric computation unchanged.
For Step231, review
[frozen policy release-quality remote run record workflow](frozen_policy_release_quality_remote_run_record_workflow.md)
before creating any remote/manual Release Quality status marker. Confirm the
future marker will record only public-safe metadata and count-only summaries,
will not paste raw GitHub Actions logs or full job output, will not include
frozen policy artifact bodies, JSON bodies, raw rows, logits/probability dumps,
private paths, raw learner text, or performance metric bodies, and will not
change workflows, wrapper scripts, Makefile, Python code, tests, or fixtures.
For Step232, confirm the public-safe status marker
[learner-state frozen policy release-quality remote run status](status/learner_state_frozen_policy_release_quality_remote_run_status.md)
records only metadata and count-only summaries for the successful remote
Release Quality run, confirms frozen policy validation was included with
12 matched fixture cases, and does not include raw logs, full job output,
copied log blocks, frozen policy artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
metric bodies.
For the Milestone 10 recap, review
[milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
and confirm it summarizes Step220 through Step232 without adding workflow,
wrapper, Makefile, Python, test, or fixture changes. The recap must keep the
public-safe boundary: no raw logs, full job output, frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, private paths, raw
learner text, generated feature/label/manifest bodies, or performance claims.
For Step234, review the
[frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
and confirm it remains docs-only: no generator, calibration code, selective
prediction code, estimator code, metric computation, workflow change, wrapper
change, Makefile change, Python change, test change, or fixture change is
introduced. The design must not paste frozen policy artifact bodies, JSON
bodies, raw rows, logits/probability dumps, label/split/calibration policy
bodies, private paths, raw learner text, GitHub raw logs, or performance
claims.
For Step235, review the
[frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
and confirm it remains docs-only: no fixture root, fixture files, generator,
calibration code, selective prediction code, estimator code, metric
computation, workflow change, wrapper change, Makefile change, Python change,
test change, or existing fixture change is introduced. The design must use
safe fixture pointers and expected-result metadata only, without pasting
prediction rows, label rows, generated frozen policy bodies, JSON bodies,
logits/probability dumps, private paths, raw learner text, GitHub raw logs, or
performance claims.
For Step236, review the
[frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
and confirm the new files are synthetic-only metadata fixtures for future
generator work. They must not include raw prediction/label bodies, generated
frozen policy artifact bodies, logits/probability dumps, private paths except
the intentional invalid output-path fixture, raw learner text, GitHub raw logs,
or performance evidence. This step must not add generator code, validator code,
CLI, Makefile targets, release-quality integration, workflow changes, Python
tests, or changes to existing fixtures.
For Step237, review the
[frozen policy generation validation design](frozen_policy_generation_validation_design.md)
and confirm it remains docs-only: no generation validator, generator code,
CLI, Makefile target, release-quality wrapper change, workflow change, Python
code, tests, or fixture changes are introduced. The design must describe safe
metadata-only validation order, result schema, reason-code mapping,
expected-result matching, input pointer checks, and forbidden-field scans
without pasting request bodies, generated artifact bodies, JSON bodies, raw
rows, logits/probability dumps, private paths, raw learner text, GitHub raw
logs, or performance claims.
For Step238, confirm
`python/learner_state/frozen_policy_generation_validation.py` and
`python/learner_state/tests/test_frozen_policy_generation_validation.py`
validate only synthetic frozen policy generation fixtures, return safe
metadata, suppress request/input/generated-artifact bodies, do not implement a
CLI or Makefile target, do not modify release-quality or workflows, do not
change fixture files, do not implement generator/calibration/selective
prediction logic, do not compute metrics, and do not claim model performance
or real-data readiness.
For Step239, review the
[frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
and confirm it remains docs-only: no CLI, generator, scaffold, Makefile target,
release-quality wrapper change, workflow change, Python code, tests, or
fixture changes are introduced. The design must specify fixture-case/root
modes, exit codes, safe human output, safe JSON output, path safety, and
expected-result matching without printing request bodies, input pointer
bodies, generated artifact bodies, raw rows, logits/probability dumps,
private paths, raw learner text, raw GitHub logs, or performance claims.
For Step240, confirm the minimal CLI implementation in
`python/learner_state/frozen_policy_generation_validation.py` and
`python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`
validates only synthetic frozen policy generation fixtures, returns safe
metadata, supports fixture-case/root modes and JSON output, treats intentional
invalid fixtures as success when expected results match, and does not print
request bodies, input pointer bodies, generated artifact bodies, raw rows,
logits/probability dumps, private paths, raw learner text, raw GitHub logs, or
performance claims. This step must not add a Makefile target, release-quality
wrapper change, workflow change, generator code, calibration/selective
prediction logic, metric computation, fixture changes, or real-data readiness
claims.
For Step241, review the
[frozen policy generation validator Makefile target design](frozen_policy_generation_validator_makefile_target_design.md)
and confirm it remains docs-only: no Makefile target, Makefile change,
release-quality wrapper change, workflow change, Python code change, test
change, fixture change, generator code, calibration/selective prediction
logic, metric computation, or real-data readiness claim is introduced. The
design must specify target name, command, help text, exit-code behavior, safe
logging, tmp/output policy, and future release-quality staging without
printing request bodies, input pointer bodies, generated artifact bodies, raw
rows, logits/probability dumps, private paths, raw learner text, raw GitHub
logs, or performance claims.
For Step242, confirm `make check-learner-state-frozen-policy-generation`
exists, appears in `make help`, reports thirteen matched synthetic generation
fixture cases, creates no `tmp/` output, prints only safe human summary
metadata, and leaves the release-quality wrapper, workflows, Python code,
tests, and fixtures unchanged. The target must not print request bodies, input
pointer bodies, generated artifact bodies, raw rows, logits/probability dumps,
private paths, raw learner text, raw GitHub logs, or performance claims, and
it remains outside release-quality until a separate integration review.
For Step243, review the
[frozen policy generation release-quality integration design](frozen_policy_generation_release_quality_integration_design.md)
and confirm it remains docs-only: no release-quality wrapper change, workflow
change, Makefile change, Python code change, test change, fixture change,
generator code, calibration/selective prediction logic, metric computation, or
real-data readiness claim is introduced. The design must specify wrapper
placement after frozen policy validation and before config/scoring smoke
checks, wrapper command, label, log-safety policy, failure interpretation,
remote/manual run recording policy, and future implementation tests without
printing request bodies, input pointer bodies, generated artifact bodies, raw
rows, logits/probability dumps, private paths, raw learner text, raw GitHub
logs, or performance claims.
For Step244, confirm `make check-release-quality` includes
`release_quality_check: learner-state frozen policy generation validation`,
calls `make check-learner-state-frozen-policy-generation` after frozen policy
validation and before config/scoring smoke checks, reports thirteen matched
synthetic generation fixture cases, and keeps workflow YAML, Makefile, Python
code, tests, and fixtures unchanged. The wrapper output must remain safe:
request bodies, input pointer bodies, generated artifact bodies, raw rows,
logits/probability dumps, private paths, raw learner text, raw GitHub logs,
and performance claims must not be copied into docs or logs.
For Step245, review the
[frozen policy generation release-quality remote run record workflow](frozen_policy_generation_release_quality_remote_run_record_workflow.md)
and confirm it remains docs-only: no remote status marker, workflow change,
wrapper change, Makefile change, Python code change, test change, fixture
change, generator code, calibration/selective prediction logic, metric
computation, or real-data readiness claim is introduced. The design must
specify the future status marker path, safe metadata fields, forbidden
metadata, count-only frozen policy generation validation summary, related
learner-state checks summary, safety review, failure handling, and future
recording workflow without copying raw logs, full job output, generation
request bodies, input pointer bodies, generated artifact bodies, frozen policy
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private
paths, raw learner text, or performance claims.
For Step246, review the
[learner-state frozen policy generation release-quality remote run status](status/learner_state_frozen_policy_generation_release_quality_remote_run_status.md)
and confirm it is a public-safe metadata-only status marker: no raw GitHub
Actions logs, full job output, copied log blocks, generation request bodies,
input pointer bodies, generated artifact bodies, frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, private paths, raw
learner text, real participant data, or performance claims are included. The
marker should record only run identity, wrapper inclusion, count-only frozen
policy generation validation summary, related learner-state check summaries,
safety review, interpretation, non-proofs, and next actions. This step must
not change workflow YAML, wrapper scripts, Makefile, Python code, tests,
fixtures, generator code, calibration/selective prediction logic, metric
computation, or real-data readiness claims.
For Step247, review the
[Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
and confirm it is recap-only: no workflow change, wrapper change, Makefile
change, Python code change, test change, fixture change, generator code,
frozen policy generation scaffold implementation, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. The recap must summarize scope,
implemented artifacts, current validation surface, commands, release-quality
status, no-oracle/synthetic-only guarantees, validated and non-validated
areas, prior milestone relation, remaining risks, and next steps without
copying raw logs, request bodies, input pointer bodies, generated artifact
bodies, frozen policy artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step248, review the
[frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
and confirm it is docs-only: no scaffold code, generator code, CLI,
Makefile change, wrapper change, workflow change, Python code change, test
change, fixture change, calibration/selective prediction logic, estimator
work, metric computation, real-data use, or real-data readiness claim is
introduced. The design must describe the future scaffold role, proposed module
and APIs, dataclasses, input/output contracts, failure categories,
no-oracle/synthetic-only boundaries, relation to validators, CLI future,
fixture future, testing plan, release-quality staging, and next steps without
copying raw logs, request bodies, input pointer bodies, generated artifact
bodies, frozen policy artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step249, review the
[frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
and confirm it is docs-only: no fixture files, existing fixture changes,
scaffold code, generator code, CLI, Makefile change, wrapper change, workflow
change, Python code change, test change, calibration/selective prediction
logic, estimator work, metric computation, real-data use, or real-data
readiness claim is introduced. The design must describe the future scaffold
fixture root, directory structure, required case files, valid and invalid
cases, expected scaffold result contract, request and pointer fixture
contracts, safe output policy, reason-code mapping, relation to existing
generation validation fixtures, future implementation path, testing plan, and
release-quality staging without copying raw logs, request bodies, input
pointer bodies, generated artifact bodies, frozen policy artifact bodies, JSON
bodies, raw rows, logits/probability dumps, private paths, raw learner text,
or performance claims.
For Step250, review the initial
[frozen policy generation scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md)
and confirm the change is fixture-only: no scaffold code, scaffold fixture
validator, generator code, CLI, Makefile change, wrapper change, workflow
change, Python code change, Python test change, existing fixture change,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. The fixture root
must contain only synthetic metadata files for the initial valid and invalid
cases, with `generation_request.json`, `input_fixture_pointer.json`, and
`expected_scaffold_result.json` per case. It must not include raw logs, request
body dumps, input pointer body dumps, generated artifact bodies, frozen policy
artifact bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, private paths, raw learner text, real
participant data, or performance evidence.
For Step251, review the
[frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
and confirm it is docs-only: no validator code, scaffold code, generator code,
CLI, Makefile change, wrapper change, workflow change, Python code change,
Python test change, fixture change, existing fixture change,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. The design must
cover root-level checks, case-level checks, forbidden field/value scans,
expected reason-code mapping, expected pass/fail behavior, safe human/JSON
summary policy, relation to scaffold implementation, relation to the existing
generation validator, CLI future, Makefile/release-quality future, and testing
plan without copying raw logs, request bodies, input pointer bodies, generated
artifact bodies, frozen policy artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step252, review
`python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
and
`python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`
and confirm the change is limited to the minimal scaffold fixture validator and
unit tests: no scaffold runtime code, generator code, scaffold CLI, Makefile
target, wrapper change, workflow change, fixture change, existing fixture
change, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced. The
validator output must remain safe metadata only and must not include raw logs,
request bodies, input pointer bodies, generated artifact bodies, frozen policy
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private
paths, raw learner text, or performance claims.
For Step253, review the
[frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
and confirm it is docs-only: no CLI code, scaffold runtime code, generator
code, Makefile target, wrapper change, workflow change, Python code change,
Python test change, fixture change, existing fixture change,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. The design must
cover entrypoint choice, fixture-root and single-case modes, argument rules,
exit codes, safe human output, safe JSON output, path safety, mismatch
reporting, relation to the existing Python API, relation to scaffold runtime,
relation to the existing generation validator CLI, future tests,
Makefile/release-quality staging, and non-goals without copying raw logs,
request bodies, input pointer bodies, generated artifact bodies, frozen policy
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private
paths, raw learner text, or performance claims.
For Step254, review
`python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
and
`python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`
and confirm the change is limited to the minimal scaffold fixture validator
CLI and CLI tests: no scaffold runtime code, generator code, Makefile target,
wrapper change, workflow change, fixture change, existing fixture change,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. The CLI output
must remain safe metadata only and must not include raw logs, request bodies,
input pointer bodies, generated artifact bodies, frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, private paths, raw
learner text, or performance claims.
For Step255, review the
[frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
and confirm it is docs-only: no Makefile target, Makefile change,
release-quality wrapper change, GitHub Actions workflow change, Python code
change, Python test change, fixture change, scaffold runtime code, generator
code, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced. The
design must cover target name, command, help text, expected behavior, exit
codes, logging safety, tmp/output policy, relation to existing targets,
release-quality staging, future tests, no-oracle boundaries, and non-goals
without copying raw logs, request bodies, input pointer bodies, generated
artifact bodies, frozen policy artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step256, review `Makefile` and the
[frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
and confirm the change is limited to the standalone Makefile target and docs:
no release-quality wrapper change, GitHub Actions workflow change, Python code
change, Python test change, fixture change, scaffold runtime code, generator
code, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced. The
target must call the scaffold fixture validator CLI in fixture-root mode, print
safe human summary only, avoid tmp/manual output creation, and remain outside
release-quality until a later integration step.
For Step257, review the
[frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
and confirm it is docs-only: no release-quality wrapper change, GitHub Actions
workflow change, Makefile change, Python code change, Python test change,
fixture change, scaffold runtime code, generator code, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. The design must cover wrapper
insertion point, command, label, expected wrapper behavior, log safety, failure
interpretation, relation to existing release-quality checks, future tests,
future status-marker policy, and non-goals without copying raw logs, request
bodies, input pointer bodies, artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step258, review `scripts/check_release_quality.sh` and the
[frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
and confirm the wrapper change is limited to adding the scaffold fixture
validator label and `make check-learner-state-frozen-policy-generation-scaffold-fixtures`
after frozen policy generation validation and before config/scoring smoke
checks. Confirm there is no GitHub Actions workflow change, Makefile change,
Python code change, Python test change, fixture change, scaffold runtime code,
generator code, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim. The wrapper output
must remain safe summary only and must not copy raw logs, request bodies, input
pointer bodies, artifact bodies, JSON bodies, raw rows, logits/probability
dumps, private paths, raw learner text, or performance claims.
For Step259, review the
[frozen policy generation scaffold fixture validator release-quality remote run record workflow](frozen_policy_generation_scaffold_fixture_validator_release_quality_remote_run_record_workflow.md)
and confirm it is docs-only: no remote run status marker, GitHub Actions
workflow change, release-quality wrapper change, Makefile change, Python code
change, Python test change, fixture change, scaffold runtime code, generator
code, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced. The
design must define the future status marker path, public-safe metadata,
forbidden metadata, marker structure, scaffold fixture validation summary,
related checks summary, safety review, interpretation, failure handling,
future recording workflow, public release checklist relation, and non-goals
without copying raw logs, request bodies, input pointer bodies, expected
scaffold result bodies, artifact bodies, JSON bodies, raw rows,
logits/probability dumps, private paths, raw learner text, or performance
claims.
For Step260, review the
[learner-state frozen policy generation scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_scaffold_fixture_release_quality_remote_run_status.md)
and confirm it records only public-safe metadata and count-only summaries:
workflow/job identity, branch/commit, success status, wrapper inclusion,
scaffold fixture validator target inclusion, `total_cases=11`,
`matched_cases=11`, `mismatched_cases=0`, `input_error_cases=0`,
`content_suppressed=true`, `no_raw_rows=true`, related learner-state check
counts, safety review, interpretation, non-goals, and next actions. Confirm
there is no GitHub Actions workflow change, release-quality wrapper change,
Makefile change, Python code change, Python test change, fixture change,
scaffold runtime code, generator code, calibration/selective prediction
logic, estimator work, metric computation, real-data use, or real-data
readiness claim. Confirm the marker does not copy raw logs, full job output,
request bodies, input pointer bodies, expected scaffold result bodies,
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private
paths, raw learner text, or performance claims.
For Step261, review the
[Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, scaffold runtime code, generator code,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. Confirm the recap
summarizes scaffold fixture validation infrastructure only: fixture root
`tests/fixtures/learner_state_frozen_policy_generation_scaffold`, valid 3,
invalid 8, total 11, JSON files 33, expected outcome matching, reason-code
matching, forbidden field/value scans, private path scans, performance claim
scans, no raw rows, no logits dump, safe summaries, Makefile target,
release-quality inclusion, remote status, remaining risks, and next steps
before scaffold runtime API design. Confirm it does not copy raw logs, full job
output, generation request bodies, input pointer bodies, expected scaffold
result bodies, artifact bodies, JSON bodies, raw rows, logits/probability
dumps, private paths, raw learner text, or performance claims.
For Step262, review the
[frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, scaffold runtime code, generator code,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. Confirm the design
defines only the future runtime API boundary: proposed module, public APIs,
dataclasses, request contract, input pointer contract, plan contract, scaffold
result contract, error categories, validator relation, release-quality
relation, path safety, no-oracle boundary, synthetic-only boundary,
logging/output policy, future tests, and staged implementation plan. Confirm
the design does not copy raw logs, full job output, generation request bodies,
input pointer bodies, expected scaffold result bodies, generated or frozen
policy artifact bodies, JSON bodies, raw rows, logits/probability dumps,
private paths, raw learner text, or performance claims.
For Step263, review the
[frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, scaffold runtime code, generator code,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim is introduced. Confirm the design
uses path-only / field-name-only contract summaries, aligns future
`FrozenPolicyGenerationScaffoldResult` fields with existing
`expected_scaffold_result.json` fields, maps current invalid reason codes
without aliases, defines valid/invalid/input-error boundaries, lists safety
flag alignment, mismatch risks, implementation constraints, testing
implications, and release-quality implications. Confirm it does not copy raw
logs, full job output, generation request bodies, input pointer bodies,
expected scaffold result bodies, generated or frozen policy artifact bodies,
JSON bodies, raw rows, logits/probability dumps, private paths, raw learner
text, or performance claims.
For Step264, review `python/learner_state/frozen_policy_generation.py`,
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime.py`,
and the linked runtime API/alignment docs. Confirm the change is limited to a
minimal metadata-only scaffold runtime API skeleton plus focused tests and
docs updates: no GitHub Actions workflow change, release-quality wrapper
change, Makefile target, fixture change, runtime CLI, generator code,
artifact-body generation, artifact file writing, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. Confirm the runtime summary contains
safe metadata only, deterministic reason codes, explicit safety booleans,
`generated_artifact_written=false`, `generated_artifact_body_available=false`,
and `artifact_body_suppressed=true`, without copying request bodies, pointer
bodies, expected scaffold result bodies, generated or frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, private paths, raw
learner text, or performance claims.
For Step265, review the
[frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, runtime CLI, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm the design explains how future tests should
compare runtime skeleton summaries with existing
`expected_scaffold_result.json` metadata through the scaffold fixture validator
contract, covers valid 3 and invalid 8 cases, malformed/missing input
boundaries, no-body-leakage scans, deterministic behavior, explicit safety
flags, and release-quality staging. Confirm it does not copy request bodies,
pointer bodies, expected scaffold result bodies, generated or frozen policy
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private
paths, raw learner text, or performance claims.
For Step266, review
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`
and the linked compatibility-test design doc. Confirm the change is limited to
minimal runtime fixture compatibility tests plus docs updates: no GitHub
Actions workflow change, release-quality wrapper change, Makefile change,
fixture change, runtime CLI, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the tests compare runtime safe summaries with the existing scaffold
fixture expected-result contract through the scaffold fixture validator helper,
cover valid 3 and invalid 8 cases, malformed/missing input boundaries,
no-body-leakage checks, deterministic behavior, and explicit safety booleans.
Confirm test assertions use safe case labels and do not print request bodies,
pointer bodies, expected scaffold result bodies, generated or frozen policy
artifact bodies, JSON bodies, raw rows, logits/probability dumps, private paths,
raw learner text, or performance claims.
For Step267, review the
[frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, runtime CLI implementation, generator code,
artifact-body generation, artifact file writing, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. Confirm the design recommends a thin
`python -m learner_state.frozen_policy_generation` wrapper over the runtime
API, defines `--request`, `--pointer`, `--json`, and `--help`, separates safe
runtime fail results from usage/input errors, and requires safe metadata-only
human/JSON output. Confirm it does not copy request bodies, pointer bodies,
expected scaffold result bodies, generated or frozen policy artifact bodies,
JSON bodies, raw rows, logits/probability dumps, private paths, raw learner
text, or performance claims.
For Step268, review `python/learner_state/frozen_policy_generation.py`,
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`,
and the linked runtime CLI design doc. Confirm the change is limited to a
minimal runtime CLI implementation plus focused tests and docs updates: no
GitHub Actions workflow change, release-quality wrapper change, Makefile target
change, fixture change, generator code, artifact-body generation, artifact
file writing, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced.
Confirm the CLI remains a thin wrapper around
`run_frozen_policy_generation_scaffold` and
`summarize_frozen_policy_generation_scaffold_result`, supports `--request`,
`--pointer`, `--json`, and `--help`, returns exit `0` for safe runtime pass or
fail results, returns exit `2` for usage/input/path-before-load errors, and
emits safe metadata-only human/JSON summaries. Confirm it does not print
request bodies, pointer bodies, expected scaffold result bodies, generated or
frozen policy artifact bodies, JSON bodies, raw rows, logits/probability dumps,
private paths, raw learner text, or performance claims.
For Step269, review the
[frozen policy generation scaffold runtime Makefile target design](frozen_policy_generation_scaffold_runtime_makefile_target_design.md)
and confirm it is docs-only: no Makefile target, Makefile change,
release-quality wrapper change, GitHub Actions workflow change, Python code
change, Python test change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness claim
is introduced. Confirm the design recommends a standalone runtime CLI smoke
target, keeps fixture-root expected matching in the scaffold fixture validator
and runtime compatibility tests, requires safe metadata-only output, creates no
tmp/manual output, and does not treat target success as generator quality or
performance evidence.
For Step270, review `Makefile` and the linked runtime Makefile target design.
Confirm the change is limited to the standalone
`check-learner-state-frozen-policy-generation-scaffold-runtime` target,
Makefile help text, and docs updates: no release-quality wrapper change,
GitHub Actions workflow change, Python code change, Python test change,
fixture change, generator code, artifact-body generation, artifact file
writing, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced.
Confirm the target runs the runtime CLI over the synthetic
`valid/minimal_fixed_threshold_dry_run` request and pointer pair, emits safe
metadata-only output, creates no tmp/manual output, and does not treat target
success as generator quality or performance evidence.
For Step271, review the
[frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
and confirm it is docs-only: no release-quality wrapper change, GitHub Actions
workflow change, Makefile change, Python code change, Python test change,
fixture change, generator code, artifact-body generation, artifact file
writing, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced.
Confirm the design places the runtime smoke target after scaffold fixture
validation and before config/scoring smoke checks, recommends calling the
standalone Makefile target, defines the wrapper label, requires safe
metadata-only output, creates no tmp/manual output, and does not treat runtime
smoke success as generator quality or performance evidence.
For Step272, review `scripts/check_release_quality.sh` and the linked runtime
release-quality integration design. Confirm the change is limited to adding
`make check-learner-state-frozen-policy-generation-scaffold-runtime` after the
scaffold fixture validator target and before config/scoring smoke checks, plus
docs updates: no GitHub Actions workflow change, Makefile change, Python code
change, Python test change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm the wrapper output remains safe metadata only and
does not treat runtime smoke success as generator quality or performance
evidence.
For Step273, review the
[frozen policy generation scaffold runtime release-quality remote run record workflow](frozen_policy_generation_scaffold_runtime_release_quality_remote_run_record_workflow.md)
and confirm it is docs-only: no remote run status marker, GitHub Actions
workflow change, release-quality wrapper change, Makefile change, Python code
change, Python test change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm the design defines the future status marker path,
safe metadata fields, forbidden content, pass-only runtime smoke summary,
count-only scaffold fixture validation summary, failure handling, and
recording workflow without raw logs, request/pointer bodies, artifact bodies,
raw rows, logits, private paths, or performance claims.
For Step274, confirm the public-safe status marker
[learner-state frozen policy generation scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_scaffold_runtime_release_quality_remote_run_status.md)
records only safe metadata, pass-only runtime smoke summary, and count-only
scaffold fixture validation summary for the successful remote/manual Release
Quality run. Confirm it does not include raw GitHub Actions logs, full job
output, copied log blocks, request/pointer/expected result bodies, generated
or frozen policy artifact bodies, JSON bodies, raw rows, logits/probability
dumps, private paths, raw learner text, real participant data, or performance
metric bodies. Confirm it does not treat runtime smoke success as generator
quality, artifact generation quality, model performance, production
readiness, or real-data readiness.

For Step275, review the
[milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the recap summarizes runtime API/CLI, compatibility tests, Makefile
and release-quality integration, remote/manual status, no-oracle and
synthetic-only boundaries, remaining risks, and next-step guidance without raw
logs, request/pointer bodies, artifact bodies, JSON bodies, raw rows, logits,
private paths, raw learner text, or performance claims.

For Step276, review the
[frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the policy defines artifact metadata, artifact body, artifact file,
manifest, pointer, validation summary, generated frozen policy, generation
result, and runtime scaffold result boundaries. Confirm it keeps initial
generator scaffold behavior metadata-only with `generated_artifact_written=false`,
`generated_artifact_body_available=false`, and `artifact_body_suppressed=true`,
and does not include raw logs, request/pointer bodies, artifact bodies, JSON
bodies, raw rows, logits, private paths, raw learner text, or performance
claims.

For Step277, review the
[frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the design defines a metadata-only generator scaffold boundary,
proposed input/output contracts, data model candidates, API surface
candidates, artifact flags, fail-closed reason codes, no-oracle and
synthetic-only policies, fixture strategy, validation strategy, and
release-quality staging without raw logs, request/pointer bodies, artifact
bodies, JSON bodies, raw rows, logits, private paths, raw learner text, or
performance claims.

For Step278, review the
[frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture creation, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the design defines the future fixture root, case layout, required
common fields, valid and invalid case candidates, malformed/missing input
handling, expected-result contract, artifact flags, safety flags, forbidden
field scan policy, no-oracle and synthetic-only fixture rules, validator
implications, release-quality staging, and non-proofs without raw logs,
request/pointer bodies, artifact bodies, JSON bodies, raw rows, logits,
private paths, raw learner text, or performance claims.

For Step279, review the
[frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
and confirm the fixture root is synthetic-only and metadata-only: no GitHub
Actions workflow change, release-quality wrapper change, Makefile change,
Python code change, Python test change, generator code, fixture validator code,
artifact-body generation, artifact file writing, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. Confirm the root includes three valid
cases, fifteen fail-closed invalid marker cases, required request/pointer/
expected-result files, fixed schema-version labels, required artifact flags,
required safety flags, body-free count summaries, and no raw logs, request
bodies, pointer bodies, artifact bodies, generated policy bodies, raw rows,
logits, private paths, raw learner text, or performance claims.

For Step280, review the
[frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
and confirm it is docs-only: no GitHub Actions workflow change,
release-quality wrapper change, Makefile change, Python code change, Python
test change, fixture change, generator code, fixture validator code,
artifact-body generation, artifact file writing, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. Confirm the design defines the future
validator module, public API candidates, dataclass candidates, discovery
contract, required file contract, schema version checks, required fields,
valid/invalid category checks, expected case lists, artifact flag validation,
safety flag validation, count-summary validation, forbidden marker scan
policy, no-oracle and synthetic-only checks, comparison strategy, summary
output, CLI implications, test strategy, relation to existing validators, and
release-quality staging without raw logs, request/pointer bodies, expected
result bodies, artifact bodies, generated policy bodies, raw rows, logits,
private paths, raw learner text, or performance claims.

For Step281, review
`python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`,
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation.py`,
and the
[frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md).
Confirm the implementation validates only the metadata-only generator scaffold
fixture contract: no CLI, Makefile target, release-quality wrapper change,
GitHub Actions workflow change, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm tests cover discovery counts, required files, JSON parse, schema
labels, valid and invalid expected reason behavior, artifact flags, safety
flags, count-only summaries, forbidden marker scan behavior, malformed/missing
input errors, deterministic discovery, JSON-serializable summaries, and no body
leakage without raw logs, request/pointer bodies, expected result bodies,
artifact bodies, generated policy bodies, raw rows, logits, private paths, raw
learner text, or performance claims.

For Step282, review the
[frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
and confirm it is docs-only: no CLI code, Makefile target, release-quality
wrapper change, GitHub Actions workflow change, Python code change, Python
test change, fixture change, generator code, artifact-body generation,
artifact file writing, calibration/selective prediction logic, estimator work,
metric computation, real-data use, or real-data readiness claim is introduced.
Confirm the design defines the future CLI entrypoint, arguments, root/case
mode behavior, exit codes, safe human output, safe JSON output,
no-body-leakage policy, relation to validator APIs and existing CLIs, future
CLI tests, Makefile staging, and release-quality staging without raw logs,
request/pointer bodies, expected result bodies, artifact bodies, generated
policy bodies, raw rows, logits, private paths, raw learner text, or
performance claims.

For Step283, review
`python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`,
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation_cli.py`,
and the
[frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md).
Confirm the CLI is only a safe metadata-only wrapper over the existing
validator APIs: no Makefile target, release-quality wrapper change, GitHub
Actions workflow change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm root and case modes expose only safe human/JSON
summaries, preserve the exit-code boundary, and avoid raw logs,
request/pointer bodies, expected result bodies, artifact bodies, generated
policy bodies, raw rows, logits, private paths, raw learner text, and
performance claims.

For Step284, review the
[frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
and confirm it is docs-only: no Makefile target, Makefile change,
release-quality wrapper change, GitHub Actions workflow change, Python code
change, Python test change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm the proposed target name, command, help text,
expected output, exit-code interpretation, tmp/output policy, relation to
existing targets, release-quality staging, future target tests, and
no-oracle/synthetic-only boundary are documented without raw logs,
request/pointer bodies, expected result bodies, artifact bodies, generated
policy bodies, raw rows, logits, private paths, raw learner text, or
performance claims.

For Step285, review `Makefile` and the
[frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md).
Confirm the change is limited to the standalone Makefile target, help text,
and docs: no release-quality wrapper change, GitHub Actions workflow change,
Python code change, Python test change, fixture change, generator code,
artifact-body generation, artifact file writing, calibration/selective
prediction logic, estimator work, metric computation, real-data use, or
real-data readiness claim is introduced. Confirm the target runs the safe CLI
root mode, exits `0`, reports 18 matched metadata-only cases, creates no tmp
output, writes no artifacts, and avoids raw logs, request/pointer bodies,
expected result bodies, artifact bodies, generated policy bodies, raw rows,
logits, private paths, raw learner text, and performance claims.

For Step286, review the
[frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
Confirm this is docs-only: no release-quality wrapper change, GitHub Actions
workflow change, Makefile change, Python code change, Python test change,
fixture change, generator code, artifact-body generation, artifact file
writing, calibration/selective prediction logic, estimator work, metric
computation, real-data use, or real-data readiness claim is introduced. Confirm
the proposed wrapper placement is after scaffold runtime smoke and before
config/scoring smoke checks; the proposed label and command remain
metadata-only; failure interpretation is contract/safety failure rather than
generator performance failure; and future status markers are restricted to
pass-only/count-only metadata with no raw logs, request/pointer bodies,
expected result bodies, artifact bodies, generated policy bodies, raw rows,
logits, private paths, raw learner text, or performance claims.

For Step287, review `scripts/check_release_quality.sh` and the
[frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
Confirm the wrapper change is limited to adding the metadata-only generator
scaffold fixture validator target after scaffold runtime smoke and before
config/scoring smoke checks. Confirm there is no GitHub Actions workflow
change, Makefile change, Python code change, Python test change, fixture
change, generator code, artifact-body generation, artifact file writing,
calibration/selective prediction logic, estimator work, metric computation,
real-data use, or real-data readiness claim. Confirm the added release-quality
section reports 18 matched metadata-only cases, keeps `content_suppressed`,
`no_raw_rows`, `no_logits_dump`, `no_private_paths`,
`artifact_policy_checked`, `body_suppression_checked`, and
`file_writing_checked` true, and avoids raw logs, request/pointer bodies,
expected result bodies, artifact bodies, generated policy bodies, raw rows,
logits, private paths, raw learner text, and performance claims.

For Step288, review the
[frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
and confirm it is docs-only: no remote run status marker, GitHub Actions
workflow change, release-quality wrapper change, Makefile change, Python code
change, Python test change, fixture change, generator code, artifact-body
generation, artifact file writing, calibration/selective prediction logic,
estimator work, metric computation, real-data use, or real-data readiness
claim is introduced. Confirm the design defines the future status marker path,
safe metadata fields, forbidden metadata, pass-only/count-only marker
structure, failure handling, and actual recording workflow without raw logs,
request/pointer bodies, expected result bodies, artifact bodies, generated
policy bodies, JSON bodies, raw rows, logits, private paths, raw learner text,
or performance claims.

For Step289, review the public-safe status marker
[learner-state frozen policy generation generator scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md).
Confirm it records only the supplied remote/manual Release Quality metadata,
wrapper inclusion status, pass-only runtime smoke summary, count-only fixture
validation summaries, related learner-state check counts, and safety review.
Confirm it does not copy raw GitHub Actions logs, full job output, generation
request bodies, input pointer bodies, expected generator scaffold result
bodies, generated artifact bodies, frozen policy artifact bodies, JSON bodies,
raw rows, logits/probability dumps, private paths, raw learner text, real
participant data, or performance metric bodies. Confirm no GitHub Actions
workflow, release-quality wrapper, Makefile, Python code, Python tests,
fixtures, generator, artifact writing, artifact body generation, calibration
code, estimator code, metric computation, or real-data readiness claim is
introduced.

For Step290, review the
[frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md).
Confirm it is docs-only and defines the future metadata-only skeleton module,
dataclasses, public APIs, input contract, output contract, artifact flags,
safety flags, count summary, fail-closed behavior, relation to the existing
fixture validator, future tests, future CLI, future Makefile target,
release-quality staging, and status-marker staging. Confirm it does not add
Python code, Python tests, fixtures, Makefile targets, release-quality wrapper
changes, GitHub Actions workflow changes, generator implementation, artifact
body generation, generated policy bodies, artifact file writing, calibration
or selective prediction logic, estimator work, metric computation,
performance evaluation, real-data use, or real-data readiness claims.
Confirm it does not include raw logs, request/pointer bodies, expected
generator scaffold result bodies, artifact bodies, generated policy bodies,
raw rows, logits, private paths, raw learner text, or performance metric
bodies.

For Step291, review the metadata-only generator scaffold skeleton
implementation in `python/learner_state/frozen_policy_generation_generator_scaffold.py`
and focused tests in
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold.py`.
Confirm the implementation reads only safe request/pointer metadata, returns
safe expected-result-compatible summaries, passes valid fixture cases, returns
fail-closed invalid fixture cases, returns safe input errors for malformed or
missing input, does not implement a CLI, does not add a Makefile target, does
not change release-quality or workflows, does not change fixtures, does not
write artifacts, does not generate artifact bodies or generated policy bodies,
does not compute metrics, and does not claim performance or real-data
readiness. Confirm tests do not print fixture bodies or write artifacts.

For Step292, review the
[frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md).
Confirm it is docs-only and defines the future safe CLI entrypoint,
arguments, example commands, expected behavior, exit codes, safe human output,
safe JSON output, no-body-leakage policy, relation to skeleton APIs, relation
to the fixture validator CLI, future CLI tests, Makefile staging,
release-quality staging, and status-marker staging. Confirm it does not add
Python code, Python tests, fixtures, Makefile targets, release-quality wrapper
changes, GitHub Actions workflow changes, artifact file writing, artifact body
generation, generated policy body generation, artifact manifest writing,
calibration/selective prediction logic, estimator work, metric computation,
performance evaluation, real-data use, or real-data readiness claims. Confirm
it does not include raw logs, request/pointer bodies, expected generator
scaffold result bodies, artifact bodies, generated policy bodies, raw rows,
logits, private paths, raw learner text, or performance metric bodies.

For Step293, review the generator scaffold CLI implementation in
`python/learner_state/frozen_policy_generation_generator_scaffold.py` and
focused CLI tests in
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_cli.py`.
Confirm the CLI is a thin wrapper over the skeleton APIs, supports
`--request`, `--pointer`, `--json`, and `--help`, returns safe human/JSON
metadata, exits `0` for valid pass and expected fail-closed invalid cases,
exits `2` for usage/input errors, and does not write artifacts or generate
artifact/policy bodies. Confirm stdout/stderr do not include request bodies,
pointer bodies, expected result bodies, artifact bodies, generated policy
bodies, raw rows, logits, private paths, raw learner text, or performance
metric bodies. Confirm no Makefile target, release-quality wrapper change,
GitHub Actions workflow change, fixture change, calibration/selective
prediction logic, estimator work, metric computation, performance evaluation,
real-data use, or real-data readiness claim is introduced.

For Step294, review the
[frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md).
Confirm it is docs-only and defines the future target name, valid-only command,
help text, expected behavior, exit-code interpretation, output/logging safety,
tmp/output policy, relation to existing targets, future implementation tests,
release-quality staging, status-marker staging, and synthetic-only/no-oracle
boundary. Confirm it does not add a Makefile target, release-quality wrapper
change, GitHub Actions workflow change, Python code, Python tests, fixtures,
artifact file writing, artifact body generation, generated policy body
generation, artifact manifest writing, calibration/selective prediction logic,
estimator work, metric computation, performance evaluation, real-data use, or
real-data readiness claim. Confirm it does not include raw logs,
request/pointer bodies, expected generator scaffold result bodies, artifact
bodies, generated policy bodies, raw rows, logits, private paths, raw learner
text, or performance metric bodies.

For Step295, review `Makefile` and
[frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md).
Confirm the change is limited to `.PHONY`, `make help`, the standalone
`check-learner-state-frozen-policy-generation-generator-scaffold-runtime`
target, and docs. Confirm the target runs one valid synthetic request/pointer
pair through the safe generator scaffold CLI, exits `0`, emits only
metadata-only output, creates no target-specific tmp output, writes no
artifacts, emits no artifact body or generated policy body, and does not add
release-quality wrapper changes, GitHub Actions workflow changes, Python code,
Python tests, fixtures, calibration/selective prediction logic, estimator
work, metric computation, performance evaluation, real-data use, or
real-data readiness claims.

For Step296, review the
[frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md).
Confirm it is docs-only and defines the future wrapper insertion point,
Makefile command, release-quality label, expected wrapper behavior, failure
interpretation, log safety, relationship to existing release-quality checks,
future implementation tests, status-marker staging, and synthetic-only/no-oracle
boundary. Confirm it does not change the release-quality wrapper, GitHub
Actions workflow, Makefile, Python code, Python tests, fixtures, artifact file
writing, artifact body generation, generated policy body generation, artifact
manifest writing, calibration/selective prediction logic, estimator work,
metric computation, performance evaluation, real-data use, or real-data
readiness claims. Confirm it does not include raw logs, request/pointer bodies,
expected generator scaffold result bodies, policy bodies, generated policy
bodies, artifact bodies, raw rows, logits, private paths, raw learner text, or
performance metric bodies.

## 7. Checks To Run

The wrapper covers the normal success-path command bundle. The individual
commands remain useful as a manual fallback or for targeted reruns.

```bash
scripts/check_release_quality.sh
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
scripts/check_synthetic_policy.sh
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
make check-learner-state-audit-fixtures
cd apps/logger-web && npm run typecheck
cd apps/logger-web && npm test
cd apps/logger-web && npm run build
scripts/check_no_config_scoring_fixture_lock.sh
scripts/check_hand_weight_config_validation.sh
scripts/check_explicit_config_ranking_diff.sh
scripts/check_config_enabled_e2e_smoke.sh
scripts/check_config_enabled_summary_smoke.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

## 8. Current Non-Goals

Do not claim:

- production readiness
- real participant evaluation
- F1
- accuracy
- calibration
- learner-state estimation
- automatic weight learning
- private validation
- model performance
- public data release readiness

Before any private real-data work, read `docs/private_real_data_readiness_checklist.md`.
