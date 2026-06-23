# Frozen Policy Generation Artifact Policy Design

This document defines the artifact policy for future frozen policy generation
work.

It is a docs-only design. It does not implement a generator, does not implement
an artifact writer, does not generate an artifact body, does not compute
metrics, does not evaluate performance, and does not claim real-data readiness.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected scaffold result bodies, generated frozen policy
artifact bodies, frozen policy artifact bodies, JSON bodies, policy bodies, raw
rows, logits/probability dumps, label bodies, split bodies, calibration policy
bodies, private paths, raw learner text, manual output bodies, tmp output
bodies, or real participant data.

## 1. Document Purpose

The purpose of this document is to define how future frozen policy generation
will treat artifacts before generator scaffold design begins.

The policy fixes the boundary for artifact metadata, artifact bodies, file
writing, safe reporting, no-oracle constraints, synthetic-only use, validation,
and release-quality staging.

This is not implementation. It is not generator behavior, not artifact writing,
not a policy body format, not a performance evaluation, and not a real-data
readiness claim.

## 2. Current State

Current state:

- runtime API skeleton exists
- runtime CLI exists
- runtime Makefile target exists
- release-quality includes runtime smoke
- remote/manual runtime status marker exists
- scaffold fixture validator exists
- runtime summary suppresses artifact bodies
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- generator is not implemented
- artifact writer is not implemented

The current runtime surface is metadata-only. It can report safe scaffold
status, reason codes, IDs, validation references, and safety flags. It does
not generate a frozen policy artifact body and does not write an artifact file.

## 3. Artifact Definitions

This policy distinguishes these terms:

- artifact metadata: safe identifiers, schema/version labels, validation
  references, status, reason codes, safety flags, and count-only summaries
- artifact body: the generated policy content or any full structured policy
  content that would be needed to use the policy
- artifact file: a persisted file containing an artifact body, artifact
  metadata, or both
- artifact manifest: metadata-only record describing what was planned,
  generated, validated, suppressed, or written
- artifact pointer: safe metadata that references an artifact location or
  identity without exposing private paths or artifact body content
- artifact validation summary: metadata-only validation result with status,
  reason codes, failed checks, safety flags, and count-only fields
- generated frozen policy: the future policy artifact that a generator may
  eventually create
- frozen policy generation result: the result object or summary produced by a
  future generator path
- runtime scaffold result: the current metadata-only runtime result returned
  by the scaffold runtime without generator or artifact writing

An artifact body is always higher risk than artifact metadata because it can
carry policy internals, raw-data-derived content, copied request content, or
future leakage. The default stance is suppression.

## 4. Initial Policy

Initial policy:

- initial generator scaffold should not generate artifact bodies
- initial generator scaffold should not write artifact files
- initial generator scaffold should return a metadata-only plan/result
- `generated_artifact_written=false` should remain true as a fact of the
  initial behavior
- `generated_artifact_body_available=false` should remain true as a fact of the
  initial behavior
- `artifact_body_suppressed=true` should remain true
- release-quality should not immediately include a body-producing generator
- body generation and file writing require separate milestones

This means the next generator scaffold can extend the runtime surface only if
it preserves metadata-only reporting and fail-closed safety behavior.

## 5. Allowed Metadata

Safe metadata may include:

- schema version
- request ID
- pointer ID
- policy ID
- artifact ID
- generator version
- validation reference IDs
- source fixture labels
- split policy label
- calibration policy label
- threshold policy label
- abstention policy label
- safety flags
- no-oracle flags
- synthetic-only flags
- artifact flags
- reason codes
- failed checks
- status
- count-only summaries

Allowed metadata must stay label-like, count-only, and body-free. It must not
echo private paths or raw content.

## 6. Forbidden Content

Forbidden content:

- raw learner text
- raw rows
- logits/probability dump
- generated policy body
- full policy JSON body
- generation request body
- input pointer body
- expected result body
- artifact body
- calibration body
- label body
- split body
- real participant data
- private paths
- final text
- observed-after text
- gold label
- expected action used as scoring feedback
- performance metric body
- raw logs

Future generator or artifact work must reject or suppress these fields before
summary, CLI, Makefile, release-quality, or status-marker output.

## 7. Artifact Body Suppression Policy

Artifact body suppression policy:

- docs must not paste artifact bodies
- CLI stdout/stderr must not print artifact bodies
- release-quality logs must not include artifact bodies
- status markers must not record artifact bodies
- tests should assert artifact body absence
- `generated_artifact_body_available=true` requires a separate design before it
  can appear
- `artifact_body_suppressed=true` remains the default and initial behavior

Body suppression applies even to synthetic fixtures. Synthetic-only status is
not a reason to expose policy bodies in public docs or release-quality logs.

## 8. Artifact File Writing Policy

Initial file-writing policy:

- no file writing
- no output path option
- no artifact output directory
- no policy JSON file
- no `manual_outputs`
- no tmp output for runtime/generator scaffold

Future file-writing policy:

- artifact writing must follow docs-only design, fixture design, tests,
  implementation, Makefile target, release-quality integration, and remote
  status-marker staging
- output paths must be controlled synthetic tmp paths only
- private paths must be rejected
- body content must not be committed
- manifests must be metadata-only
- generated artifacts must be excluded from public docs unless separately
  approved as safe metadata

Artifact file writing is a new surface. It should not be bundled into the
first generator scaffold skeleton.

## 9. No-Oracle Policy

No-oracle policy:

- do not use `observed_after_text`
- do not use `final_text`
- do not use `gold_label`
- do not use expected action as scoring feedback
- do not tune on the test split
- do not leak validation/test content into policy generation
- generate only from frozen validated metadata
- keep scoring feedback violations fail-closed

Validation split metadata may be recorded only when it is explicitly safe and
does not expose body content. Test split metadata must not drive tuning or
policy selection.

## 10. Synthetic-Only Policy

Synthetic-only policy:

- initial artifacts use synthetic fixtures only
- no real data
- no participant data
- no private data
- no real output directory
- all public artifacts are metadata-only
- real-data artifact generation requires future private/institution-approved
  review

Synthetic-only outputs are useful for safety and compatibility checks. They do
not establish production readiness or real-data readiness.

## 11. Validation Policy

Future generator scaffold validation should check:

- schema version
- required metadata fields
- forbidden fields
- no body leakage
- no raw rows
- no logits
- no private paths
- no performance claims
- no test tuning
- no scoring feedback
- artifact flags
- deterministic summary
- JSON serializable safe summary
- fail-closed invalid cases

Invalid cases should fail with stable reason codes. Valid cases should pass
without generating or exposing artifact bodies in the initial scaffold stage.

## 12. Release-Quality Policy

Release-quality policy:

- runtime smoke can stay in release-quality
- artifact body generation must not enter release-quality until body-safety
  tests exist
- file-writing generator behavior must not enter release-quality until
  tmp/output policy exists
- release-quality success is safety/smoke evidence, not performance evidence
- status markers must remain pass-only and count-only

The current release-quality runtime smoke should remain a metadata-only safe
entrypoint. Generator and artifact writing should be staged only after local
tests prove body suppression and output-path safety.

## 13. Future Artifact Lifecycle

Docs-only lifecycle:

- artifact policy design
- generator scaffold design
- artifact fixture design
- generator scaffold implementation
- artifact validation implementation
- generator CLI extension design
- generator CLI tests
- Makefile target design and implementation
- release-quality integration design and implementation
- remote status marker

Each stage should preserve metadata-only public reporting until a later,
separately reviewed body-generation policy exists.

## 14. What Is Safe To Commit

Safe to commit:

- docs
- metadata-only fixtures
- expected safe summaries
- reason-code fixtures
- count-only summaries

Unsafe to commit:

- artifact body
- generated policy body
- raw data
- learner text
- private paths
- real participant data
- logits
- full calibration bodies
- full policy bodies

Generated outputs under tmp or manual output locations must not be added to
Git.

## 15. Relation To Current Runtime Infrastructure

The current runtime infrastructure enforces a metadata-only surface. Future
generator work should extend that surface without weakening suppression.

Artifact policy is a precondition for generator scaffold work because the
generator boundary must know whether it may produce a body, write a file, or
report only metadata.

The scaffold fixture validator and runtime compatibility tests should remain
the oracle for expected safe behavior. Release-quality should continue to use
safe smoke checks only until generator and artifact safety tests are mature.

## 16. What This Does NOT Do

This document does not:

- implement a generator
- write artifacts
- create artifact fixtures
- change the CLI
- change the Makefile
- change release-quality
- change workflows
- change Python code
- change tests
- change fixtures
- compute metrics
- evaluate performance
- use real data
- prove generation quality

## 17. Beginner-Friendly Explanation

An artifact is something a generator might eventually produce. In this project,
that could someday mean a frozen policy plus safe metadata around it.

Metadata is the safe label around an artifact: IDs, schema versions, statuses,
reason codes, and safety flags. The body is the actual policy content. Bodies
are riskier because they can accidentally contain private content, raw data,
or future-derived information.

The first generator scaffold should not create a body because the project is
still proving the boundary. It is safer to make sure the command can plan,
validate, summarize, and fail closed before it can produce a policy body.

File writing is also a separate milestone because output paths, cleanup, tmp
policy, Git hygiene, and body suppression all need their own tests.

Release-quality should not immediately run body-producing generation because a
release-quality pass would otherwise be easy to misread as generation quality
or performance evidence. At this stage, it should remain safety/smoke evidence
only.

## 18. Next Recommended Steps

Recommended sequence:

- generator scaffold design
- generator fixture design
- generator scaffold skeleton
- artifact validation design

The next step can be generator scaffold design because this artifact policy now
sets the initial no-body and no-file-writing boundary. Artifact fixture design
should follow before any generator implementation that changes observable
results.

Step277 adds that next design at
[Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md).
It keeps generator implementation, artifact body generation, artifact file
writing, metrics, real-data use, and release-quality generator integration out
of scope.

Step278 adds the metadata-only fixture design at
[Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md).
It keeps fixture creation, generator implementation, artifact body generation,
artifact file writing, metrics, real-data use, and release-quality generator
integration out of scope.

Step279 creates the corresponding metadata-only fixture root at
`tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.
The fixture root keeps artifact body generation, generated policy bodies,
artifact file writing, metrics, real-data use, and generator implementation out
of scope.

## Related Documents

- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
- [Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
- [Public release checklist](public_release_checklist.md)
