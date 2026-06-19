# Revision Event Spec

This file defines the documentation home for revision-event extraction.

No extraction logic is implemented yet.

## Planned Responsibility

Revision events will represent meaningful changes derived from replayed text states.

## Forbidden Location

Revision-event extraction must not be implemented in the TypeScript logger.

## Planned Concerns

- insertion, deletion, replacement, and movement categories
- span offsets and text-state references
- timestamp boundaries
- validation invariants
- synthetic fixtures
