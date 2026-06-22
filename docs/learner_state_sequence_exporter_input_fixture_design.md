# Learner-State Sequence Exporter Input Fixture Design

This document designs future synthetic input fixtures and input contracts for a
minimal learner-state sequence exporter.

It is design documentation only. It does not create fixture files, implement a
sequence exporter, implement a learner-state estimator, add a model, add a
metric, change audit code, change existing fixtures, change workflows, change
Makefile targets, change release-quality wrapper behavior, or change scorer,
candidate, tie-break, or manifest logic. It is not a performance evaluation and
is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define the shape of synthetic input fixtures
that a future learner-state sequence exporter may read.

The design covers:

- fixture root options
- fixture case structure
- input file set
- minimal valid input contract
- expected output contract metadata
- relation to existing audit fixtures
- no-oracle and leakage checks before implementation
- first fixture priority
- future module and CLI connection
- output and logging safety

No fixture directories or fixture files are created in this step.

## 2. One-Sentence Summary

A minimal synthetic exporter input fixture should keep safe micro-episode
views, candidate score summaries, diagnostic summaries, synthetic expected
action labels, and synthetic grouping metadata separated so that the future
exporter can generate separated `features.jsonl`, `labels.jsonl`, and
`manifest.json` outputs for audit.

## 3. Fixture Root Candidate

Candidate roots:

| Candidate root | Pros | Cons | Recommendation |
| --- | --- | --- | --- |
| `tests/fixtures/learner_state_sequence_exporter/` | Language-neutral, visible beside existing audit fixtures, usable from Python tests and future Makefile checks | Adds a new fixture family | Recommended |
| `tests/fixtures/learner_state_sequence/` | Broad name could cover exporter and audit data | May blur generated sequence outputs, exporter inputs, and audit fixtures | Not preferred initially |
| `python/learner_state/tests/fixtures/` | Close to future Python exporter tests | Python-specific and less visible to cross-pipeline checks | Possible later for package-local helpers |
| `tests/fixtures/synthetic/learner_state_sequence_exporter/` | Clear synthetic grouping | Deeper path and new convention | Acceptable later if fixture families grow |
| `docs/examples/` | Easy to browse | Encourages copying JSON/JSONL bodies into docs | Avoid |

Initial recommendation:

`tests/fixtures/learner_state_sequence_exporter/`

Rationale:

- it is language-neutral
- it sits near the existing `tests/fixtures/learner_state_sequence_audit/`
  family
- it keeps exporter inputs separate from audit fixtures
- docs can link to the fixture root later without copying row bodies

## 4. Fixture Case Structure

Future case structure candidates:

```text
tests/fixtures/learner_state_sequence_exporter/
  valid/
    minimal_single_participant/
    multi_episode_single_task/
    multi_task_split_ready/
  invalid/
    missing_safe_view/
    label_in_feature_input/
    future_window_input/
    split_leakage_input/
```

This step does not create these directories.

The first implementation should start with one valid case only. Invalid exporter
input fixtures can follow once the minimal exporter can read the valid case and
produce auditable outputs.

## 5. Input File Set

Each future fixture case may contain:

| File | Role | Public docs policy |
| --- | --- | --- |
| `safe_episodes.jsonl` | Synthetic no-oracle-safe episode or micro-episode input records | Do not paste row body |
| `candidate_scores.jsonl` | Candidate-family score summaries or safe score metadata | Do not paste score rows |
| `diagnostic_summary.json` | Count-only diagnostic summary metadata | Field-level overview only |
| `expected_actions.jsonl` or `labels_source.jsonl` | Synthetic expected-action labels for evaluation output only | Do not paste label body |
| `synthetic_metadata.json` | Synthetic participant/session/task grouping metadata | Count and field-level overview only |
| `split_metadata.json` | Synthetic split assignments, if used | Count-only and no label-derived splits |
| `expected_output_contract.json` | Safe metadata expectations for generated output | Do not include generated row bodies |
| `README.md` | Optional short case note | No fixture body dumps |

The input file set should keep expected-action labels outside safe episode and
candidate score inputs. The exporter should join them only to build label rows,
not feature rows.

## 6. Minimal Valid Input Contract

The first valid input case should include:

- one synthetic participant
- one synthetic session
- one synthetic task
- two or three ordered synthetic micro-episodes
- safe synthetic participant/session/task IDs
- ordered synthetic micro-episode IDs
- safe episode features or safe view references
- candidate family summaries or candidate scores for each episode
- diagnostic count-only summary
- separated synthetic expected-action labels
- split metadata if safe, or a simple train-only split note
- manifest-ready metadata such as schema versions and input source categories

Forbidden in input fixtures:

- raw learner text
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future action fields
- future episode fields in current-row input
- real participant ID
- private/manual/real-data path
- expected action inside safe episode or feature-like input files
- expected action as scorer, ranker, or candidate-generation feedback

The minimal case should test exporter plumbing and safety boundaries, not
realistic learner behavior.

## 7. Expected Output Contract

The first implementation should not store full expected output bodies.

Future `expected_output_contract.json` may contain safe metadata such as:

- expected feature row count
- expected label row count
- expected manifest schema version
- expected feature schema version
- expected label schema version
- expected split counts
- expected audit status
- expected reason code absence
- `no_raw_rows`
- `content_suppressed`
- `synthetic_only`
- expected output file presence

Forbidden in the expected output contract:

- full `features.jsonl` body
- full `labels.jsonl` body
- manifest body dump
- raw learner text
- label body
- expected action body
- candidate score rows
- private paths
- real participant data

The contract should let tests assert exporter behavior without turning the
fixture into a copied output dump.

## 8. Relation To Audit Fixtures

Existing audit fixture root:

`tests/fixtures/learner_state_sequence_audit/`

Purpose:

- provides direct inputs to the audit module
- includes valid and invalid feature/label/manifest fixtures
- verifies expected failures and safe audit reason codes

Future exporter input fixture root:

`tests/fixtures/learner_state_sequence_exporter/`

Purpose:

- provides upstream synthetic inputs for the exporter
- lets the exporter generate feature, label, and manifest outputs
- expects generated outputs to be checked by `learner_state.sequence_audit`

These fixture families should not be mixed. Audit fixtures test the audit
module directly. Exporter input fixtures test whether the exporter can produce
auditable outputs from safe upstream synthetic inputs.

## 9. No-Oracle / Leakage Checks Before Implementation

Before creating exporter input fixtures, review each fixture for:

- no forbidden fields
- expected action separated from feature-like inputs
- no expected action in candidate scoring input
- no future leakage
- no future-window aggregates
- no split leakage
- no label-derived split assignment
- synthetic-only paths
- safe synthetic join keys
- no real participant IDs
- no raw body in docs
- no private paths

The future exporter should fail closed if input files contain fields that look
like labels, future data, raw text, private paths, or real participant data.

## 10. First Fixture Priority

Initial fixture recommendation:

`valid/minimal_single_participant`

Shape:

- one synthetic participant
- one session
- one task
- two or three ordered episodes
- safe episode records
- candidate score summaries available
- diagnostic count-only summary available
- synthetic expected-action labels separated
- split metadata omitted or train-only
- expected output contract with counts and audit status only

Rationale:

- keeps the first exporter implementation small
- exercises ordering without needing complex split logic
- verifies label separation early
- produces enough rows to test past-only window behavior later
- avoids conflating exporter implementation with estimator or metric work

Invalid fixtures should wait until the valid path can produce auditable outputs,
except for a small missing-input case if needed to test fail-closed behavior.

## 11. Module / CLI Future Connection

Future module and CLI candidates:

- module: `python/learner_state/sequence_exporter.py`
- CLI: `python -m learner_state.sequence_exporter`
- input mode: `--input-fixture <case_dir>`
- output mode: explicit output directory, or temporary directory for smoke tests
- audit option: run learner-state sequence audit after export by default
- summary: safe count-only stdout

Future CLI behavior should:

- read fixture inputs without printing bodies
- write generated outputs only to explicit safe output paths
- run audit on generated output
- exit nonzero if export or audit fails
- avoid raw row output on errors

This step does not implement the module, CLI, output directory behavior, or
tests.

## 12. Output / Logging Safety

Safety rules:

- no raw fixture body in docs
- no raw output rows in stdout
- no generated `features.jsonl` body in docs
- no generated `labels.jsonl` body in docs
- no generated manifest body in docs
- no candidate score row dumps
- no expected action body
- no private paths
- no raw GitHub Actions logs
- public result summaries are count-only
- test failures should report safe case names and reason codes only

Generated outputs should not be committed from `tmp/`, `manual_outputs/`, or
private/local paths.

## 13. Future Roadmap

Recommended next steps:

1. Step 177: create initial exporter input fixture files.
2. Step 178: implement minimal synthetic sequence exporter.
3. Step 179: add exporter audit integration tests.
4. Step 180: design or implement a Makefile target after tests are stable.
5. Step 181: review release-quality integration after the Makefile target is
   stable.

Possible adjustment: add malformed/empty/unknown-version audit fixtures before
exporter implementation if fail-closed coverage needs to be broadened first.

Step 177 implementation note: the initial synthetic exporter input fixture root
now exists at
[`tests/fixtures/learner_state_sequence_exporter/`](../tests/fixtures/learner_state_sequence_exporter/README.md).
The first case is `valid/minimal_single_participant/` and contains separated
safe episode inputs, candidate summaries, diagnostic counts, synthetic
evaluation labels, grouping metadata, split metadata, and a safe expected output
contract. Public docs still do not copy fixture row bodies.

Step 178 implementation note: the minimal exporter module now consumes this
fixture and writes generated sequence outputs only to a caller-provided output
directory, such as a test temporary directory. The generated files are audited
by `learner_state.sequence_audit`, and tests compare safe contract metadata
rather than full generated JSONL bodies.

Step 179 follow-up: see
[Learner-state sequence exporter edge fixture design](learner_state_sequence_exporter_edge_fixture_design.md)
for future exporter-specific valid/invalid fixtures, safe failure reason codes,
and test expansion guidance. That follow-up is docs-only and does not create
additional fixture files.

Step 180 follow-up: the exporter fixture root now also contains initial
synthetic edge-case fixtures for future fail-closed exporter tests. Public docs
continue to describe only fixture categories and safe contracts, not JSONL row
bodies or malformed-line contents.

## 14. Beginner Notes

An input fixture is a small synthetic test case that a future exporter can read.
It helps prove that the exporter understands the input contract before larger
data generation exists.

Exporter input fixtures are different from audit fixtures. Audit fixtures are
already shaped like exported feature/label/manifest files. Exporter input
fixtures are upstream ingredients that the exporter turns into those files.

An expected output contract is a safe checklist of what the exporter should
produce. It records counts, versions, and audit status without copying the full
generated output.

Full expected output bodies are avoided at first because they make public docs
and tests more likely to expose row bodies, labels, or generated content.

Labels are separated because labels are answers for evaluation. If labels appear
in features, a future model could learn the answer directly.

## 15. Related Documents

- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Learner-state sequence exporter edge fixture design](learner_state_sequence_exporter_edge_fixture_design.md)
- [Milestone 06 learner-state audit infrastructure recap](milestone_06_learner_state_audit_infrastructure_recap.md)
- [Public release checklist](public_release_checklist.md)
