# Frozen Policy Generation Generator Scaffold Fixtures

This fixture root contains metadata-only synthetic fixtures for the future
frozen policy generation generator scaffold.

These files are fixture contracts only. They do not implement a generator, do
not validate fixtures, do not generate artifact bodies, and do not write
artifact files.

Safety boundary:

- generator implementation is not included
- artifact body content is not included
- generated policy body content is not included
- artifact file writing is not included
- raw rows are not included
- logits or probability dumps are not included
- private paths are not included
- raw learner text is not included
- real participant data is not included

Valid cases are metadata-only cases that a future scaffold should pass.
Invalid cases are fail-closed marker cases for reason-code alignment. Invalid
cases may use safe marker labels and reason codes, but they do not include
actual payload bodies.

Each case contains:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generator_scaffold_result.json`

Expected results are safe metadata-only summaries. They keep
`generated_artifact_written=false`, `generated_artifact_body_available=false`,
`artifact_body_suppressed=true`, and `artifact_file_path_available=false`.

This root is synthetic-only and no-oracle. It is not performance evidence, not
generator quality evidence, not artifact generation evidence, and not
real-data readiness evidence.
