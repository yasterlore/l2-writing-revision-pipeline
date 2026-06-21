# Release-Quality Manual Workflow Remote-Run Report Template

Template status:

- blank template
- not an actual remote run report
- do not paste raw logs
- do not paste workflow logs
- no performance claim
- no real data
- no expected-action scoring feedback

Use this template only after a manual GitHub Actions remote run of the
release-quality workflow. Keep the report safe, high-level, and count/status
oriented.

## 1. Run Metadata

- Date:
- Reviewer:
- GitHub workflow name:
- Branch:
- Commit SHA:
- Run URL:
- Run attempt number:
- Result: pass / fail / cancelled
- Duration: approximate only

## 2. Trigger Confirmation

- [ ] `workflow_dispatch` only
- [ ] Branch selected
- [ ] No `pull_request` trigger
- [ ] No `push` trigger
- [ ] No `schedule` trigger
- [ ] No artifact upload

Notes:

-

## 3. Setup Stage Checklist

- [ ] Checkout completed
- [ ] Python setup completed
- [ ] Rust setup completed
- [ ] Node setup completed
- [ ] `npm ci` completed
- [ ] Wrapper executable confirmed
- [ ] Repository root execution confirmed

Notes:

-

## 4. Wrapper Execution Checklist

- [ ] `scripts/check_release_quality.sh` started
- [ ] Summary generation completed
- [ ] Manifest sync completed
- [ ] Diagnostic distribution completed
- [ ] Python checks completed
- [ ] Rust checks completed
- [ ] logger-web checks completed
- [ ] Synthetic policy completed
- [ ] Conflict marker grep completed

Notes:

-

## 5. Safe Logs Checklist

- [ ] No raw JSONL body
- [ ] No summary body
- [ ] No marker body
- [ ] No diagnostic body
- [ ] No config body
- [ ] No candidate score rows
- [ ] No raw text
- [ ] No artifact upload
- [ ] Logs are safe status/path/count/reason only

Notes:

-

## 6. Failure Summary

Leave this section blank for a successful run unless a non-blocking issue needs
safe follow-up.

- Failing stage:
- Safe reason:
- Local reproduction command:
- Suspected category: setup / dependency / wrapper / manifest sync / diagnostic
  distribution / logger-web / Rust / Python / synthetic policy / output safety /
  unknown
- No raw logs pasted: yes / no

Notes:

-

## 7. Decision

Select one:

- [ ] Usable as manual release-quality workflow
- [ ] Revise workflow setup
- [ ] Revise wrapper
- [ ] Investigate environment difference
- [ ] Stop and fix output safety
- [ ] Defer

Decision note:

-

## 8. Follow-Up Actions

- Issue/PR link, if any:
- Local command to rerun:
- Docs to update:
- Next step:
- GitHub Actions warning follow-up, if any:
- Node runtime warning status: removed / reduced / unchanged / changed / not
  checked

Notes:

-

## 9. Do Not Include

Do not include:

- raw workflow logs
- raw JSONL body
- summary CSV body
- manifest JSON body
- diagnostic summary body
- config body
- candidate score rows
- raw learner text
- expected action details
- performance metrics
- real participant data
- private/manual/real paths

## 10. Beginner Notes

A remote run report is a safe summary of a GitHub Actions run.

It is not a place to paste raw logs. In many cases, the failed stage and a safe
reason are enough to decide the next step.

It is not a performance evaluation. It does not measure model quality, scoring
quality, calibration, or learner state.

Keep public records high-level so the repository history remains safe to share.

## 11. Related Documents

- [Release-quality manual workflow remote-run checklist](../release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow design](../release_quality_manual_workflow_design.md)
- [GitHub Actions Node deprecation warning handling design](../actions_node_deprecation_warning_handling_design.md)
- [Release-quality action version update plan](../release_quality_action_version_update_plan.md)
- [Public release checklist](../public_release_checklist.md)
