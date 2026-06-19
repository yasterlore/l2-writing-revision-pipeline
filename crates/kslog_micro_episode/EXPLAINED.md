# kslog_micro_episode Explained

## 1. Beginner Summary

`kslog_micro_episode` takes an observed edit and wraps it with a small amount of nearby text context.

The result is called a `MicroEpisode`. It is a compact unit that later modeling code can inspect.

## 2. What This Component Does

This component:

- runs revision-event extraction
- walks through the observed edits in order
- keeps a local replay state
- captures pre-edit local context
- applies the observed edit
- captures observed post-edit local context
- builds a deterministic `MicroEpisode`

## 3. What This Component Does Not Do

This component does not:

- implement a browser logger
- run a no-oracle audit
- generate candidates
- rank candidates
- perform OT scoring
- estimate learner state
- use gold labels
- use final corrected text
- decide whether an edit is correct

## 4. Input and Output

Input is a slice of `RawEvent` values.

Output is a `MicroEpisodeConstructionReport`, which contains `MicroEpisode` records and summary counts.

Each `MicroEpisode` includes identifiers, revision kind, local contexts, span, inserted/deleted text, cursor positions, document lengths, and quality flags.

## 5. Step-by-Step Mechanism

1. Extract `RevisionEvent` values from the raw events.
2. Start with an empty local document state.
3. For each revision event, identify the edit anchor.
4. Capture `local_context_before` around the anchor.
5. Apply the observed edit to the local state.
6. Capture `local_context_after_observed` around the post-edit anchor.
7. Build a deterministic `micro_episode_id`.
8. Store the episode unless options say to skip it.

## 6. Important Data Structures

`MicroEpisode` is the main analysis unit.

`MicroEpisodeContext` stores a local text window, anchor, window start, window end, and window size.

`MicroEpisodeTarget` stores the edit span and inserted/deleted text fragments.

`MicroEpisodeOptions` controls context window size and whether non-revision-like or unsupported events are included.

`MicroEpisodeConstructionReport` stores all constructed episodes.

## 7. Theory Behind the Implementation

Micro-episodes represent local observed writing-process evidence. They are useful because many revisions are best interpreted near the text that surrounds them.

The component separates observed local context from later interpretation. It does not infer intent, correctness, or learner state.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

The local context uses a fixed window size `N = 30` characters by default. This is not a learned mathematical weight; it is an initial engineering choice that can be changed and evaluated later.

## 9. Weighting Rationale, If Weights Are Used

No learned weights are used.

The value `N = 30` is a fixed context-window size, not a model weight. It is large enough for small synthetic examples and small enough to avoid collecting unnecessary context in early tests.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

A char-window design is simple, deterministic, and easy to test.

Token-based or sentence-based context may be better later, but those choices require additional segmentation policy. The first version avoids that complexity.

Normal typing is included by default with `is_revision_like = false`, so downstream components can decide whether to filter it.

## 12. Security and Privacy Considerations

Tests use only synthetic fixtures.

The crate does not read `private_data/`, `real_data/`, or `participant_data/`.

It does not include `final_text`, `observed_after_text`, `gold_label`, teacher corrections, or human corrections.

`local_context_after_observed` is no-oracle unsafe for candidate generation and ranking because it contains observed post-edit context.

`inserted_text`, `deleted_text`, and local contexts may contain text fragments. Do not commit micro-episode output derived from real participant data.

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- deletion fixture micro-episodes
- replacement fixture micro-episodes
- selection edit fixture micro-episodes
- paste fixture micro-episodes
- simple typing as non-revision-like insertion episodes
- optional skipping of non-revision-like insertions
- deterministic micro-episode IDs
- expected local context window behavior
- retained `local_context_after_observed`
- replay-impossible input returning an error
- malformed JSON parse failure without panic

## 14. Known Limitations

The context window uses Rust `char` count, not grapheme clusters. Emoji and combining marks may need grapheme-aware handling later.

The first version uses a fixed char window. Future versions may use token-based, sentence-based, or discourse-aware context.

`local_context_after_observed` is retained for evaluation and reconstruction checks, but it must be filtered out before no-oracle candidate generation or ranking.

## 15. What To Read Next

- `crates/kslog_extract/README.md`
- `docs/07_micro_episode_spec.md`
- `docs/03_no_oracle_policy.md`
- `docs/08_candidate_generation_spec.md`
- `docs/09_ot_scoring_spec.md`

