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

# check-release-quality already runs the normal success-path command bundle.
check-all: check-release-quality
