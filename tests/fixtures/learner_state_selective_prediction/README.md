# Learner-State Selective Prediction Fixtures

These fixtures are synthetic-only inputs for future calibration and selective
prediction validation.

They test prediction rows, label rows, split metadata, calibration policy
metadata, and expected validation results. Prediction rows and label rows are
kept separate so expected actions remain label-side only, except for
intentional invalid fixtures that test leakage detection.

Validation split examples are for future temperature and threshold selection.
Test split examples are for final evaluation after policy freeze. Test tuning
is represented only as an invalid fixture target.

Expected validation result files are count/reason-code contracts only. They
are not metric reports and not performance evidence.

Do not paste fixture row bodies into public docs. The fixtures contain no real
participant data, no raw learner text, and no private paths.
