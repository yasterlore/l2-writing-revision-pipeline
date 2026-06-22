# Learner-State Sequence Exporter Design

This document designs a future synthetic learner-state sequence exporter. The
exporter would generate an audit-ready learner-state sequence dataset by
separating feature rows, label rows, and manifest metadata.

This is design documentation only. It does not implement a sequence exporter,
learner-state estimator, new model, new metric, real-data pipeline, workflow
change, Makefile change, release-quality wrapper change, audit-code change, or
fixture-file change. It does not change candidate generation, OT scoring,
scoring formula, tie-break behavior, or existing manifest schemas. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define how a future learner-state sequence
exporter should produce synthetic-only, audit-ready sequence data.

The design covers:

- input sources
- output files
- feature row boundaries
- label row boundaries
- manifest metadata
- processing order
- past-only window features
- split handling
- no-oracle audit integration
- safe output policy
- future module and CLI location
- minimal implementation roadmap

The exporter must preserve the no-oracle, synthetic-only, and no-future-leakage
boundaries already established by the learner-state audit infrastructure.

## 2. One-Sentence Summary

The future exporter should take synthetic safe micro-episodes, candidate score
sets, diagnostic summaries, synthetic expected-action labels, and safe
participant/session/task metadata as input, then emit separated `features.jsonl`,
`labels.jsonl`, `manifest.json`, and optional count-only `summary.json` files
that can be checked by the learner-state sequence audit before use.

## 3. Input Sources

Allowed future input sources:

- `SafeEpisodeView`
- no-oracle-safe micro-episode metadata
- `CandidateScoreSet`
- candidate action family metadata
- diagnostic count-only summaries
- synthetic expected action registry, for labels only
- synthetic participant, session, and task metadata
- synthetic split metadata
- previous-window features computed only from current and past episodes

Forbidden input sources:

- `final_text`
- `observed_after_text`
- `gold_label`
- raw learner text
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future episode
- final essay outcome
- real participant data
- private/manual/real-data paths as dataset sources
- expected action as feature input
- expected action as scorer, ranker, or candidate-generation feedback

The exporter should reject or ignore any candidate source whose no-oracle status
is unclear until a separate design review approves it.

## 4. Output Files

Recommended future output set:

| File | Role | Public-safety rule |
| --- | --- | --- |
| `features.jsonl` | One no-oracle-safe feature row per synthetic micro-episode | Never paste row body into docs |
| `labels.jsonl` | Evaluation-only synthetic expected-action labels | Keep separate from features and scorer inputs |
| `manifest.json` | Dataset-level metadata, versions, counts, paths, and audit placeholders | Count-only; no row dumps |
| `summary.json` | Optional count-only public summary | No row body, label body, or candidate score rows |

This document does not create any output files. Public docs should describe
field names and counts only, not JSONL lines or manifest bodies.

## 5. Feature Row Design

Allowed feature row candidates:

- `schema_version`
- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- safe `micro_episode_id`
- `episode_order_index`
- safe task/session order metadata
- boundary markers for participant, session, and task starts
- no-oracle micro-episode derived features
- candidate-family score summaries
- top-ranked candidate family
- top-k candidate family summary, if summarized safely
- blocked candidate count
- diagnostic count-only features
- past-only rolling window aggregates
- split label as metadata, only if assigned without labels or outcomes

Feature rows must not include:

- `expected_action`
- expected action family or type
- label fields
- final outcome
- future summary
- future edit count
- raw text
- `observed_after_text`
- `final_text`
- `gold_label`
- teacher or human correction fields
- real participant identifiers
- private paths
- candidate score row dumps

Candidate and diagnostic information should be summarized as safe categorical
or count-only features. Raw candidate bodies, raw score rows, and raw text must
remain outside the feature path.

## 6. Label Row Design

Allowed label row candidates:

- `label_schema_version`
- the same safe synthetic join keys as feature rows
- synthetic expected action family
- synthetic expected action type
- label source, such as synthetic expected-action registry

Label rows are evaluation-only. They are not model inputs for the exporter
itself, not scorer feedback, not candidate-generation input, and not ranking
feedback.

Label rows must not contain feature vectors, candidate score summaries,
diagnostic features, real correction sources, teacher corrections, human
corrections, or post-hoc annotations.

## 7. Manifest Design

Allowed manifest candidates:

- `manifest_schema_version`
- dataset schema version
- feature schema version
- label schema version
- `synthetic_only: true`
- `content_suppressed: true`
- count-only feature row count
- count-only label row count
- participant/session/task/episode counts
- split counts
- input source categories, not raw private paths
- output file category paths, sanitized and repository-relative when possible
- audit status placeholder or audit result summary
- forbidden-fields-absent summary
- no-real-data note
- no-row-body note

Manifest contents must not include:

- raw row dumps
- full JSONL body
- label body
- manifest body copied from generated output into docs
- candidate score rows
- raw learner text
- expected action body
- private absolute paths
- real-data source paths

This future learner-state sequence manifest is separate from existing summary
manifest schemas. This design does not change any existing manifest schema.

## 8. Processing Order

Recommended future processing order:

1. Load safe synthetic inputs.
2. Validate input source categories and schema versions.
3. Construct feature rows from current episode and past-only context.
4. Construct label rows separately from the synthetic expected-action registry.
5. Construct a count-only manifest with content suppression enabled.
6. Run the learner-state sequence audit on the generated outputs.
7. Fail the exporter if the audit fails.
8. Write outputs atomically if practical in the future implementation.
9. Emit a safe count-only summary.

The exporter should not print raw rows, labels, manifests, or candidate score
details to stdout. When an error occurs, it should report safe category and
reason-code information only.

## 9. Past-Only Window Feature Design

Past-only window features may be useful for local learner-state tendency
signals, but they must be computed carefully.

Rules:

- use only previous `N` episodes and the current episode when explicitly safe
- reset windows at participant boundaries
- reset or clearly mark windows at session and task boundaries
- do not include future episodes
- do not include final task length when that requires future knowledge
- do not include final essay outcome
- do not include label-based aggregates
- do not include expected action aggregates in features
- do not compute progress from future-derived total episode count

Safe examples are count-only summaries of earlier candidate-family outcomes,
earlier blocked counts, or earlier diagnostic count categories. The future
implementation should still audit these fields because rolling features are a
common source of future leakage.

## 10. Split Handling

Split handling should support learner-disjoint evaluation without leaking
labels or outcomes.

Rules:

- use synthetic participant IDs only
- support learner-disjoint split metadata
- optionally support task-disjoint split metadata later
- do not assign splits based on expected actions
- do not assign splits based on final outcomes, correctness, or labels
- ensure the same synthetic participant does not appear across train,
  validation, and test splits for learner-disjoint split families
- store split summaries count-only in the manifest
- fail audit if split leakage is detected

Split metadata may appear in feature rows only if it is safe, synthetic, and
does not encode labels or outcomes.

## 11. Audit Integration

Exporter outputs should be audited by the existing learner-state sequence audit
module before downstream use.

Integration rules:

- run `learner_state.sequence_audit` on generated `features.jsonl`,
  `labels.jsonl`, and `manifest.json`
- fail the exporter if the audit fails
- keep audit result output safe and count-only
- do not print row bodies on failure
- do not print label contents on failure
- do not print manifest bodies on failure
- fixture-root audit remains separate from exporter-output audit
- fixture-root audit continues to test expected-fail synthetic cases
- exporter-output audit checks generated synthetic sequence outputs

The future exporter should treat audit pass as a safety precondition, not as a
research-quality or model-performance result.

## 12. Output Safety

Output safety rules:

- no raw row body in stdout
- no labels printed
- no manifest body printed
- no candidate score row dumps
- no private paths
- no raw learner text
- no raw GitHub Actions logs in docs
- public summaries are count-only
- failure messages use safe reason codes and categories
- generated outputs should not be added from `tmp/` or `manual_outputs/`

Docs may mention file names, schema families, field names, and count-only
summaries. Docs must not paste generated JSONL bodies or generated manifest
bodies.

## 13. Module / CLI Future Location

Possible future locations:

- module: `python/learner_state/sequence_exporter.py`
- CLI: `python -m learner_state.sequence_exporter`
- tests: `python/learner_state/tests/`
- synthetic input fixtures: a dedicated test fixture root chosen in a future
  fixture/input design step

Initial recommendation:

- implement in Python first because JSON/JSONL handling, audit integration, and
  fixture tests are already Python-based
- keep the core exporter as a library function
- keep CLI as a thin wrapper over the library function
- avoid a Makefile target until exporter smoke tests are stable

This step does not create files in these locations.

## 14. Minimal Implementation Roadmap

Recommended next steps:

1. Step 176: synthetic exporter fixture/input design.
2. Step 177: minimal exporter implementation for synthetic-only inputs.
3. Step 178: exporter audit integration tests.
4. Step 179: Makefile target design and optional implementation.
5. Step 180: release-quality integration review after smoke tests stabilize.

Possible adjustment: add extra audit fixtures for malformed input, empty input,
unknown version, and multi-violation cases before Step 177 if the exporter
needs stronger fail-closed coverage first.

## 15. Relation To Existing Pipeline

The exporter sits between existing safe synthetic pipeline components and future
learner-state modeling.

Relationships:

- Rust safe view and no-oracle audit define safe episode surfaces.
- Micro-episode records provide the sequence unit.
- Python candidate generation produces candidate metadata and score sets.
- `CandidateScoreSet` provides no-oracle candidate scoring summaries.
- Diagnostic summaries provide count-only descriptive features.
- Synthetic expected-action registry provides evaluation-only labels.
- Learner-state sequence audit checks generated feature/label/manifest outputs.
- Makefile and release-quality infrastructure provide the current check surface.

The exporter should not change candidate generation, scoring, ranking,
tie-breaks, diagnostic construction, or existing summary manifests.

## 16. What This Does Not Do

This design does not:

- implement the exporter
- train a learner-state estimator
- implement a new model
- implement new metrics
- evaluate F1, accuracy, calibration, ECE, or AURCC
- use real data
- prove model validity
- prove scorer quality
- prove learner-state construct validity
- claim production readiness
- claim data-collection readiness
- change audit code or fixtures
- change Makefile, wrapper, workflows, scripts, or tests
- use expected action as scoring feedback

## 17. Beginner Notes

An exporter is a program that takes already-safe internal data and writes it
into a dataset format that another tool can read later.

Feature and label files are separate because features are inputs, while labels
are answers used only for evaluation. Mixing them would let a future model see
the answer.

The audit runs after export so the generated files can be checked for forbidden
fields, label leakage, future leakage, unsafe paths, and manifest body leakage
before anyone trains or evaluates a model.

Past-only windows are needed because learner-state work often depends on recent
history. The rule is that the current row may only see the past, never future
episodes.

The exporter is not a model. It prepares safe synthetic data. It does not learn,
predict, score research performance, or validate learner-state quality.

## 18. Related Documents

- [Milestone 06 learner-state audit infrastructure recap](milestone_06_learner_state_audit_infrastructure_recap.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
- [Learner-state sequence audit CLI design](learner_state_sequence_audit_cli_design.md)
- [Learner-state audit release-quality remote run status](status/learner_state_audit_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
