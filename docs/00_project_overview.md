# Project Overview

This project supports research on L2 English free-writing by building a reproducible pipeline for keystroke-level writing process data.

The long-term pipeline is:

1. Browser-side raw event collection.
2. Deterministic raw-event validation.
3. Text replay.
4. Revision-event extraction.
5. Micro-episode construction.
6. No-oracle candidate generation.
7. OT-inspired candidate ranking.
8. Evaluation.
9. Learner-state estimation.
10. Visualization and reporting.

Current repository status: structure and documentation foundations only. No logger or processing logic is implemented yet.

## Non-Negotiable Constraints

- Development and testing use synthetic data only.
- Real participant data must never be committed.
- Codex must not read, inspect, transform, summarize, or write real participant data.
- TypeScript is limited to browser-side raw event collection.
- Rust is authoritative for deterministic validation and transformation.
- Python is exploratory and analytical.
- No-oracle components must not use future edits, gold labels, final corrected text, teacher corrections, or post-hoc annotations.
