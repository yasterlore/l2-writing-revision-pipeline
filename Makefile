.PHONY: help
.PHONY: check-release-quality
.PHONY: check-summary
.PHONY: check-manifest-sync
.PHONY: check-diagnostic-distribution
.PHONY: check-summary-flow
.PHONY: check-config-smoke
.PHONY: check-python
.PHONY: check-rust
.PHONY: check-logger
.PHONY: check-policy
.PHONY: check-fixtures
.PHONY: check-learner-state-audit-fixtures
.PHONY: check-learner-state-exporter-cli
.PHONY: check-learner-state-estimator-input
.PHONY: check-learner-state-selective-prediction
.PHONY: check-learner-state-frozen-policy
.PHONY: check-learner-state-frozen-policy-generation
.PHONY: check-learner-state-frozen-policy-generation-scaffold-fixtures
.PHONY: check-learner-state-frozen-policy-generation-scaffold-runtime
.PHONY: check-learner-state-frozen-policy-generation-generator-scaffold-fixtures
.PHONY: check-learner-state-frozen-policy-generation-generator-scaffold-runtime
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime
.PHONY: check-learner-state-frozen-policy-generation-artifact-writer-runtime
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-generation
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke
.PHONY: check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-fixtures
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-runtime
.PHONY: check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing
.PHONY: check-all

# Shared tmp outputs are not safe for parallel summary-flow checks.
.NOTPARALLEL:

help:
	@echo "Available targets:"
	@echo "  note: do not use make -j with summary-flow targets"
	@echo "  check-release-quality        Run the normal release-quality wrapper"
	@echo "  check-summary-flow           Run summary, manifest sync, and diagnostic distribution"
	@echo "  check-summary                Generate the synthetic E2E summary"
	@echo "  check-manifest-sync          Check summary manifest schema constants sync"
	@echo "  check-diagnostic-distribution Check synthetic diagnostic distribution"
	@echo "  check-config-smoke           Run config-enabled summary and E2E smoke checks"
	@echo "  check-python                 Run Python unittest and compileall"
	@echo "  check-rust                   Run Rust fmt, test, and clippy"
	@echo "  check-logger                 Run logger-web typecheck, test, and build"
	@echo "  check-policy                 Run synthetic policy checks"
	@echo "  check-fixtures               Run fixture/config validation checks"
	@echo "  check-learner-state-audit-fixtures  Audit synthetic learner-state fixtures"
	@echo "  check-learner-state-exporter-cli  Smoke-test learner-state exporter CLI"
	@echo "  check-learner-state-estimator-input  Smoke-test learner-state estimator input validation"
	@echo "  check-learner-state-selective-prediction  Smoke-test selective prediction calibration validation"
	@echo "  check-learner-state-frozen-policy  Smoke-test frozen selective prediction policy validation"
	@echo "  check-learner-state-frozen-policy-generation  Smoke-test frozen policy generation fixture validation"
	@echo "  check-learner-state-frozen-policy-generation-scaffold-fixtures  Smoke-test frozen policy generation scaffold fixture validation"
	@echo "  check-learner-state-frozen-policy-generation-scaffold-runtime  Smoke-test frozen policy generation scaffold runtime CLI"
	@echo "  check-learner-state-frozen-policy-generation-generator-scaffold-fixtures  Validate frozen policy generation generator scaffold fixtures"
	@echo "  check-learner-state-frozen-policy-generation-generator-scaffold-runtime  Run frozen policy generation generator scaffold runtime smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-fixtures  Validate frozen policy generation artifact writer fixtures"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures  Validate artifact writer CLI integration fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures  Validate artifact writer CLI integration runtime fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures  Run artifact writer CLI actual invocation fixture validation"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime  Run artifact writer CLI integration runtime smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime  Run artifact writer CLI actual invocation metadata-only runtime smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-writer-runtime  Run frozen policy generation artifact writer runtime smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-fixtures  Validate frozen policy generation artifact body fixtures"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures  Run artifact body generation integration fixture validation"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration  Run artifact body generation runtime integration plan-only bridge smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-generation  Run artifact body generation CLI smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata  Run artifact body generation safe-metadata CLI smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures  Validate artifact body file writing fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke  Run artifact body safe-metadata file writing smoke"
	@echo "  check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation  Validate isolated artifact body file writing cases"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation  Validate manifest writer metadata-only isolated write behavior"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures  Validate manifest writer metadata-only file writing fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures  Validate manifest writer production metadata-only file writing fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-fixtures  Validate manifest writer fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures  Validate manifest writer runtime fixture contracts"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-runtime  Smoke test manifest writer metadata-only runtime"
	@echo "  check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing  Smoke test manifest writer metadata-only runtime file writing"
	@echo "  check-all                    Run the normal release-quality wrapper"

check-release-quality:
	scripts/check_release_quality.sh

check-summary:
	scripts/run_synthetic_e2e_summary.sh

check-manifest-sync:
	scripts/check_summary_manifest_schema_sync.sh

check-diagnostic-distribution:
	scripts/check_synthetic_diagnostic_distribution.sh

check-summary-flow:
	scripts/run_synthetic_e2e_summary.sh
	scripts/check_summary_manifest_schema_sync.sh
	scripts/check_synthetic_diagnostic_distribution.sh

check-config-smoke:
	scripts/check_config_enabled_summary_smoke.sh
	scripts/check_config_enabled_e2e_smoke.sh

check-python:
	PYTHONPATH=python python3 -m unittest discover -s python
	PYTHONPATH=python python3 -m compileall python

check-rust:
	cargo fmt --all -- --check
	cargo test --workspace
	cargo clippy --workspace -- -D warnings

check-logger:
	cd apps/logger-web && npm run typecheck
	cd apps/logger-web && npm test
	cd apps/logger-web && npm run build

check-policy:
	scripts/check_synthetic_policy.sh

check-fixtures:
	scripts/check_no_config_scoring_fixture_lock.sh
	scripts/check_hand_weight_config_validation.sh
	scripts/check_explicit_config_ranking_diff.sh

check-learner-state-audit-fixtures:
	PYTHONPATH=python python3 -m learner_state.sequence_audit --fixture-root tests/fixtures/learner_state_sequence_audit

check-learner-state-exporter-cli:
	rm -rf tmp/learner_state_sequence_exporter_smoke
	PYTHONPATH=python python3 -m learner_state.sequence_exporter --input-fixture tests/fixtures/learner_state_sequence_exporter/valid/minimal_single_participant --output-dir tmp/learner_state_sequence_exporter_smoke/minimal_single_participant
	PYTHONPATH=python python3 -m learner_state.sequence_exporter --input-fixture tests/fixtures/learner_state_sequence_exporter/valid/past_window_boundary_reset --output-dir tmp/learner_state_sequence_exporter_smoke/past_window_boundary_reset

check-learner-state-estimator-input:
	PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input

check-learner-state-selective-prediction:
	PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-root tests/fixtures/learner_state_selective_prediction

check-learner-state-frozen-policy:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_validation --fixture-root tests/fixtures/learner_state_frozen_selective_prediction_policy

check-learner-state-frozen-policy-generation:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation

check-learner-state-frozen-policy-generation-scaffold-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_scaffold

check-learner-state-frozen-policy-generation-scaffold-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation --request tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/input_fixture_pointer.json

check-learner-state-frozen-policy-generation-generator-scaffold-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold

check-learner-state-frozen-policy-generation-generator-scaffold-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/input_fixture_pointer.json

check-learner-state-frozen-policy-generation-artifact-writer-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer

check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration

check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime

check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation

check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime --fixture-case valid/valid_minimal_metadata_runtime_pass

check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime --fixture-case valid/valid_actual_invocation_minimal_metadata_only --actual-invocation --summary-only --no-file-writing

check-learner-state-frozen-policy-generation-artifact-writer-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json

check-learner-state-frozen-policy-generation-artifact-body-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body

check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_integration_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration

check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration --fixture-case valid/valid_minimal_suppressed_metadata_only_bridge --mode plan-only-bridge --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output

check-learner-state-frozen-policy-generation-artifact-body-generation:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/minimal_suppressed_metadata_only_body/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/minimal_suppressed_metadata_only_body/artifact_writer_result_pointer.json

check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_writer_result_pointer.json --mode safe-metadata

check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing

check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke:
	@set -e; \
	output="tmp/artifact_body_generation/smoke/safe_metadata_artifact_body.json"; \
	cleanup() { rm -f "$$output"; rmdir tmp/artifact_body_generation/smoke 2>/dev/null || true; rmdir tmp/artifact_body_generation 2>/dev/null || true; }; \
	trap cleanup EXIT; \
	rm -f "$$output"; \
	mkdir -p tmp/artifact_body_generation/smoke; \
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_writer_result_pointer.json --mode safe-metadata --artifact-body-out smoke/safe_metadata_artifact_body.json; \
	python3 -m json.tool "$$output" >/dev/null; \
	if grep -Eq '"raw_rows"|"raw_event_rows"|"logits"|"probabilities"|"private_path"|"manifest_body"|"generated_policy_body"|"request_body"|"pointer_body"|"artifact_body_request"|"artifact_writer_result_pointer"|"expected_file_write_result"' "$$output"; then \
		echo "artifact_body_file_writing_smoke_safety_scan=fail"; \
		exit 1; \
	fi; \
	echo "artifact_body_file_writing_smoke_json_parse=pass"; \
	echo "artifact_body_file_writing_smoke_safety_scan=pass"; \
	cleanup; \
	if test -e "$$output"; then \
		echo "artifact_body_file_writing_smoke_cleanup=fail"; \
		exit 1; \
	fi; \
	echo "artifact_body_file_writing_smoke_cleanup=pass"

check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation

check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation

check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing

check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing

check-learner-state-frozen-policy-generation-manifest-writer-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer

check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime

check-learner-state-frozen-policy-generation-manifest-writer-runtime:
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer --request tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/manifest_writer_request.json --artifact-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_writer_result_pointer.json --artifact-body-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_body_generation_result_pointer.json

check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing:
	@set -e; \
	smoke_dir="tmp/frozen_policy_generation_manifest/smoke"; \
	output="$$smoke_dir/manifest.json"; \
	stdout_file="$$smoke_dir/runtime.stdout"; \
	stderr_file="$$smoke_dir/runtime.stderr"; \
	cleanup() { rm -rf "$$smoke_dir"; }; \
	trap cleanup EXIT; \
	cleanup; \
	mkdir -p "$$smoke_dir"; \
	PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer --request tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/manifest_writer_request.json --artifact-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_writer_result_pointer.json --artifact-body-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_body_generation_result_pointer.json --manifest-out smoke/manifest.json >"$$stdout_file" 2>"$$stderr_file"; \
	if ! grep -q '^manifest_file_written=true$$' "$$stdout_file"; then \
		echo "manifest_writer_runtime_file_writing_smoke=fail"; \
		exit 1; \
	fi; \
	if ! grep -q '"written_file_count":1' "$$stdout_file"; then \
		echo "manifest_writer_runtime_file_writing_smoke=fail"; \
		exit 1; \
	fi; \
	if test ! -f "$$output"; then \
		echo "manifest_writer_runtime_file_writing_smoke=fail"; \
		exit 1; \
	fi; \
	python3 -m json.tool "$$output" >/dev/null; \
	if grep -Eiq '"manifest_body"|"manifest_json_body"|"artifact_body_payload"|"generated_policy_body"|"request_body"|"pointer_body"|"expected_body"|"raw_rows"|"raw_row"|"logits"|"probabilities"|"private_path"|"absolute_path"|"raw_learner_text"|"final_text"|"observed_after_text"|"gold_label"|"scoring_feedback"|"real_participant_data"|"performance_metric_body"|/Users/|/home/|/tmp/|Dropbox|CloudStorage' "$$output"; then \
		echo "manifest_writer_runtime_file_writing_smoke_safety_scan=fail"; \
		exit 1; \
	fi; \
	if grep -Eiq '"manifest_body":|"manifest_json_body":|"artifact_body_payload":|"generated_policy_body":|"request_body":|"pointer_body":|"expected_body":|"raw_rows":|"logits":|"probabilities":|"raw_learner_text":|"final_text":|"observed_after_text":|"gold_label":|"scoring_feedback":|"real_participant_data":|"performance_metric_body":|/Users/|/home/|/tmp/|/private/|/var/folders/|Dropbox|CloudStorage' "$$stdout_file" "$$stderr_file"; then \
		echo "manifest_writer_runtime_file_writing_smoke_public_output_scan=fail"; \
		exit 1; \
	fi; \
	cat "$$stdout_file"; \
	if test -s "$$stderr_file"; then cat "$$stderr_file"; fi; \
	echo "written_file_count=1"; \
	echo "manifest_body_suppressed=true"; \
	echo "file_writing_checked=true"; \
	echo "output_path_safety_checked=true"; \
	echo "content_policy_checked=true"; \
	echo "no_manifest_body=true"; \
	echo "no_artifact_body_payload=true"; \
	echo "no_generated_policy_body=true"; \
	echo "no_request_body=true"; \
	echo "no_pointer_body=true"; \
	echo "no_expected_body=true"; \
	echo "no_raw_rows=true"; \
	echo "no_logits_dump=true"; \
	echo "no_private_paths=true"; \
	echo "no_absolute_paths=true"; \
	echo "no_performance_claims=true"; \
	echo "synthetic_only_checked=true"; \
	echo "no_oracle_checked=true"; \
	echo "manifest_writer_runtime_file_writing_smoke=ok"; \
	echo "manifest_writer_runtime_file_writing_smoke_json_parse=pass"; \
	echo "manifest_writer_runtime_file_writing_smoke_safety_scan=pass"; \
	cleanup; \
	if test -e "$$smoke_dir"; then \
		echo "manifest_writer_runtime_file_writing_smoke_cleanup=fail"; \
		exit 1; \
	fi; \
	echo "smoke_residue_file_count=0"

# check-release-quality already runs the normal success-path command bundle.
check-all: check-release-quality
