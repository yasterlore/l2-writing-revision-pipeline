# kslog_cli Explained

## 1. Beginner Summary

`kslog_cli` is a small command-line tool for running the Rust pipeline on synthetic raw event JSONL files.

It helps check that validation, replay, extraction, micro-episode construction, no-oracle audit, and safe-view creation work from one entry point.

## 2. What This Component Does

This component:

- validates synthetic JSONL
- replays validated events
- extracts revision-event summaries
- builds micro-episode summaries
- runs no-oracle audit summaries
- creates safe-view summaries
- exports no-oracle safe-view JSONL for synthetic downstream prototypes

## 3. What This Component Does Not Do

This component does not:

- implement a browser logger
- run Python candidate generation
- run OT scoring
- estimate learner state
- process real participant data
- export full `MicroEpisode` artifacts
- decide whether observed edit text is safe for every prediction target

## 4. Input and Output

Input is a synthetic raw event JSONL file.

Most commands output a text summary printed to stdout. `export-safe-view` writes JSONL to the requested output path and prints a short summary.

The CLI avoids printing final replay text and local contexts by default.

## 5. Step-by-Step Mechanism

1. Read command-line arguments.
2. Read the input JSONL file.
3. Run validation.
4. Parse valid JSONL lines into `RawEvent`.
5. Run the selected command.
6. Print a short summary.
7. Return a non-zero exit code on error.

## 6. Important Data Structures

The CLI calls into existing Rust crate types:

- `ValidationReport`
- `ReplayReport`
- `RevisionExtractionReport`
- `MicroEpisodeConstructionReport`
- `NoOracleAuditReport`
- `NoOracleSafeEpisodeView`

## 7. Theory Behind the Implementation

The CLI is an orchestration layer. It does not reinterpret the data; it calls the deterministic Rust layers in order.

This keeps command-line behavior aligned with library behavior.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used.

## 9. Weighting Rationale, If Weights Are Used

No weights are used.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used.

## 11. Why This Design Was Selected Over Alternatives

The first version uses `std::env::args` instead of adding a CLI dependency. This keeps dependencies minimal while the command surface is still small.

The command logic lives in `lib.rs` so it can be tested without spawning subprocesses.

Safe-view export is implemented in the CLI rather than Python so the deterministic Rust layers can validate, replay, construct micro-episodes, and audit no-oracle safety before any modeling prototype reads the data.

## 12. Security and Privacy Considerations

Tests use only synthetic fixtures.

The CLI does not touch `private_data/`, `real_data/`, or `participant_data/`.

The CLI avoids printing final replay text and local contexts because those can contain writing fragments.

Do not save CLI output derived from real participant data into this repository.

`export-safe-view` excludes `local_context_after_observed` and no-oracle forbidden fields. It excludes observed edit text by default. If `--include-observed-edit-text` is used, the resulting JSONL may leak the prediction target depending on the task definition.

## 13. Tests Added

The tests cover:

- validation success
- validation failure
- replay summary without final text
- revision-event summary
- micro-episode summary
- no-oracle audit command
- safe-view command excluding `local_context_after_observed`
- safe-view JSONL export parsing
- default observed edit text exclusion
- forbidden field exclusion in export
- argument-missing behavior without panic

## 14. Known Limitations

The CLI exports safe-view JSONL only. It does not export full micro-episodes and does not implement Python candidate generation.

Argument parsing is intentionally simple. If command options grow, a CLI parser such as `clap` may be useful.

## 15. What To Read Next

- `crates/kslog_validate/README.md`
- `crates/kslog_replay/README.md`
- `crates/kslog_extract/README.md`
- `crates/kslog_micro_episode/README.md`
- `crates/kslog_no_oracle_audit/README.md`
