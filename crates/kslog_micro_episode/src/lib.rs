//! Micro-episode construction from revision events.
//!
//! A micro-episode is a local analysis unit centered on one observed
//! `RevisionEvent`. It is not a correctness label and does not represent a
//! learner's internal state.

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
};

use kslog_extract::{
    extract_revision_events, RevisionEvent, RevisionEventKind, RevisionExtractionError,
};
use kslog_schema::RawEvent;

pub const DEFAULT_CONTEXT_WINDOW_CHARS: usize = 30;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MicroEpisodeOptions {
    pub context_window_chars: usize,
    pub include_non_revision_like: bool,
    pub include_unsupported: bool,
}

impl Default for MicroEpisodeOptions {
    fn default() -> Self {
        Self {
            context_window_chars: DEFAULT_CONTEXT_WINDOW_CHARS,
            include_non_revision_like: true,
            include_unsupported: true,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MicroEpisodeContext {
    pub text: String,
    pub anchor: u32,
    pub window_start: u32,
    pub window_end: u32,
    pub window_size: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MicroEpisodeTarget {
    pub span_start: Option<u32>,
    pub span_end: Option<u32>,
    pub inserted_text: Option<String>,
    pub deleted_text: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MicroEpisode {
    pub micro_episode_id: String,
    pub session_id: String,
    pub task_id: String,
    pub prompt_id: String,
    pub source_revision_event_id: String,
    pub source_seq: u64,
    pub timestamp_ms: u64,
    pub revision_kind: RevisionEventKind,
    pub is_revision_like: bool,
    pub local_context_before: MicroEpisodeContext,
    /// Observed post-edit context. This is no-oracle unsafe for candidate
    /// generation and ranking; keep it for reconstruction checks/evaluation only.
    pub local_context_after_observed: MicroEpisodeContext,
    pub target: MicroEpisodeTarget,
    pub cursor_pos_before: Option<u32>,
    pub cursor_pos_after: Option<u32>,
    pub span_start: Option<u32>,
    pub span_end: Option<u32>,
    pub inserted_text: Option<String>,
    pub deleted_text: Option<String>,
    pub doc_len_before: Option<u32>,
    pub doc_len_after: Option<u32>,
    pub quality_flags: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MicroEpisodeConstructionReport {
    pub episodes: Vec<MicroEpisode>,
    pub source_revision_event_count: usize,
    pub skipped_event_count: usize,
    pub context_window_chars: usize,
}

pub type MicroEpisodeConstructionResult<T> = Result<T, MicroEpisodeConstructionError>;

#[derive(Debug)]
pub enum MicroEpisodeConstructionError {
    Extraction(RevisionExtractionError),
    InvalidSpan {
        source_revision_event_id: String,
        start: u32,
        end: u32,
    },
    SpanOutOfBounds {
        source_revision_event_id: String,
        start: u32,
        end: u32,
        doc_len: usize,
    },
    DeletedTextMismatch {
        source_revision_event_id: String,
        expected: String,
        actual: String,
    },
    MissingEditLocation {
        source_revision_event_id: String,
    },
}

impl Display for MicroEpisodeConstructionError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::Extraction(error) => write!(formatter, "revision extraction failed: {error}"),
            Self::InvalidSpan {
                source_revision_event_id,
                start,
                end,
            } => write!(
                formatter,
                "invalid span for {source_revision_event_id}: {start} > {end}"
            ),
            Self::SpanOutOfBounds {
                source_revision_event_id,
                start,
                end,
                doc_len,
            } => write!(
                formatter,
                "span out of bounds for {source_revision_event_id}: {start}..{end} exceeds {doc_len}"
            ),
            Self::DeletedTextMismatch {
                source_revision_event_id,
                expected,
                actual,
            } => write!(
                formatter,
                "deleted text mismatch for {source_revision_event_id}: expected {expected:?}, got {actual:?}"
            ),
            Self::MissingEditLocation {
                source_revision_event_id,
            } => write!(
                formatter,
                "missing edit location for {source_revision_event_id}"
            ),
        }
    }
}

impl Error for MicroEpisodeConstructionError {}

impl From<RevisionExtractionError> for MicroEpisodeConstructionError {
    fn from(error: RevisionExtractionError) -> Self {
        Self::Extraction(error)
    }
}

pub fn build_micro_episodes(
    events: &[RawEvent],
) -> MicroEpisodeConstructionResult<MicroEpisodeConstructionReport> {
    build_micro_episodes_with_options(events, &MicroEpisodeOptions::default())
}

pub fn build_micro_episodes_with_options(
    events: &[RawEvent],
    options: &MicroEpisodeOptions,
) -> MicroEpisodeConstructionResult<MicroEpisodeConstructionReport> {
    let extraction_report = extract_revision_events(events)?;
    let mut text_state = String::new();
    let mut episodes = Vec::new();
    let mut skipped_event_count = 0;

    for revision_event in &extraction_report.events {
        let text_before = text_state.clone();
        let before_anchor = anchor_before(revision_event)?;
        let local_context_before =
            context_window(&text_before, before_anchor, options.context_window_chars);

        apply_revision_event(&mut text_state, revision_event)?;

        let after_anchor = anchor_after(revision_event);
        let local_context_after_observed =
            context_window(&text_state, after_anchor, options.context_window_chars);

        if should_skip_episode(revision_event, options) {
            skipped_event_count += 1;
            continue;
        }

        let span_start = revision_event.span.as_ref().map(|span| span.start);
        let span_end = revision_event.span.as_ref().map(|span| span.end);
        let source_revision_event_id = revision_event.revision_event_id.clone();

        episodes.push(MicroEpisode {
            micro_episode_id: format!(
                "{}:micro:{}",
                revision_event.session_id, revision_event.source_seq
            ),
            session_id: revision_event.session_id.clone(),
            task_id: revision_event.task_id.clone(),
            prompt_id: revision_event.prompt_id.clone(),
            source_revision_event_id,
            source_seq: revision_event.source_seq,
            timestamp_ms: revision_event.timestamp_ms,
            revision_kind: revision_event.kind.clone(),
            is_revision_like: revision_event.is_revision_like,
            local_context_before,
            local_context_after_observed,
            target: MicroEpisodeTarget {
                span_start,
                span_end,
                inserted_text: revision_event.inserted_text.clone(),
                deleted_text: revision_event.deleted_text.clone(),
            },
            cursor_pos_before: revision_event.cursor_pos_before,
            cursor_pos_after: revision_event.cursor_pos_after,
            span_start,
            span_end,
            inserted_text: revision_event.inserted_text.clone(),
            deleted_text: revision_event.deleted_text.clone(),
            doc_len_before: revision_event.doc_len_before,
            doc_len_after: revision_event.doc_len_after,
            quality_flags: revision_event.quality_flags.clone(),
        });
    }

    Ok(MicroEpisodeConstructionReport {
        episodes,
        source_revision_event_count: extraction_report.events.len(),
        skipped_event_count,
        context_window_chars: options.context_window_chars,
    })
}

fn should_skip_episode(revision_event: &RevisionEvent, options: &MicroEpisodeOptions) -> bool {
    (!options.include_non_revision_like && !revision_event.is_revision_like)
        || (!options.include_unsupported && revision_event.kind == RevisionEventKind::Unsupported)
}

fn anchor_before(revision_event: &RevisionEvent) -> MicroEpisodeConstructionResult<u32> {
    if let Some(span) = &revision_event.span {
        return Ok(span.start);
    }

    revision_event.cursor_pos_before.ok_or_else(|| {
        MicroEpisodeConstructionError::MissingEditLocation {
            source_revision_event_id: revision_event.revision_event_id.clone(),
        }
    })
}

fn anchor_after(revision_event: &RevisionEvent) -> u32 {
    revision_event.cursor_pos_after.unwrap_or_else(|| {
        revision_event
            .span
            .as_ref()
            .map(|span| span.start)
            .unwrap_or(0)
    })
}

fn apply_revision_event(
    text_state: &mut String,
    revision_event: &RevisionEvent,
) -> MicroEpisodeConstructionResult<()> {
    match revision_event.kind {
        RevisionEventKind::Unsupported => Ok(()),
        RevisionEventKind::Insertion
        | RevisionEventKind::Paste
        | RevisionEventKind::CompositionCommit
        | RevisionEventKind::SelectionRangeEdit
        | RevisionEventKind::Replacement
        | RevisionEventKind::Deletion => {
            let (start, end) = span_bounds(revision_event, text_state)?;
            if let Some(deleted_text) = &revision_event.deleted_text {
                let actual = slice_chars(text_state, start, end);
                if actual != *deleted_text {
                    return Err(MicroEpisodeConstructionError::DeletedTextMismatch {
                        source_revision_event_id: revision_event.revision_event_id.clone(),
                        expected: deleted_text.clone(),
                        actual,
                    });
                }
            }

            let inserted_text = revision_event.inserted_text.as_deref().unwrap_or("");
            replace_range(text_state, start, end, inserted_text);
            Ok(())
        }
    }
}

fn span_bounds(
    revision_event: &RevisionEvent,
    text_state: &str,
) -> MicroEpisodeConstructionResult<(usize, usize)> {
    let Some(span) = &revision_event.span else {
        return Err(MicroEpisodeConstructionError::MissingEditLocation {
            source_revision_event_id: revision_event.revision_event_id.clone(),
        });
    };

    if span.start > span.end {
        return Err(MicroEpisodeConstructionError::InvalidSpan {
            source_revision_event_id: revision_event.revision_event_id.clone(),
            start: span.start,
            end: span.end,
        });
    }

    let start = span.start as usize;
    let end = span.end as usize;
    let doc_len = char_count(text_state);
    if end > doc_len {
        return Err(MicroEpisodeConstructionError::SpanOutOfBounds {
            source_revision_event_id: revision_event.revision_event_id.clone(),
            start: span.start,
            end: span.end,
            doc_len,
        });
    }

    Ok((start, end))
}

fn context_window(text: &str, anchor: u32, window_size: usize) -> MicroEpisodeContext {
    let char_len = char_count(text);
    let anchor = (anchor as usize).min(char_len);
    let window_start = anchor.saturating_sub(window_size);
    let window_end = anchor.saturating_add(window_size).min(char_len);

    MicroEpisodeContext {
        text: slice_chars(text, window_start, window_end),
        anchor: anchor as u32,
        window_start: window_start as u32,
        window_end: window_end as u32,
        window_size,
    }
}

fn replace_range(text: &mut String, start: usize, end: usize, inserted_text: &str) {
    let start_byte = char_to_byte_index(text, start);
    let end_byte = char_to_byte_index(text, end);
    text.replace_range(start_byte..end_byte, inserted_text);
}

fn char_count(text: &str) -> usize {
    text.chars().count()
}

fn char_to_byte_index(text: &str, char_index: usize) -> usize {
    text.char_indices()
        .nth(char_index)
        .map(|(byte_index, _)| byte_index)
        .unwrap_or(text.len())
}

fn slice_chars(text: &str, start: usize, end: usize) -> String {
    text.chars().skip(start).take(end - start).collect()
}

#[cfg(test)]
mod tests {
    use super::{
        build_micro_episodes, build_micro_episodes_with_options, MicroEpisodeConstructionError,
        MicroEpisodeOptions,
    };
    use kslog_extract::RevisionEventKind;
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
    fn deletion_fixture_builds_micro_episode() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");

        let report = build_micro_episodes(&events).expect("deletion fixture builds episodes");

        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.revision_kind == RevisionEventKind::Deletion)
            .expect("deletion micro episode exists");
        assert_eq!(episode.deleted_text.as_deref(), Some("s"));
        assert_eq!(episode.local_context_before.text, "I likes music.");
        assert_eq!(episode.local_context_after_observed.text, "I like music.");
    }

    #[test]
    fn replacement_fixture_builds_micro_episode() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/replacement_case.jsonl");

        let report = build_micro_episodes(&events).expect("replacement fixture builds episodes");

        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.revision_kind == RevisionEventKind::Replacement)
            .expect("replacement micro episode exists");
        assert_eq!(episode.inserted_text.as_deref(), Some("go to"));
        assert_eq!(episode.deleted_text.as_deref(), Some("go"));
        assert_eq!(episode.local_context_after_observed.text, "I go to school.");
    }

    #[test]
    fn selection_edit_fixture_builds_micro_episode() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/selection_edit_case.jsonl",
        );

        let report = build_micro_episodes(&events).expect("selection fixture builds episodes");

        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.deleted_text.as_deref() == Some("song"))
            .expect("selection edit micro episode exists");
        assert_eq!(episode.span_start, Some(8));
        assert_eq!(episode.span_end, Some(12));
        assert_eq!(episode.local_context_before.text, "I enjoy song.");
        assert_eq!(episode.local_context_after_observed.text, "I enjoy music.");
    }

    #[test]
    fn paste_fixture_builds_micro_episode() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/paste_case.jsonl");

        let report = build_micro_episodes(&events).expect("paste fixture builds episodes");

        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.revision_kind == RevisionEventKind::Paste)
            .expect("paste micro episode exists");
        assert_eq!(episode.inserted_text.as_deref(), Some("synthetic note"));
        assert!(episode.is_revision_like);
    }

    #[test]
    fn simple_typing_keeps_non_revision_like_insertions_by_default() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");

        let report = build_micro_episodes(&events).expect("simple typing builds episodes");

        assert_eq!(report.episodes.len(), 6);
        assert!(report
            .episodes
            .iter()
            .all(|episode| episode.revision_kind == RevisionEventKind::Insertion));
        assert!(report
            .episodes
            .iter()
            .all(|episode| !episode.is_revision_like));
    }

    #[test]
    fn non_revision_like_insertions_can_be_skipped() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");
        let options = MicroEpisodeOptions {
            include_non_revision_like: false,
            ..MicroEpisodeOptions::default()
        };

        let report = build_micro_episodes_with_options(&events, &options)
            .expect("simple typing builds with skip option");

        assert!(report.episodes.is_empty());
        assert_eq!(report.skipped_event_count, 6);
    }

    #[test]
    fn micro_episode_id_is_deterministic() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");

        let first = build_micro_episodes(&events).expect("first run succeeds");
        let second = build_micro_episodes(&events).expect("second run succeeds");

        let first_ids = first
            .episodes
            .iter()
            .map(|episode| episode.micro_episode_id.as_str())
            .collect::<Vec<_>>();
        let second_ids = second
            .episodes
            .iter()
            .map(|episode| episode.micro_episode_id.as_str())
            .collect::<Vec<_>>();

        assert_eq!(first_ids, second_ids);
        assert!(first_ids.contains(&"synthetic_session_002:micro:2"));
    }

    #[test]
    fn local_context_before_uses_expected_char_window() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");
        let options = MicroEpisodeOptions {
            context_window_chars: 2,
            ..MicroEpisodeOptions::default()
        };

        let report = build_micro_episodes_with_options(&events, &options)
            .expect("deletion fixture builds episodes");
        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.revision_kind == RevisionEventKind::Deletion)
            .expect("deletion micro episode exists");

        assert_eq!(episode.local_context_before.text, "kes ");
        assert_eq!(episode.local_context_before.window_start, 4);
        assert_eq!(episode.local_context_before.window_end, 8);
    }

    #[test]
    fn local_context_after_observed_is_retained() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");

        let report = build_micro_episodes(&events).expect("deletion fixture builds episodes");
        let episode = report
            .episodes
            .iter()
            .find(|episode| episode.revision_kind == RevisionEventKind::Deletion)
            .expect("deletion micro episode exists");

        assert_eq!(episode.local_context_after_observed.text, "I like music.");
    }

    #[test]
    fn replay_impossible_input_returns_error_without_panic() {
        let mut events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");
        events[0].doc_len_before = Some(99);

        let err = build_micro_episodes(&events)
            .expect_err("replay-impossible input should return an error");

        assert!(matches!(err, MicroEpisodeConstructionError::Extraction(_)));
    }

    #[test]
    fn malformed_json_test_path_does_not_panic() {
        let parsed = serde_json::from_str::<RawEvent>("{not-json");

        assert!(parsed.is_err());
    }
}
