use std::{
    error::Error,
    fmt::{self, Display, Formatter},
    fs,
    io::Cursor,
    path::{Path, PathBuf},
};

use kslog_extract::{extract_revision_events, RevisionEventKind};
use kslog_micro_episode::build_micro_episodes;
use kslog_no_oracle_audit::{
    audit_micro_episodes, audit_no_oracle_safe_episode_view_for_candidate_generation,
    NoOracleRiskLevel, NoOracleSafeEpisodeView, NoOracleSafeEpisodeViewOptions, NoOracleUseContext,
};
use kslog_replay::{
    diagnose_replay_events, replay_events, ReplayDiagnosticFailureKind,
    ReplayDiagnosticProbableLayer, ReplayDiagnosticStatus,
};
use kslog_schema::RawEvent;
use kslog_validate::{validate_jsonl_reader, ValidationOptions};

#[derive(Debug)]
pub enum CliError {
    Usage(String),
    Io { path: PathBuf, message: String },
    Validation(String),
    ParseRawEvent { line_number: usize, message: String },
    Replay(String),
    Extraction(String),
    MicroEpisode(String),
    Export(String),
}

impl Display for CliError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::Usage(message) => write!(formatter, "{message}\n\n{}", usage()),
            Self::Io { path, message } => {
                write!(formatter, "I/O error at {}: {message}", path.display())
            }
            Self::Validation(message) => write!(formatter, "validation failed: {message}"),
            Self::ParseRawEvent {
                line_number,
                message,
            } => write!(
                formatter,
                "failed to parse RawEvent at line {line_number}: {message}"
            ),
            Self::Replay(message) => write!(formatter, "replay failed: {message}"),
            Self::Extraction(message) => write!(formatter, "revision extraction failed: {message}"),
            Self::MicroEpisode(message) => {
                write!(formatter, "micro-episode construction failed: {message}")
            }
            Self::Export(message) => write!(formatter, "safe-view export failed: {message}"),
        }
    }
}

impl Error for CliError {}

pub fn run_cli<I, S>(args: I) -> Result<String, CliError>
where
    I: IntoIterator<Item = S>,
    S: Into<String>,
{
    let args = args.into_iter().map(Into::into).collect::<Vec<_>>();
    let Some(command) = args.first().map(String::as_str) else {
        return Err(CliError::Usage("missing command".to_string()));
    };

    match command {
        "validate" => {
            let input = required_path(&args)?;
            command_validate(input)
        }
        "replay" => {
            let input = required_path(&args)?;
            command_replay(input)
        }
        "diagnose-replay" => {
            let input = required_path(&args)?;
            command_diagnose_replay(input)
        }
        "extract" => {
            let input = required_path(&args)?;
            command_extract(input)
        }
        "build-micro-episodes" => {
            let input = required_path(&args)?;
            command_build_micro_episodes(input)
        }
        "audit-no-oracle" => {
            let input = required_path(&args)?;
            command_audit_no_oracle(input)
        }
        "make-safe-view" => command_make_safe_view(&args),
        "export-safe-view" => command_export_safe_view(&args),
        "-h" | "--help" | "help" => Ok(usage()),
        other => Err(CliError::Usage(format!("unknown command: {other}"))),
    }
}

fn required_path(args: &[String]) -> Result<&Path, CliError> {
    match args {
        [_, path] => Ok(Path::new(path)),
        [_] => Err(CliError::Usage("missing input JSONL path".to_string())),
        _ => Err(CliError::Usage(
            "expected exactly one input JSONL path".to_string(),
        )),
    }
}

fn command_validate(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    let report = validate_content(&content)?;

    Ok(format!(
        "validation: ok\nevents: {}\nfirst_seq: {}\nlast_seq: {}\nfirst_timestamp_ms: {}\nlast_timestamp_ms: {}",
        report.event_count,
        option_u64(report.first_seq),
        option_u64(report.last_seq),
        option_u64(report.first_timestamp_ms),
        option_u64(report.last_timestamp_ms)
    ))
}

fn command_replay(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let report = replay_events(&events).map_err(|error| CliError::Replay(error.to_string()))?;

    Ok(format!(
        "replay: ok\nevents: {}\nfinal_doc_len: {}\nfinal_cursor_pos: {}\nfinal_text_suppressed: true",
        report.event_count, report.final_doc_len, report.final_cursor_pos
    ))
}

fn command_diagnose_replay(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let report = diagnose_replay_events(&events);

    Ok(format!(
        "diagnose_replay: ok\nreplay_status: {}\nevent_count: {}\nfailure_line: {}\nfailure_kind: {}\nsource_seq: {}\nevent_type: {}\ninput_type: {}\ndoc_len_before: {}\ndoc_len_after: {}\ncursor_pos_before: {}\ncursor_pos_after: {}\nselection_start_before: {}\nselection_end_before: {}\nselection_start_after: {}\nselection_end_after: {}\ninserted_text_present: {}\ninserted_text_len: {}\ndeleted_text_present: {}\ndeleted_text_len: {}\ndiff_op: {}\nquality_flags: {}\ncontent_suppressed: {}\nprobable_layer: {}\nsuggested_next_check: {}",
        diagnostic_status_name(&report.replay_status),
        report.event_count,
        option_usize(report.failure_line),
        option_failure_kind(report.failure_kind.as_ref()),
        option_u64(report.source_seq),
        report
            .event_type
            .as_ref()
            .map(|event_type| format!("{event_type:?}"))
            .unwrap_or_else(|| "none".to_string()),
        option_string(report.input_type.as_deref()),
        option_u32(report.doc_len_before),
        option_u32(report.doc_len_after),
        option_u32(report.cursor_pos_before),
        option_u32(report.cursor_pos_after),
        option_u32(report.selection_start_before),
        option_u32(report.selection_end_before),
        option_u32(report.selection_start_after),
        option_u32(report.selection_end_after),
        option_bool(report.inserted_text_present),
        option_usize(report.inserted_text_len),
        option_bool(report.deleted_text_present),
        option_usize(report.deleted_text_len),
        option_string(report.diff_op.as_deref()),
        if report.quality_flags.is_empty() {
            "none".to_string()
        } else {
            report.quality_flags.join(",")
        },
        report.content_suppressed,
        probable_layer_name(&report.probable_layer),
        report.suggested_next_check
    ))
}

fn command_extract(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let report = extract_revision_events(&events)
        .map_err(|error| CliError::Extraction(error.to_string()))?;
    let counts = KindCounts::from_events(&report.events);

    Ok(format!(
        "revision_events: ok\nsource_events: {}\nrevision_events: {}\nunsupported_events: {}\n{}",
        report.source_event_count,
        report.events.len(),
        report.unsupported_event_count,
        counts.format()
    ))
}

fn command_build_micro_episodes(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let report =
        build_micro_episodes(&events).map_err(|error| CliError::MicroEpisode(error.to_string()))?;
    let revision_like_count = report
        .episodes
        .iter()
        .filter(|episode| episode.is_revision_like)
        .count();

    Ok(format!(
        "micro_episodes: ok\nepisodes: {}\nrevision_like_episodes: {}\nskipped_events: {}\ncontext_window_chars: {}",
        report.episodes.len(),
        revision_like_count,
        report.skipped_event_count,
        report.context_window_chars
    ))
}

fn command_audit_no_oracle(path: &Path) -> Result<String, CliError> {
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let episode_report =
        build_micro_episodes(&events).map_err(|error| CliError::MicroEpisode(error.to_string()))?;
    let audit_report = audit_micro_episodes(
        &episode_report.episodes,
        NoOracleUseContext::ForCandidateGeneration,
    );

    let unsafe_count = audit_report
        .issues
        .iter()
        .filter(|issue| {
            matches!(
                issue.risk_level,
                NoOracleRiskLevel::Unsafe | NoOracleRiskLevel::Blocking
            )
        })
        .count();

    Ok(format!(
        "no_oracle_audit: ok\nuse_context: ForCandidateGeneration\nepisodes_checked: {}\nissues: {}\nunsafe_or_blocking_issues: {}",
        audit_report.checked_artifact_count,
        audit_report.issues.len(),
        unsafe_count
    ))
}

fn command_make_safe_view(args: &[String]) -> Result<String, CliError> {
    let mut exclude_observed_edit_text = false;
    let mut path = None;

    for arg in args.iter().skip(1) {
        if arg == "--exclude-observed-edit-text" {
            exclude_observed_edit_text = true;
        } else if path.is_none() {
            path = Some(Path::new(arg));
        } else {
            return Err(CliError::Usage(
                "make-safe-view expected one input path and optional --exclude-observed-edit-text"
                    .to_string(),
            ));
        }
    }

    let path = path.ok_or_else(|| CliError::Usage("missing input JSONL path".to_string()))?;
    let content = read_file(path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let episode_report =
        build_micro_episodes(&events).map_err(|error| CliError::MicroEpisode(error.to_string()))?;
    let options = NoOracleSafeEpisodeViewOptions {
        include_observed_edit_text: !exclude_observed_edit_text,
    };
    let safe_views = episode_report
        .episodes
        .iter()
        .map(|episode| {
            NoOracleSafeEpisodeView::try_from_micro_episode_with_options(episode, &options)
        })
        .collect::<Vec<_>>();
    let audited_issue_count = safe_views
        .iter()
        .map(audit_no_oracle_safe_episode_view_for_candidate_generation)
        .map(|report| report.issues.len())
        .sum::<usize>();

    Ok(format!(
        "safe_view: ok\nsafe_views: {}\nfields: {}\ncontains_local_context_after_observed: false\nobserved_edit_text_included: {}\ncandidate_generation_audit_issues: {}",
        safe_views.len(),
        NoOracleSafeEpisodeView::field_names().join(","),
        !exclude_observed_edit_text,
        audited_issue_count
    ))
}

fn command_export_safe_view(args: &[String]) -> Result<String, CliError> {
    let ExportSafeViewArgs {
        input_path,
        output_path,
        include_observed_edit_text,
    } = parse_export_safe_view_args(args)?;
    let content = read_file(input_path)?;
    validate_content(&content)?;
    let events = parse_events(&content)?;
    let episode_report =
        build_micro_episodes(&events).map_err(|error| CliError::MicroEpisode(error.to_string()))?;
    let options = NoOracleSafeEpisodeViewOptions {
        include_observed_edit_text,
    };
    let safe_views = episode_report
        .episodes
        .iter()
        .map(|episode| {
            NoOracleSafeEpisodeView::try_from_micro_episode_with_options(episode, &options)
        })
        .collect::<Vec<_>>();
    let blocking_issue_count = safe_views
        .iter()
        .map(audit_no_oracle_safe_episode_view_for_candidate_generation)
        .flat_map(|report| report.issues)
        .filter(|issue| {
            matches!(
                issue.risk_level,
                NoOracleRiskLevel::Unsafe | NoOracleRiskLevel::Blocking
            )
        })
        .count();

    if blocking_issue_count > 0 {
        return Err(CliError::Export(format!(
            "candidate-generation audit found {blocking_issue_count} unsafe or blocking issue(s)"
        )));
    }

    let mut output = String::new();
    for safe_view in &safe_views {
        let line = serde_json::to_string(safe_view)
            .map_err(|error| CliError::Export(format!("failed to serialize safe view: {error}")))?;
        output.push_str(&line);
        output.push('\n');
    }

    if let Some(parent) = output_path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent).map_err(|error| CliError::Io {
                path: parent.to_path_buf(),
                message: error.to_string(),
            })?;
        }
    }
    fs::write(output_path, output).map_err(|error| CliError::Io {
        path: output_path.to_path_buf(),
        message: error.to_string(),
    })?;

    Ok(format!(
        "export_safe_view: ok\nsafe_views: {}\noutput_path: {}\nobserved_edit_text_included: {}\nlocal_context_after_observed_included: false\ncandidate_generation_audit_issues: 0",
        safe_views.len(),
        output_path.display(),
        include_observed_edit_text
    ))
}

struct ExportSafeViewArgs<'a> {
    input_path: &'a Path,
    output_path: &'a Path,
    include_observed_edit_text: bool,
}

fn parse_export_safe_view_args(args: &[String]) -> Result<ExportSafeViewArgs<'_>, CliError> {
    let mut paths = Vec::new();
    let mut include_observed_edit_text = false;
    let mut include_seen = false;
    let mut exclude_seen = false;

    for arg in args.iter().skip(1) {
        match arg.as_str() {
            "--include-observed-edit-text" => {
                include_seen = true;
                include_observed_edit_text = true;
            }
            "--exclude-observed-edit-text" => {
                exclude_seen = true;
                include_observed_edit_text = false;
            }
            _ => paths.push(Path::new(arg)),
        }
    }

    if include_seen && exclude_seen {
        return Err(CliError::Usage(
            "export-safe-view accepts only one observed-edit-text option".to_string(),
        ));
    }

    match paths.as_slice() {
        [input_path, output_path] => Ok(ExportSafeViewArgs {
            input_path,
            output_path,
            include_observed_edit_text,
        }),
        [_] => Err(CliError::Usage(
            "missing output JSONL path for export-safe-view".to_string(),
        )),
        [] => Err(CliError::Usage(
            "missing input and output JSONL paths for export-safe-view".to_string(),
        )),
        _ => Err(CliError::Usage(
            "export-safe-view expected input path, output path, and optional observed-edit-text flag"
                .to_string(),
        )),
    }
}

fn read_file(path: &Path) -> Result<String, CliError> {
    fs::read_to_string(path).map_err(|error| CliError::Io {
        path: path.to_path_buf(),
        message: error.to_string(),
    })
}

fn validate_content(content: &str) -> Result<kslog_validate::ValidationReport, CliError> {
    validate_jsonl_reader(Cursor::new(content), &ValidationOptions::default())
        .map_err(|error| CliError::Validation(error.to_string()))
}

fn parse_events(content: &str) -> Result<Vec<RawEvent>, CliError> {
    content
        .lines()
        .enumerate()
        .filter(|(_, line)| !line.trim().is_empty())
        .map(|(line_index, line)| {
            serde_json::from_str::<RawEvent>(line).map_err(|error| CliError::ParseRawEvent {
                line_number: line_index + 1,
                message: error.to_string(),
            })
        })
        .collect()
}

fn option_u64(value: Option<u64>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "none".to_string())
}

fn option_u32(value: Option<u32>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "none".to_string())
}

fn option_usize(value: Option<usize>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "none".to_string())
}

fn option_bool(value: Option<bool>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "none".to_string())
}

fn option_string(value: Option<&str>) -> String {
    value.unwrap_or("none").to_string()
}

fn diagnostic_status_name(status: &ReplayDiagnosticStatus) -> &'static str {
    match status {
        ReplayDiagnosticStatus::Ok => "ok",
        ReplayDiagnosticStatus::Failed => "failed",
    }
}

fn option_failure_kind(kind: Option<&ReplayDiagnosticFailureKind>) -> &'static str {
    match kind {
        Some(ReplayDiagnosticFailureKind::DocLenBeforeMismatch) => "doc_len_before_mismatch",
        Some(ReplayDiagnosticFailureKind::DocLenAfterMismatch) => "doc_len_after_mismatch",
        Some(ReplayDiagnosticFailureKind::TextHashBeforeMismatch) => "text_hash_before_mismatch",
        Some(ReplayDiagnosticFailureKind::TextHashAfterMismatch) => "text_hash_after_mismatch",
        Some(ReplayDiagnosticFailureKind::CursorOutOfBounds) => "cursor_out_of_bounds",
        Some(ReplayDiagnosticFailureKind::SelectionOutOfBounds) => "selection_out_of_bounds",
        Some(ReplayDiagnosticFailureKind::SelectionRangeInverted) => "selection_range_inverted",
        Some(ReplayDiagnosticFailureKind::AmbiguousEditLocation) => "ambiguous_edit_location",
        Some(ReplayDiagnosticFailureKind::DeletedTextMismatch) => "deleted_text_mismatch",
        None => "none",
    }
}

fn probable_layer_name(layer: &ReplayDiagnosticProbableLayer) -> &'static str {
    match layer {
        ReplayDiagnosticProbableLayer::LoggerDiffEstimation => "logger_diff_estimation",
        ReplayDiagnosticProbableLayer::CursorOrSelectionCapture => "cursor_or_selection_capture",
        ReplayDiagnosticProbableLayer::ReplayAssumption => "replay_assumption",
        ReplayDiagnosticProbableLayer::SchemaOrValidation => "schema_or_validation",
        ReplayDiagnosticProbableLayer::Unknown => "unknown",
    }
}

fn usage() -> String {
    [
        "kslog <command> <input.jsonl>",
        "",
        "Commands:",
        "  validate <input.jsonl>",
        "  replay <input.jsonl>",
        "  diagnose-replay <input.jsonl>",
        "  extract <input.jsonl>",
        "  build-micro-episodes <input.jsonl>",
        "  audit-no-oracle <input.jsonl>",
        "  make-safe-view <input.jsonl> [--exclude-observed-edit-text]",
        "  export-safe-view <input.jsonl> <output.jsonl> [--exclude-observed-edit-text|--include-observed-edit-text]",
    ]
    .join("\n")
}

#[derive(Debug, Default)]
struct KindCounts {
    insertion: usize,
    deletion: usize,
    replacement: usize,
    selection_range_edit: usize,
    paste: usize,
    composition_commit: usize,
    unsupported: usize,
}

impl KindCounts {
    fn from_events(events: &[kslog_extract::RevisionEvent]) -> Self {
        let mut counts = Self::default();
        for event in events {
            match event.kind {
                RevisionEventKind::Insertion => counts.insertion += 1,
                RevisionEventKind::Deletion => counts.deletion += 1,
                RevisionEventKind::Replacement => counts.replacement += 1,
                RevisionEventKind::SelectionRangeEdit => counts.selection_range_edit += 1,
                RevisionEventKind::Paste => counts.paste += 1,
                RevisionEventKind::CompositionCommit => counts.composition_commit += 1,
                RevisionEventKind::Unsupported => counts.unsupported += 1,
            }
        }
        counts
    }

    fn format(&self) -> String {
        format!(
            "kind_counts: insertion={}, deletion={}, replacement={}, selection_range_edit={}, paste={}, composition_commit={}, unsupported={}",
            self.insertion,
            self.deletion,
            self.replacement,
            self.selection_range_edit,
            self.paste,
            self.composition_commit,
            self.unsupported
        )
    }
}

#[cfg(test)]
mod tests {
    use super::run_cli;
    use std::{
        fs,
        path::{Path, PathBuf},
    };

    fn repository_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
    }

    fn fixture(relative_path: &str) -> String {
        repository_root()
            .join(relative_path)
            .to_string_lossy()
            .into_owned()
    }

    #[test]
    fn validates_simple_typing_fixture() {
        let output = run_cli([
            "validate",
            fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl").as_str(),
        ])
        .expect("validate should succeed");

        assert!(output.contains("validation: ok"));
        assert!(output.contains("events: 6"));
    }

    #[test]
    fn validate_fails_for_seq_gap_fixture() {
        let error = run_cli([
            "validate",
            fixture("tests/fixtures/synthetic/raw_events/invalid/seq_gap.jsonl").as_str(),
        ])
        .expect_err("seq gap fixture should fail validation");

        assert!(error.to_string().contains("seq is not consecutive"));
    }

    #[test]
    fn replays_deletion_fixture_without_printing_final_text() {
        let output = run_cli([
            "replay",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
        ])
        .expect("replay should succeed");

        assert!(output.contains("replay: ok"));
        assert!(output.contains("final_doc_len: 13"));
        assert!(output.contains("final_text_suppressed: true"));
        assert!(!output.contains("I like music."));
    }

    #[test]
    fn diagnose_replay_returns_success_summary_for_valid_fixture() {
        let output = run_cli([
            "diagnose-replay",
            fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl").as_str(),
        ])
        .expect("diagnose replay should succeed");

        assert!(output.contains("diagnose_replay: ok"));
        assert!(output.contains("replay_status: ok"));
        assert!(output.contains("content_suppressed: true"));
        assert!(output.contains("failure_kind: none"));
        assert!(!output.contains("I like music."));
    }

    #[test]
    fn diagnose_replay_returns_safe_failure_summary() {
        let path = std::env::temp_dir().join(format!(
            "kslog_cli_diagnose_replay_{}.jsonl",
            std::process::id()
        ));
        let jsonl = r#"{"logger_schema_version":"kslog.raw_event.v1","session_id":"synthetic_session_cli_diag","participant_local_id":"synthetic_writer_cli_diag","task_id":"synthetic_task_cli_diag","prompt_id":"synthetic_prompt_cli_diag","seq":1,"timestamp_ms":1700000100001,"event_type":"input","input_type":"insertText","is_composing":false,"composition_id":null,"selection_start_before":null,"selection_end_before":null,"selection_start_after":null,"selection_end_after":null,"cursor_pos_before":0,"cursor_pos_after":1,"doc_len_before":0,"doc_len_after":1,"inserted_text":"x","deleted_text":null,"text_hash_before":null,"text_hash_after":null,"diff_op":"insert","quality_flags":[]}
{"logger_schema_version":"kslog.raw_event.v1","session_id":"synthetic_session_cli_diag","participant_local_id":"synthetic_writer_cli_diag","task_id":"synthetic_task_cli_diag","prompt_id":"synthetic_prompt_cli_diag","seq":2,"timestamp_ms":1700000100002,"event_type":"input","input_type":"deleteContentBackward","is_composing":false,"composition_id":null,"selection_start_before":null,"selection_end_before":null,"selection_start_after":null,"selection_end_after":null,"cursor_pos_before":1,"cursor_pos_after":0,"doc_len_before":1,"doc_len_after":0,"inserted_text":null,"deleted_text":"LEAK_MARKER_SHOULD_NOT_APPEAR","text_hash_before":null,"text_hash_after":null,"diff_op":"delete","quality_flags":[]}
"#;
        fs::write(&path, jsonl).expect("write synthetic diagnostic fixture");

        let output = run_cli(["diagnose-replay", path.to_string_lossy().as_ref()])
            .expect("diagnose replay should return a safe failure summary");

        let _ = fs::remove_file(&path);

        assert!(output.contains("diagnose_replay: ok"));
        assert!(output.contains("replay_status: failed"));
        assert!(output.contains("failure_kind: deleted_text_mismatch"));
        assert!(output.contains("probable_layer: logger_diff_estimation"));
        assert!(output.contains("content_suppressed: true"));
        assert!(output.contains("deleted_text_present: true"));
        assert!(output.contains("deleted_text_len:"));
        assert!(!output.contains("LEAK_MARKER_SHOULD_NOT_APPEAR"));
    }

    #[test]
    fn extracts_revision_event_summary_for_replacement_fixture() {
        let output = run_cli([
            "extract",
            fixture("tests/fixtures/synthetic/raw_events/valid/replacement_case.jsonl").as_str(),
        ])
        .expect("extract should succeed");

        assert!(output.contains("revision_events: ok"));
        assert!(output.contains("selection_range_edit=1"));
    }

    #[test]
    fn builds_micro_episode_summary_for_selection_edit_fixture() {
        let output = run_cli([
            "build-micro-episodes",
            fixture("tests/fixtures/synthetic/raw_events/valid/selection_edit_case.jsonl").as_str(),
        ])
        .expect("micro episode build should succeed");

        assert!(output.contains("micro_episodes: ok"));
        assert!(output.contains("episodes: 2"));
        assert!(output.contains("revision_like_episodes: 1"));
    }

    #[test]
    fn audit_no_oracle_does_not_panic() {
        let output = run_cli([
            "audit-no-oracle",
            fixture("tests/fixtures/synthetic/raw_events/valid/paste_case.jsonl").as_str(),
        ])
        .expect("audit should succeed");

        assert!(output.contains("no_oracle_audit: ok"));
        assert!(output.contains("unsafe_or_blocking_issues:"));
    }

    #[test]
    fn make_safe_view_excludes_after_observed_context() {
        let output = run_cli([
            "make-safe-view",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
            "--exclude-observed-edit-text",
        ])
        .expect("safe view should succeed");

        assert!(output.contains("safe_view: ok"));
        assert!(output.contains("contains_local_context_after_observed: false"));
        assert!(output.contains("observed_edit_text_included: false"));
        assert!(!output.contains("local_context_after_observed,"));
    }

    #[test]
    fn export_safe_view_writes_parseable_jsonl_without_forbidden_fields_by_default() {
        let path = std::env::temp_dir().join(format!(
            "kslog_cli_safe_view_export_{}.jsonl",
            std::process::id()
        ));
        let _ = fs::remove_file(&path);

        let output = run_cli([
            "export-safe-view",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
            path.to_string_lossy().as_ref(),
        ])
        .expect("safe-view export should succeed");

        assert!(output.contains("export_safe_view: ok"));
        assert!(output.contains("observed_edit_text_included: false"));
        assert!(output.contains("local_context_after_observed_included: false"));
        assert!(output.contains("candidate_generation_audit_issues: 0"));

        let exported = fs::read_to_string(&path).expect("export output should be readable");
        let _ = fs::remove_file(&path);
        let rows = exported
            .lines()
            .map(|line| serde_json::from_str::<serde_json::Value>(line).expect("JSONL row parses"))
            .collect::<Vec<_>>();

        assert!(!rows.is_empty());
        for row in rows {
            assert!(row.get("episode_id").is_some());
            assert_eq!(
                row.get("no_oracle_safe_view")
                    .and_then(|value| value.as_bool()),
                Some(true)
            );
            assert_eq!(
                row.get("post_edit_context_suppressed")
                    .and_then(|value| value.as_bool()),
                Some(true)
            );
            assert_eq!(
                row.get("observed_edit_text_included")
                    .and_then(|value| value.as_bool()),
                Some(false)
            );
            assert!(row.get("local_context_after_observed").is_none());
            assert!(row.get("final_text").is_none());
            assert!(row.get("observed_after_text").is_none());
            assert!(row.get("gold_label").is_none());
            assert!(row.get("teacher_correction").is_none());
            assert!(row.get("inserted_text_observed").is_none());
            assert!(row.get("deleted_text_observed").is_none());
        }
    }

    #[test]
    fn export_safe_view_can_include_observed_edit_text_explicitly() {
        let path = std::env::temp_dir().join(format!(
            "kslog_cli_safe_view_export_include_{}.jsonl",
            std::process::id()
        ));
        let _ = fs::remove_file(&path);

        let output = run_cli([
            "export-safe-view",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
            path.to_string_lossy().as_ref(),
            "--include-observed-edit-text",
        ])
        .expect("safe-view export should succeed");

        assert!(output.contains("observed_edit_text_included: true"));

        let exported = fs::read_to_string(&path).expect("export output should be readable");
        let _ = fs::remove_file(&path);
        let rows = exported
            .lines()
            .map(|line| serde_json::from_str::<serde_json::Value>(line).expect("JSONL row parses"))
            .collect::<Vec<_>>();

        assert!(rows
            .iter()
            .any(|row| row.get("deleted_text_observed").is_some()));
        assert!(rows
            .iter()
            .all(|row| row.get("local_context_after_observed").is_none()));
    }

    #[test]
    fn export_safe_view_creates_missing_output_parent_without_panic() {
        let base = std::env::temp_dir().join(format!(
            "kslog_cli_safe_view_export_nested_{}",
            std::process::id()
        ));
        let path = base.join("nested").join("safe_view.jsonl");
        let _ = fs::remove_dir_all(&base);

        let output = run_cli([
            "export-safe-view",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
            path.to_string_lossy().as_ref(),
        ])
        .expect("safe-view export should create missing parent directories");

        assert!(output.contains("export_safe_view: ok"));
        assert!(path.exists());
        let exported = fs::read_to_string(&path).expect("export output should be readable");
        assert!(!exported.lines().collect::<Vec<_>>().is_empty());

        let _ = fs::remove_dir_all(&base);
    }

    #[test]
    fn export_safe_view_missing_args_returns_usage_error_without_panic() {
        let error = run_cli(["export-safe-view"]).expect_err("missing args should fail");

        assert!(error
            .to_string()
            .contains("missing input and output JSONL paths"));
        assert!(error
            .to_string()
            .contains("export-safe-view <input.jsonl> <output.jsonl>"));
    }

    #[test]
    fn export_safe_view_conflicting_options_return_usage_error() {
        let error = run_cli([
            "export-safe-view",
            fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl").as_str(),
            std::env::temp_dir()
                .join("kslog_conflicting_export_options.jsonl")
                .to_string_lossy()
                .as_ref(),
            "--include-observed-edit-text",
            "--exclude-observed-edit-text",
        ])
        .expect_err("conflicting options should fail");

        assert!(error
            .to_string()
            .contains("only one observed-edit-text option"));
    }

    #[test]
    fn missing_args_returns_usage_error_without_panic() {
        let error = run_cli(Vec::<String>::new()).expect_err("missing args should fail");

        assert!(error.to_string().contains("missing command"));
        assert!(error.to_string().contains("kslog <command> <input.jsonl>"));
    }

    #[test]
    fn diagnose_replay_missing_path_returns_usage_error_without_panic() {
        let error = run_cli(["diagnose-replay"]).expect_err("missing path should fail");

        assert!(error.to_string().contains("missing input JSONL path"));
        assert!(error.to_string().contains("diagnose-replay <input.jsonl>"));
    }
}
