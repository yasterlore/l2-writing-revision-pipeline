# Data Quality Policy

Data quality checks must begin with synthetic data.

## Raw Input Quality

Raw JSONL input must be treated as untrusted. Future validators should check:

- parse failures
- missing required fields
- unknown fields where disallowed
- timestamp monotonicity where required
- impossible cursor or text states
- oversized payloads
- invalid encodings
- adversarial structures

The first Rust validator lives in `crates/kslog_validate/`. It currently checks:

- one JSON object per JSONL line
- malformed JSON
- empty-line rejection by default
- maximum line size
- `kslog_schema::RawEvent` deserialization
- no-oracle forbidden fields
- consecutive `seq`
- monotonic non-decreasing `timestamp_ms`
- cursor positions against corresponding document lengths
- selection range ordering and bounds

It intentionally does not replay text or validate the semantic consistency of `inserted_text`, `deleted_text`, and `diff_op`.

The first Rust replay layer lives in `crates/kslog_replay/`. It checks replay-specific consistency after JSONL validation:

- `doc_len_before` against current replayed character count
- `doc_len_after` against updated replayed character count
- cursor and selection bounds used by replay
- selected text against `deleted_text` when present
- non-placeholder replay hash labels when present

Replay output may contain reconstructed writing. Do not commit replay output derived from real participant data.

The first revision-event extraction layer lives in `crates/kslog_extract/`. It converts validated and replayable raw events into observed edit records:

- insertion
- deletion
- replacement
- selection range edit
- paste
- composition commit
- unsupported observed event

These records are observations, not correctness labels. Extraction must not use final corrected text, gold labels, teacher corrections, or post-hoc annotations.

The first micro-episode construction layer lives in `crates/kslog_micro_episode/`. It packages extracted revision events with local context:

- pre-edit `local_context_before`
- observed post-edit `local_context_after_observed`
- edit span and text fragments
- cursor and document length metadata

`local_context_after_observed` is retained for reconstruction checks and evaluation, but it is no-oracle unsafe for candidate generation and ranking. Micro-episode outputs may contain writing fragments and must not be committed when derived from real participant data.

The first no-oracle audit layer lives in `crates/kslog_no_oracle_audit/`. It checks use-context-specific risks before candidate generation, ranking, OT scoring, or learner-state estimation.

Current audit checks include:

- forbidden field names such as `final_text`, `observed_after_text`, and `gold_label`
- observed post-edit context used in candidate generation or ranking contexts
- core Rust pipeline field-name collisions with the forbidden list

Audit reports derived from real participant data must not be committed to this repository.

## Derived Data Quality

Derived artifacts should document:

- source input hash or identifier
- validation status
- transformation version
- no-oracle audit status where applicable

## Testing

Malformed, adversarial, and invalid inputs should be covered when each implementation component is added.
