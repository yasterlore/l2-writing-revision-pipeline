//! No-oracle audit checks for writing-process pipeline artifacts.
//!
//! This crate does not generate candidates or rank anything. It only reports
//! fields and concepts that would leak future, gold, or post-hoc information
//! into no-oracle modeling contexts.

use kslog_extract::RevisionEvent;
use kslog_micro_episode::MicroEpisode;
use kslog_schema::RawEvent;

pub const FORBIDDEN_FIELD_NAMES: &[&str] = &[
    "final_text",
    "final_corrected_text",
    "observed_after_text",
    "gold_label",
    "teacher_correction",
    "teacher_corrections",
    "human_correction",
    "human_corrections",
    "post_hoc_annotation",
    "post_hoc_annotations",
    "target_label",
    "answer_key",
    "corrected_sentence",
    "future_edit",
    "future_context",
];

pub const RAW_EVENT_FIELD_NAMES: &[&str] = &[
    "logger_schema_version",
    "session_id",
    "participant_local_id",
    "task_id",
    "prompt_id",
    "seq",
    "timestamp_ms",
    "event_type",
    "input_type",
    "is_composing",
    "composition_id",
    "selection_start_before",
    "selection_end_before",
    "selection_start_after",
    "selection_end_after",
    "cursor_pos_before",
    "cursor_pos_after",
    "doc_len_before",
    "doc_len_after",
    "inserted_text",
    "deleted_text",
    "text_hash_before",
    "text_hash_after",
    "diff_op",
    "quality_flags",
];

pub const REVISION_EVENT_FIELD_NAMES: &[&str] = &[
    "revision_event_id",
    "session_id",
    "task_id",
    "prompt_id",
    "source_seq",
    "timestamp_ms",
    "kind",
    "span",
    "inserted_text",
    "deleted_text",
    "cursor_pos_before",
    "cursor_pos_after",
    "doc_len_before",
    "doc_len_after",
    "is_revision_like",
    "quality_flags",
];

pub const MICRO_EPISODE_FIELD_NAMES: &[&str] = &[
    "micro_episode_id",
    "session_id",
    "task_id",
    "prompt_id",
    "source_revision_event_id",
    "source_seq",
    "timestamp_ms",
    "revision_kind",
    "is_revision_like",
    "local_context_before",
    "local_context_after_observed",
    "target",
    "cursor_pos_before",
    "cursor_pos_after",
    "span_start",
    "span_end",
    "inserted_text",
    "deleted_text",
    "doc_len_before",
    "doc_len_after",
    "quality_flags",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NoOracleUseContext {
    ForArchival,
    ForReplayVerification,
    ForEvaluation,
    ForCandidateGeneration,
    ForRanking,
    ForOtScoring,
    ForLearnerStateEstimation,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum NoOracleRiskLevel {
    Info,
    Warning,
    Unsafe,
    Blocking,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NoOracleAuditIssue {
    pub risk_level: NoOracleRiskLevel,
    pub use_context: NoOracleUseContext,
    pub artifact_type: &'static str,
    pub artifact_id: Option<String>,
    pub field_name: Option<String>,
    pub message: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NoOracleAuditReport {
    pub use_context: NoOracleUseContext,
    pub checked_artifact_count: usize,
    pub issues: Vec<NoOracleAuditIssue>,
}

impl NoOracleAuditReport {
    pub fn new(use_context: NoOracleUseContext) -> Self {
        Self {
            use_context,
            checked_artifact_count: 0,
            issues: Vec::new(),
        }
    }

    pub fn has_unsafe_or_blocking_issues(&self) -> bool {
        self.issues.iter().any(|issue| {
            matches!(
                issue.risk_level,
                NoOracleRiskLevel::Unsafe | NoOracleRiskLevel::Blocking
            )
        })
    }

    pub fn highest_risk_level(&self) -> Option<NoOracleRiskLevel> {
        self.issues.iter().map(|issue| issue.risk_level).max()
    }

    fn push(&mut self, issue: NoOracleAuditIssue) {
        self.issues.push(issue);
    }
}

pub fn audit_raw_event(raw_event: &RawEvent) -> NoOracleAuditReport {
    let mut report = audit_field_names(
        RAW_EVENT_FIELD_NAMES,
        NoOracleUseContext::ForReplayVerification,
        "RawEvent",
        Some(format!("{}:{}", raw_event.session_id, raw_event.seq)),
    );
    report.checked_artifact_count = 1;
    report
}

pub fn audit_revision_event(revision_event: &RevisionEvent) -> NoOracleAuditReport {
    let mut report = audit_field_names(
        REVISION_EVENT_FIELD_NAMES,
        NoOracleUseContext::ForEvaluation,
        "RevisionEvent",
        Some(revision_event.revision_event_id.clone()),
    );
    report.checked_artifact_count = 1;
    report
}

pub fn audit_micro_episode(
    micro_episode: &MicroEpisode,
    use_context: NoOracleUseContext,
) -> NoOracleAuditReport {
    let mut report = audit_field_names(
        MICRO_EPISODE_FIELD_NAMES,
        use_context,
        "MicroEpisode",
        Some(micro_episode.micro_episode_id.clone()),
    );
    report.checked_artifact_count = 1;

    if is_no_oracle_modeling_context(use_context) {
        report.push(NoOracleAuditIssue {
            risk_level: NoOracleRiskLevel::Unsafe,
            use_context,
            artifact_type: "MicroEpisode",
            artifact_id: Some(micro_episode.micro_episode_id.clone()),
            field_name: Some("local_context_after_observed".to_string()),
            message: "observed post-edit context is no-oracle unsafe for candidate generation, ranking, OT scoring, or learner-state estimation".to_string(),
        });
    }

    report
}

pub fn audit_micro_episode_for_candidate_generation(
    micro_episode: &MicroEpisode,
) -> NoOracleAuditReport {
    audit_micro_episode(micro_episode, NoOracleUseContext::ForCandidateGeneration)
}

pub fn audit_micro_episodes(
    micro_episodes: &[MicroEpisode],
    use_context: NoOracleUseContext,
) -> NoOracleAuditReport {
    let mut report = NoOracleAuditReport::new(use_context);
    report.checked_artifact_count = micro_episodes.len();

    for micro_episode in micro_episodes {
        let episode_report = audit_micro_episode(micro_episode, use_context);
        report.issues.extend(episode_report.issues);
    }

    report
}

pub fn audit_metadata_field_names<'a, I>(
    field_names: I,
    use_context: NoOracleUseContext,
    artifact_type: &'static str,
    artifact_id: Option<String>,
) -> NoOracleAuditReport
where
    I: IntoIterator<Item = &'a str>,
{
    let fields = field_names.into_iter().collect::<Vec<_>>();
    audit_field_names(&fields, use_context, artifact_type, artifact_id)
}

pub fn audit_field_names(
    field_names: &[&str],
    use_context: NoOracleUseContext,
    artifact_type: &'static str,
    artifact_id: Option<String>,
) -> NoOracleAuditReport {
    let mut report = NoOracleAuditReport::new(use_context);
    report.checked_artifact_count = 1;

    for field_name in field_names {
        if is_forbidden_field_name(field_name) {
            report.push(NoOracleAuditIssue {
                risk_level: risk_level_for_forbidden_field(use_context),
                use_context,
                artifact_type,
                artifact_id: artifact_id.clone(),
                field_name: Some((*field_name).to_string()),
                message: format!(
                    "field `{field_name}` is forbidden by no-oracle policy in this pipeline"
                ),
            });
        }
    }

    report
}

pub fn is_forbidden_field_name(field_name: &str) -> bool {
    FORBIDDEN_FIELD_NAMES
        .iter()
        .any(|forbidden| forbidden.eq_ignore_ascii_case(field_name))
}

fn is_no_oracle_modeling_context(use_context: NoOracleUseContext) -> bool {
    matches!(
        use_context,
        NoOracleUseContext::ForCandidateGeneration
            | NoOracleUseContext::ForRanking
            | NoOracleUseContext::ForOtScoring
            | NoOracleUseContext::ForLearnerStateEstimation
    )
}

fn risk_level_for_forbidden_field(use_context: NoOracleUseContext) -> NoOracleRiskLevel {
    if is_no_oracle_modeling_context(use_context) {
        NoOracleRiskLevel::Blocking
    } else {
        NoOracleRiskLevel::Unsafe
    }
}

#[cfg(test)]
mod tests {
    use super::{
        audit_field_names, audit_metadata_field_names, audit_micro_episode,
        audit_micro_episode_for_candidate_generation, audit_micro_episodes, audit_raw_event,
        audit_revision_event, NoOracleRiskLevel, NoOracleUseContext, MICRO_EPISODE_FIELD_NAMES,
        RAW_EVENT_FIELD_NAMES, REVISION_EVENT_FIELD_NAMES,
    };
    use kslog_extract::extract_revision_events;
    use kslog_micro_episode::build_micro_episodes;
    use kslog_schema::RawEvent;
    use kslog_validate::{validate_jsonl_reader, ValidationOptions};
    use std::{
        fs,
        io::Cursor,
        path::{Path, PathBuf},
    };

    fn repository_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
    }

    fn fixture_path(relative_path: &str) -> PathBuf {
        repository_root().join(relative_path)
    }

    fn read_valid_fixture(relative_path: &str) -> Vec<RawEvent> {
        let path = fixture_path(relative_path);
        let content = fs::read_to_string(&path)
            .unwrap_or_else(|error| panic!("failed to read {}: {error}", path.display()));
        validate_jsonl_reader(Cursor::new(content.as_str()), &ValidationOptions::default())
            .unwrap_or_else(|error| panic!("{} failed validation: {error}", path.display()));
        content
            .lines()
            .filter(|line| !line.trim().is_empty())
            .map(|line| {
                serde_json::from_str::<RawEvent>(line)
                    .unwrap_or_else(|error| panic!("failed to parse {}: {error}", path.display()))
            })
            .collect()
    }

    #[test]
    fn valid_synthetic_micro_episode_is_allowed_for_evaluation() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");
        let report = build_micro_episodes(&events).expect("micro episodes build");
        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.is_revision_like)
            .expect("revision-like episode exists");

        let audit = audit_micro_episode(episode, NoOracleUseContext::ForEvaluation);

        assert!(!audit.has_unsafe_or_blocking_issues());
        assert!(audit.issues.is_empty());
    }

    #[test]
    fn candidate_generation_flags_after_observed_context() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");
        let report = build_micro_episodes(&events).expect("micro episodes build");
        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.is_revision_like)
            .expect("revision-like episode exists");

        let audit = audit_micro_episode_for_candidate_generation(episode);

        assert!(audit.has_unsafe_or_blocking_issues());
        assert!(audit.issues.iter().any(|issue| {
            issue.risk_level == NoOracleRiskLevel::Unsafe
                && issue.field_name.as_deref() == Some("local_context_after_observed")
        }));
    }

    #[test]
    fn ranking_flags_after_observed_context() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/paste_case.jsonl");
        let report = build_micro_episodes(&events).expect("micro episodes build");

        let audit = audit_micro_episodes(&report.episodes, NoOracleUseContext::ForRanking);

        assert!(audit.has_unsafe_or_blocking_issues());
        assert_eq!(audit.checked_artifact_count, report.episodes.len());
    }

    #[test]
    fn forbidden_metadata_final_text_is_detected() {
        let audit = audit_metadata_field_names(
            ["synthetic_id", "final_text"],
            NoOracleUseContext::ForCandidateGeneration,
            "SyntheticMetadata",
            Some("synthetic_metadata_001".to_string()),
        );

        assert!(audit.issues.iter().any(|issue| {
            issue.risk_level == NoOracleRiskLevel::Blocking
                && issue.field_name.as_deref() == Some("final_text")
        }));
    }

    #[test]
    fn forbidden_metadata_observed_after_text_is_detected() {
        let audit = audit_metadata_field_names(
            ["observed_after_text"],
            NoOracleUseContext::ForRanking,
            "SyntheticMetadata",
            None,
        );

        assert!(audit.issues.iter().any(|issue| {
            issue.risk_level == NoOracleRiskLevel::Blocking
                && issue.field_name.as_deref() == Some("observed_after_text")
        }));
    }

    #[test]
    fn forbidden_metadata_gold_label_is_detected() {
        let audit = audit_metadata_field_names(
            ["gold_label"],
            NoOracleUseContext::ForEvaluation,
            "SyntheticMetadata",
            None,
        );

        assert!(audit.issues.iter().any(|issue| {
            issue.risk_level == NoOracleRiskLevel::Unsafe
                && issue.field_name.as_deref() == Some("gold_label")
        }));
    }

    #[test]
    fn core_type_field_names_do_not_collide_with_forbidden_list() {
        for (artifact_type, fields) in [
            ("RawEvent", RAW_EVENT_FIELD_NAMES),
            ("RevisionEvent", REVISION_EVENT_FIELD_NAMES),
            ("MicroEpisode", MICRO_EPISODE_FIELD_NAMES),
        ] {
            let audit = audit_field_names(
                fields,
                NoOracleUseContext::ForCandidateGeneration,
                artifact_type,
                None,
            );

            assert!(
                audit.issues.is_empty(),
                "{artifact_type} field names should not collide: {:?}",
                audit.issues
            );
        }
    }

    #[test]
    fn raw_event_and_revision_event_audits_do_not_panic() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");
        let raw_audit = audit_raw_event(&events[0]);
        assert!(raw_audit.issues.is_empty());

        let revision_report =
            extract_revision_events(&events).expect("revision events extract successfully");
        let revision_audit = audit_revision_event(&revision_report.events[0]);
        assert!(revision_audit.issues.is_empty());
    }

    #[test]
    fn audit_handles_empty_metadata_without_panic() {
        let audit = audit_metadata_field_names(
            [],
            NoOracleUseContext::ForCandidateGeneration,
            "EmptySyntheticMetadata",
            None,
        );

        assert!(audit.issues.is_empty());
        assert_eq!(audit.checked_artifact_count, 1);
    }
}
