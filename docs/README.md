# Documentation Index

This directory contains architecture notes, policies, specs, and milestone recaps.

Recommended entry points:

- [Milestone 01 pipeline recap](milestone_01_pipeline_recap.md): beginner-friendly recap of the current pipeline foundation.
- [Milestone 02 synthetic evaluation recap](milestone_02_synthetic_evaluation_recap.md): beginner-friendly recap of the synthetic evaluation wiring milestone.
- [System architecture](02_system_architecture.md): language boundaries and component layout.
- [No-oracle policy](03_no_oracle_policy.md): no-oracle rules for candidate generation, ranking, scoring, and learner-state work.
- [Data quality policy](10_data_quality_policy.md): validation and data-quality rules.
- [Synthetic data policy](12_synthetic_data_policy.md): synthetic-only development policy.
- [Private real-data readiness checklist](private_real_data_readiness_checklist.md): Go / No-Go checklist before any private real-data trial.
- [Evaluation spec](evaluation_spec.md): synthetic-only evaluation schema.
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md): Rust + Python synthetic E2E pipeline scripts.
- [Scoring policy refinement plan](scoring_policy_refinement_plan.md): planned no-oracle-safe scorer improvements.
- [Diagnostic-to-scoring boundary review](diagnostic_to_scoring_boundary_review.md): boundary review before connecting diagnostics to hand-weight scoring policy.
- [Hand-weight policy design](hand_weight_policy_design.md): design principles for future interpretable hand-designed scoring weights.
- [Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md): narrow selection plan for future score-active constraint families.
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md): schema design for future explicit hand-weight configuration.
- [Default-unchanged config support design](default_unchanged_config_support_design.md): safety design for future config support without changing default scoring behavior.
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md): design plan for locking no-config scoring output before config support.
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md): design plan for future explicit-config ranking diff checks without changing no-config defaults.
- [Config-aware scorer function design](config_aware_scorer_function_design.md): design plan for a future explicit config-aware scorer path that preserves no-config defaults.
- [Explicit config CLI option design](explicit_config_cli_option_design.md): design record for explicit `score.py --weight-config` support while preserving no-config defaults.
- [Config-enabled E2E design](config_enabled_e2e_design.md): design plan for optional explicit config-enabled synthetic E2E while keeping default E2E no-config.
- [Config-enabled summary collector design](config_enabled_summary_collector_design.md): separate config-enabled E2E summary collector design and implementation notes without changing no-config summary.
- [Linguistic placeholder constraint plan](linguistic_placeholder_constraint_plan.md): design plan for future descriptive linguistic placeholder constraints.
- [Non-leaky linguistic constraint design plan](non_leaky_linguistic_constraint_design_plan.md): design plan for future descriptive linguistic diagnostics using no-oracle-safe local pattern features.
- [Local pattern feature plan](local_pattern_feature_plan.md): design plan for future no-oracle-safe local context abstractions.
- [Local pattern feature schema v0.3 plan](local_pattern_feature_schema_v0_3_plan.md): implemented initial CandidateFeatureSet v0.3 field definitions.
- [Local pattern diagnostic constraint plan](local_pattern_diagnostic_constraint_plan.md): design plan for descriptive diagnostics derived from v0.3 local pattern features.
- [Diagnostic summary tooling plan](diagnostic_summary_tooling_plan.md): safe summary-only aggregation of descriptive diagnostics.
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md): safe review plan for count-only synthetic diagnostic distributions.
- [Synthetic diagnostic observation note template](templates/synthetic_diagnostic_observation_note_template.md): count-only note template for safe human diagnostic review.
- [Config-enabled observation note template](templates/config_enabled_observation_note_template.md): count-only note template for safe human review of explicit config-enabled summaries.
- [Public release checklist](public_release_checklist.md): public GitHub readiness checklist.

Do not paste JSONL contents, real participant text, private data, or production outputs into documentation.
