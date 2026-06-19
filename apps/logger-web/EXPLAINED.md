# logger-web Explained

## 1. Beginner Summary

`logger-web` is a tiny browser page with a textarea. As a user types, it records raw browser events into JSONL.

It is an observation tool, not an analysis tool.

## 2. What This Component Does

This component:

- displays one textarea
- records browser events in memory
- adds synthetic session/task metadata
- builds RawEvent-like JSON objects
- lets the user download JSONL
- shows event count and last event type

## 3. What This Component Does Not Do

This component does not:

- validate JSONL
- replay text
- extract revision events
- construct micro-episodes
- run no-oracle audit
- generate candidates
- rank candidates
- send data to a server
- store data in `localStorage`

## 4. Input and Output

Input is synthetic manual typing in the textarea.

Output is downloaded JSONL, with one raw event object per line.

## 5. Step-by-Step Mechanism

1. The browser loads the page.
2. The app initializes synthetic metadata.
3. A user types synthetic text in the textarea.
4. Browser events such as `keydown`, `beforeinput`, `input`, and `compositionend` are observed.
5. The app snapshots textarea state before and after events when possible.
6. For `beforeinput` followed by `input`, the app keeps the `beforeinput` snapshot so deletion events are not accidentally based on a later `selectionchange`.
7. The app builds RawEvent-like objects.
8. The app stores those objects in memory.
9. The user downloads JSONL.
10. Rust tools validate and process the JSONL later.

## 6. Important Data Structures

`RawEvent` is the TypeScript interface matching the Rust-side schema shape.

`TextSnapshot` stores textarea text and selection positions at a moment in time.

`SyntheticMetadata` stores fixed synthetic identifiers.

## 7. Theory Behind the Implementation

The browser logger should only observe. Interpretation belongs to Rust.

This keeps browser code simple and avoids mixing data collection with analysis.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used.

## 9. Weighting Rationale, If Weights Are Used

No weights are used.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used.

## 11. Why This Design Was Selected Over Alternatives

The first version uses plain TypeScript and Vite instead of React because the UI is small and the main goal is event observation.

Events are stored in memory rather than `localStorage` to avoid accidental long-term storage of writing data.

The app downloads JSONL rather than sending it over the network because no backend is implemented yet.

## 12. Security and Privacy Considerations

Use synthetic data only.

The app does not send data over the network, does not use `localStorage`, and does not log text content to the console.

It avoids `innerHTML`, `eval`, and the `Function` constructor.

Downloaded JSONL can contain text fragments. Do not commit downloaded JSONL from real sessions.

## 13. Tests Added

The tests check:

- RawEvent builder creates required fields
- inserted text inference
- deleted text inference
- forbidden fields such as `final_text`, `observed_after_text`, and `gold_label` are not generated
- JSONL serialization shape

## 14. Known Limitations

The first version performs only limited inserted/deleted text inference. `deleteContentBackward` has a focused rule for collapsed-cursor and selected-range deletion, but broader browser editing behavior may still need synthetic E2E checks.

IME behavior is observed but not deeply interpreted.

The placeholder hashes are not cryptographic hashes. Rust replay currently skips `synthetic_hash_*` placeholders.

The logger uses `Date.now()` for timestamps.

## 15. What To Read Next

- `docs/02_system_architecture.md`
- `docs/04_raw_event_schema.md`
- `crates/kslog_schema/README.md`
- `crates/kslog_validate/README.md`
