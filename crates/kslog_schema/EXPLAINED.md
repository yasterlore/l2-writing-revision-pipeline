# kslog_schema Explained

## 1. Beginner Summary

`kslog_schema` defines the Rust shape of one raw keystroke-log event. It answers the question: “What fields can one raw browser event row have?”

It does not decide whether the event is valid in a deeper research sense. That stricter validation belongs in later Rust crates.

## 2. What This Component Does

This component defines:

- `RawEvent`
- `EventType`
- `InputType`
- `DiffOp`

It also derives serde support so synthetic JSON can be converted into Rust types and Rust types can be converted back into JSON.

## 3. What This Component Does Not Do

This component does not:

- implement the web logger
- validate full JSONL files
- replay text
- extract revision events
- construct micro-episodes
- perform no-oracle audits
- generate candidates
- rank candidates
- estimate learner state
- process real participant data

## 4. Input and Output

Input is a synthetic JSON object representing one raw event.

Output is a Rust `RawEvent` value, or JSON generated from a Rust `RawEvent` value.

This crate treats optional event-dependent fields with `Option<T>` because many raw events do not have inserted text, deleted text, cursor positions, or composition identifiers.

## 5. Step-by-Step Mechanism

1. A JSON object contains raw event fields.
2. serde reads the JSON object.
3. serde maps string event names to enum variants such as `EventType::Input`.
4. Missing optional fields become `None`.
5. Missing `quality_flags` becomes an empty vector.
6. Unknown fields are rejected so forbidden no-oracle fields are not silently accepted.
7. Rust code receives a typed `RawEvent`.

## 6. Important Data Structures

`RawEvent` is the main structure. It stores identifiers, ordering fields, timestamp, event category, optional edit-related fields, text hashes, and quality flags.

`EventType` describes the browser or logger event category.

`InputType` represents selected browser `InputEvent.inputType` values, such as `insertText` and `deleteContentBackward`.

`DiffOp` is a coarse operation hint such as `insert`, `delete`, or `replace`. It is not a replay algorithm and not a revision-event extractor.

## 7. Theory Behind the Implementation

The design separates raw event representation from deterministic transformation. This helps keep the browser logger simple and moves authoritative interpretation into Rust.

The schema is intentionally event-level rather than essay-level. Later components can replay sequences, extract revision events, and construct micro-episodes without needing the logger to make those decisions.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

## 9. Weighting Rationale, If Weights Are Used

No weights are used in this component.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

The design uses a Rust struct instead of untyped JSON maps so downstream deterministic crates can rely on explicit fields and enum values.

It uses `Option<T>` instead of placeholder values because absent event data is different from empty event data.

It does not include validation-heavy rules because those belong in `kslog_validate`.

It uses serde `deny_unknown_fields` to avoid silently accepting forbidden no-oracle fields such as `final_text`, `observed_after_text`, and `gold_label`.

## 12. Security and Privacy Considerations

Only synthetic data is used in tests.

The schema must not include real names, email addresses, institution participant IDs, or real writing content.

`RawEvent` intentionally excludes:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections after writing

These exclusions support the project no-oracle policy.

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- deserializing valid synthetic JSON into `RawEvent`
- serializing `RawEvent` into JSON
- enum handling for `event_type`
- missing optional fields
- rejection of a forbidden unknown field such as `final_text`

## 14. Known Limitations

This is an initial schema. It may need additional event types, input types, quality flags, and metadata fields after synthetic logger prototypes are designed.

The crate does not validate cross-field consistency. For example, it does not check whether document lengths match inserted text lengths. That belongs in `kslog_validate`.

## 15. What To Read Next

- `docs/04_raw_event_schema.md`
- `docs/05_text_replay_spec.md`
- `docs/06_revision_event_spec.md`
- `docs/07_micro_episode_spec.md`
- `docs/03_no_oracle_policy.md`

