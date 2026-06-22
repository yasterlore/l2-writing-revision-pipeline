# Learner-State Estimator Input Fixtures

These fixtures are synthetic-only exported-shape inputs for a future
learner-state estimator input loader/validator.

They differ from exporter fixtures: exporter fixtures start from upstream
synthetic inputs and generate sequence outputs, while these fixtures begin at
the exported `features.jsonl` / `labels.jsonl` / `manifest.json` boundary.

The expected validation result files are count/reason-code contracts only.
They are not full output snapshots, and they are not performance evidence.

Do not paste fixture row bodies into public docs. The fixtures contain no real
participant data, no raw learner text, and no private paths.
