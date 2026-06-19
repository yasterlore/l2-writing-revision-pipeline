# kslog_validate Explained

## 1. Beginner Summary

`kslog_validate` checks whether a raw keystroke event JSONL file is safe and well-formed enough for later pipeline stages.

It does not understand the whole writing process yet. It only checks basic structure, ordering, ranges, and no-oracle field policy.

## 2. What This Component Does

This component:

- reads JSONL one line at a time
- rejects malformed JSON
- rejects empty lines by default
- rejects lines that are too large
- deserializes each line as `RawEvent`
- checks consecutive `seq`
- checks monotonic non-decreasing `timestamp_ms`
- checks cursor bounds
- checks selection bounds
- rejects no-oracle forbidden fields

## 3. What This Component Does Not Do

This component does not:

- implement a browser logger
- replay text
- reconstruct final document states
- extract revision events
- construct micro-episodes
- run the full no-oracle audit
- perform candidate generation
- perform ranking or OT scoring
- estimate learner state
- process real participant data

## 4. Input and Output

Input is synthetic JSONL, where each non-empty line should be one JSON object representing a `RawEvent`.

Output is either:

- `ValidationReport`, if all lines pass
- `ValidationError`, if validation fails

`ValidationError` includes a line number when possible.

## 5. Step-by-Step Mechanism

1. Read one line from the JSONL stream.
2. Check that the line does not exceed `max_line_bytes`.
3. Reject empty lines by default.
4. Parse the line as JSON.
5. Check that the JSON value is an object.
6. Reject no-oracle forbidden fields.
7. Deserialize the object as `RawEvent`.
8. Check `seq` continuity.
9. Check timestamp monotonicity.
10. Check cursor bounds.
11. Check selection bounds.
12. Update the validation report.

## 6. Important Data Structures

`ValidationOptions` controls validator behavior, including maximum line size and empty-line policy.

`ValidationReport` summarizes a successful validation run.

`ValidationError` reports failure with an optional line number.

`ValidationErrorKind` describes the reason for failure.

## 7. Theory Behind the Implementation

The validator follows a staged safety model. It first checks that each line is syntactically parseable, then checks that it matches the schema, and then applies simple deterministic cross-field checks.

This keeps the raw schema separate from validation logic while still blocking unsafe or inconsistent input before later transformations.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

## 9. Weighting Rationale, If Weights Are Used

No weights are used in this component.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

The validator is implemented in Rust because Rust is the authoritative deterministic layer for validation and transformation.

It returns `Result` instead of panicking so malformed input can be handled safely.

It validates line by line so future tools can process JSONL streams without loading entire datasets into memory.

It avoids text replay so the validation boundary stays narrow and testable.

## 12. Security and Privacy Considerations

The tests use only synthetic fixtures.

The validator rejects malformed JSONL without panicking. It also rejects lines larger than a configured limit.

The validator rejects no-oracle forbidden fields such as:

- `final_text`
- `observed_after_text`
- `gold_label`

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- `valid/simple_typing.jsonl`
- all valid raw event fixtures
- malformed JSON
- missing required fields
- forbidden no-oracle fields
- `seq` gaps
- timestamp inversion
- cursor out of bounds
- inverted selection ranges
- empty-line rejection
- line-size rejection

## 14. Known Limitations

This crate does not verify whether `inserted_text`, `deleted_text`, and document lengths reconstruct a valid text trajectory.

It does not validate all possible browser event semantics.

It stops at the first validation error rather than collecting all errors.

## 15. What To Read Next

- `crates/kslog_schema/README.md`
- `docs/04_raw_event_schema.md`
- `docs/10_data_quality_policy.md`
- `docs/05_text_replay_spec.md`
- `docs/03_no_oracle_policy.md`

