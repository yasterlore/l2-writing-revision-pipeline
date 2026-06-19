//! Initial revision-event extraction from raw keystroke event sequences.
//!
//! This crate describes observed editing actions. It does not assign gold
//! labels, rank candidates, or construct micro-episodes.

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
};

use kslog_replay::{replay_events, ReplayError};
use kslog_schema::{EventType, InputType, RawEvent};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RevisionSpan {
    pub start: u32,
    pub end: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RevisionEventKind {
    Insertion,
    Deletion,
    Replacement,
    SelectionRangeEdit,
    Paste,
    CompositionCommit,
    Unsupported,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RevisionEvent {
    pub revision_event_id: String,
    pub session_id: String,
    pub task_id: String,
    pub prompt_id: String,
    pub source_seq: u64,
    pub timestamp_ms: u64,
    pub kind: RevisionEventKind,
    pub span: Option<RevisionSpan>,
    pub inserted_text: Option<String>,
    pub deleted_text: Option<String>,
    pub cursor_pos_before: Option<u32>,
    pub cursor_pos_after: Option<u32>,
    pub doc_len_before: Option<u32>,
    pub doc_len_after: Option<u32>,
    pub is_revision_like: bool,
    pub quality_flags: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RevisionExtractionReport {
    pub events: Vec<RevisionEvent>,
    pub source_event_count: usize,
    pub unsupported_event_count: usize,
}

pub type RevisionExtractionResult<T> = Result<T, RevisionExtractionError>;

#[derive(Debug)]
pub enum RevisionExtractionError {
    Replay(ReplayError),
    InvalidSpan {
        source_seq: u64,
        start: u32,
        end: u32,
    },
    AmbiguousEdit {
        source_seq: u64,
        reason: String,
    },
}

impl Display for RevisionExtractionError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::Replay(error) => write!(formatter, "replay failed before extraction: {error}"),
            Self::InvalidSpan {
                source_seq,
                start,
                end,
            } => write!(
                formatter,
                "invalid revision span at seq {source_seq}: {start} > {end}"
            ),
            Self::AmbiguousEdit { source_seq, reason } => {
                write!(formatter, "ambiguous edit at seq {source_seq}: {reason}")
            }
        }
    }
}

impl Error for RevisionExtractionError {}

impl From<ReplayError> for RevisionExtractionError {
    fn from(error: ReplayError) -> Self {
        Self::Replay(error)
    }
}

pub fn extract_revision_events(
    events: &[RawEvent],
) -> RevisionExtractionResult<RevisionExtractionReport> {
    replay_events(events)?;

    let mut revision_events = Vec::new();
    let mut unsupported_event_count = 0;

    for event in events {
        let revision_event = classify_event(event)?;
        if revision_event.kind == RevisionEventKind::Unsupported {
            unsupported_event_count += 1;
        }
        revision_events.push(revision_event);
    }

    Ok(RevisionExtractionReport {
        events: revision_events,
        source_event_count: events.len(),
        unsupported_event_count,
    })
}

fn classify_event(event: &RawEvent) -> RevisionExtractionResult<RevisionEvent> {
    let kind = classify_kind(event);
    let is_revision_like = is_revision_like(event, &kind);
    let span = span_for_event(event, &kind)?;

    Ok(RevisionEvent {
        revision_event_id: format!("{}:{}", event.session_id, event.seq),
        session_id: event.session_id.clone(),
        task_id: event.task_id.clone(),
        prompt_id: event.prompt_id.clone(),
        source_seq: event.seq,
        timestamp_ms: event.timestamp_ms,
        kind,
        span,
        inserted_text: event.inserted_text.clone(),
        deleted_text: event.deleted_text.clone(),
        cursor_pos_before: event.cursor_pos_before,
        cursor_pos_after: event.cursor_pos_after,
        doc_len_before: event.doc_len_before,
        doc_len_after: event.doc_len_after,
        is_revision_like,
        quality_flags: event.quality_flags.clone(),
    })
}

fn classify_kind(event: &RawEvent) -> RevisionEventKind {
    if is_composition_commit(event) {
        return RevisionEventKind::CompositionCommit;
    }

    if is_paste(event) {
        return RevisionEventKind::Paste;
    }

    if has_non_collapsed_selection(event) && has_text_edit(event) {
        return RevisionEventKind::SelectionRangeEdit;
    }

    match (&event.inserted_text, &event.deleted_text) {
        (Some(_), Some(_)) => RevisionEventKind::Replacement,
        (None, Some(_)) => RevisionEventKind::Deletion,
        (Some(_), None) => RevisionEventKind::Insertion,
        (None, None) => RevisionEventKind::Unsupported,
    }
}

fn is_revision_like(event: &RawEvent, kind: &RevisionEventKind) -> bool {
    match kind {
        RevisionEventKind::Insertion => {
            has_non_collapsed_selection(event) || is_cursor_local(event)
        }
        RevisionEventKind::Deletion
        | RevisionEventKind::Replacement
        | RevisionEventKind::SelectionRangeEdit
        | RevisionEventKind::Paste
        | RevisionEventKind::CompositionCommit => true,
        RevisionEventKind::Unsupported => false,
    }
}

fn span_for_event(
    event: &RawEvent,
    kind: &RevisionEventKind,
) -> RevisionExtractionResult<Option<RevisionSpan>> {
    match kind {
        RevisionEventKind::Unsupported => Ok(None),
        RevisionEventKind::Insertion
        | RevisionEventKind::Paste
        | RevisionEventKind::CompositionCommit => insertion_span(event),
        RevisionEventKind::Deletion => deletion_span(event),
        RevisionEventKind::Replacement | RevisionEventKind::SelectionRangeEdit => {
            replacement_span(event)
        }
    }
}

fn insertion_span(event: &RawEvent) -> RevisionExtractionResult<Option<RevisionSpan>> {
    if let Some(span) = selection_span(event)? {
        return Ok(Some(span));
    }

    let cursor = event
        .cursor_pos_before
        .or(event.cursor_pos_after)
        .ok_or_else(|| RevisionExtractionError::AmbiguousEdit {
            source_seq: event.seq,
            reason: "insertion has no cursor or selection position".to_string(),
        })?;

    Ok(Some(RevisionSpan {
        start: cursor,
        end: cursor,
    }))
}

fn deletion_span(event: &RawEvent) -> RevisionExtractionResult<Option<RevisionSpan>> {
    if let Some(span) = selection_span(event)? {
        return Ok(Some(span));
    }

    match (event.cursor_pos_after, event.cursor_pos_before) {
        (Some(start), Some(end)) => make_span(event, start, end).map(Some),
        _ => {
            let end =
                event
                    .cursor_pos_before
                    .ok_or_else(|| RevisionExtractionError::AmbiguousEdit {
                        source_seq: event.seq,
                        reason: "deletion has no cursor or selection position".to_string(),
                    })?;
            let deleted_len = event.deleted_text.as_deref().map(char_count).unwrap_or(0) as u32;
            let start = end.checked_sub(deleted_len).ok_or_else(|| {
                RevisionExtractionError::AmbiguousEdit {
                    source_seq: event.seq,
                    reason: "deleted_text is longer than cursor_pos_before".to_string(),
                }
            })?;
            make_span(event, start, end).map(Some)
        }
    }
}

fn replacement_span(event: &RawEvent) -> RevisionExtractionResult<Option<RevisionSpan>> {
    if let Some(span) = selection_span(event)? {
        return Ok(Some(span));
    }

    if let (Some(start), Some(end)) = (event.cursor_pos_before, event.cursor_pos_after) {
        return make_span(event, start.min(end), start.max(end)).map(Some);
    }

    Err(RevisionExtractionError::AmbiguousEdit {
        source_seq: event.seq,
        reason: "replacement has no cursor or selection position".to_string(),
    })
}

fn selection_span(event: &RawEvent) -> RevisionExtractionResult<Option<RevisionSpan>> {
    match (event.selection_start_before, event.selection_end_before) {
        (Some(start), Some(end)) => make_span(event, start, end).map(Some),
        (None, None) => Ok(None),
        _ => Err(RevisionExtractionError::AmbiguousEdit {
            source_seq: event.seq,
            reason: "selection range is incomplete".to_string(),
        }),
    }
}

fn make_span(event: &RawEvent, start: u32, end: u32) -> RevisionExtractionResult<RevisionSpan> {
    if start > end {
        return Err(RevisionExtractionError::InvalidSpan {
            source_seq: event.seq,
            start,
            end,
        });
    }

    Ok(RevisionSpan { start, end })
}

fn has_non_collapsed_selection(event: &RawEvent) -> bool {
    matches!(
        (event.selection_start_before, event.selection_end_before),
        (Some(start), Some(end)) if start < end
    )
}

fn has_text_edit(event: &RawEvent) -> bool {
    event.inserted_text.is_some() || event.deleted_text.is_some()
}

fn is_cursor_local(event: &RawEvent) -> bool {
    matches!(
        (event.cursor_pos_before, event.doc_len_before),
        (Some(cursor), Some(doc_len)) if cursor < doc_len
    )
}

fn is_paste(event: &RawEvent) -> bool {
    event.event_type == EventType::Paste || event.input_type == Some(InputType::InsertFromPaste)
}

fn is_composition_commit(event: &RawEvent) -> bool {
    event.event_type == EventType::CompositionEnd && event.inserted_text.is_some()
}

fn char_count(text: &str) -> usize {
    text.chars().count()
}

#[cfg(test)]
mod tests {
    use super::{extract_revision_events, RevisionEventKind};
    use kslog_schema::{DiffOp, EventType, InputType, RawEvent};
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

    fn synthetic_event(
        seq: u64,
        event_type: EventType,
        input_type: Option<InputType>,
        before_text_len: u32,
        after_text_len: u32,
        cursor_before: u32,
        cursor_after: u32,
    ) -> RawEvent {
        RawEvent {
            logger_schema_version: "kslog.raw_event.v1".to_string(),
            session_id: "synthetic_session_extract_inline".to_string(),
            participant_local_id: "synthetic_writer_extract_inline".to_string(),
            task_id: "synthetic_task_extract_inline".to_string(),
            prompt_id: "synthetic_prompt_extract_inline".to_string(),
            seq,
            timestamp_ms: 1_700_000_020_000 + seq,
            event_type,
            input_type,
            is_composing: false,
            composition_id: None,
            selection_start_before: Some(cursor_before),
            selection_end_before: Some(cursor_before),
            selection_start_after: Some(cursor_after),
            selection_end_after: Some(cursor_after),
            cursor_pos_before: Some(cursor_before),
            cursor_pos_after: Some(cursor_after),
            doc_len_before: Some(before_text_len),
            doc_len_after: Some(after_text_len),
            inserted_text: None,
            deleted_text: None,
            text_hash_before: None,
            text_hash_after: None,
            diff_op: None,
            quality_flags: vec![],
        }
    }

    fn insert_event(seq: u64, before_text_len: u32, cursor_before: u32, text: &str) -> RawEvent {
        let inserted_len = text.chars().count() as u32;
        let mut event = synthetic_event(
            seq,
            EventType::Input,
            Some(InputType::InsertText),
            before_text_len,
            before_text_len + inserted_len,
            cursor_before,
            cursor_before + inserted_len,
        );
        event.inserted_text = Some(text.to_string());
        event.diff_op = Some(DiffOp::Insert);
        event
    }

    #[test]
    fn deletion_case_extracts_deletion() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");

        let report = extract_revision_events(&events).expect("deletion fixture extracts");

        let deletion = report
            .events
            .iter()
            .find(|event| event.kind == RevisionEventKind::Deletion)
            .expect("Deletion event exists");
        assert_eq!(deletion.deleted_text.as_deref(), Some("s"));
        assert!(deletion.is_revision_like);
    }

    #[test]
    fn replacement_fixture_with_selection_prioritizes_selection_range_edit() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/replacement_case.jsonl");

        let report = extract_revision_events(&events).expect("replacement fixture extracts");

        let replacement = report
            .events
            .iter()
            .find(|event| event.kind == RevisionEventKind::SelectionRangeEdit)
            .expect("selection-prioritized replacement event exists");
        assert_eq!(replacement.inserted_text.as_deref(), Some("go to"));
        assert_eq!(replacement.deleted_text.as_deref(), Some("go"));
        assert!(replacement.is_revision_like);
    }

    #[test]
    fn selection_edit_case_extracts_selection_range_edit() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/selection_edit_case.jsonl",
        );

        let report = extract_revision_events(&events).expect("selection edit fixture extracts");

        let selection_edit = report
            .events
            .iter()
            .find(|event| {
                matches!(
                    event.kind,
                    RevisionEventKind::SelectionRangeEdit | RevisionEventKind::Replacement
                ) && event.deleted_text.as_deref() == Some("song")
            })
            .expect("selection edit event exists");
        assert_eq!(selection_edit.inserted_text.as_deref(), Some("music"));
        assert_eq!(selection_edit.deleted_text.as_deref(), Some("song"));
        assert_eq!(
            selection_edit
                .span
                .as_ref()
                .map(|span| (span.start, span.end)),
            Some((8, 12))
        );
        assert_eq!(selection_edit.kind, RevisionEventKind::SelectionRangeEdit);
        assert!(selection_edit.is_revision_like);
    }

    #[test]
    fn selection_range_edit_is_prioritized_over_replacement() {
        let setup = insert_event(1, 0, 0, "abcd");
        let mut selection_replace =
            synthetic_event(2, EventType::Input, Some(InputType::InsertText), 4, 4, 1, 3);
        selection_replace.selection_start_before = Some(1);
        selection_replace.selection_end_before = Some(3);
        selection_replace.selection_start_after = Some(3);
        selection_replace.selection_end_after = Some(3);
        selection_replace.inserted_text = Some("XY".to_string());
        selection_replace.deleted_text = Some("bc".to_string());
        selection_replace.diff_op = Some(DiffOp::Replace);

        let report = extract_revision_events(&[setup, selection_replace])
            .expect("selection replacement should extract");
        let event = report.events.last().expect("selection event exists");

        assert_eq!(event.kind, RevisionEventKind::SelectionRangeEdit);
        assert!(event.is_revision_like);
        assert_eq!(
            event.span.as_ref().map(|span| (span.start, span.end)),
            Some((1, 3))
        );
    }

    #[test]
    fn non_terminal_cursor_insertion_is_revision_like() {
        let setup = insert_event(1, 0, 0, "abcd");
        let local_insert = insert_event(2, 4, 2, "X");

        let report =
            extract_revision_events(&[setup, local_insert]).expect("local insertion extracts");
        let event = report.events.last().expect("local insertion exists");

        assert_eq!(event.kind, RevisionEventKind::Insertion);
        assert!(event.is_revision_like);
    }

    #[test]
    fn terminal_normal_typing_remains_non_revision_like() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");

        let report = extract_revision_events(&events).expect("simple typing fixture extracts");

        assert!(report
            .events
            .iter()
            .all(|event| event.kind == RevisionEventKind::Insertion));
        assert!(report.events.iter().all(|event| !event.is_revision_like));
    }

    #[test]
    fn paste_case_extracts_paste() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/paste_case.jsonl");

        let report = extract_revision_events(&events).expect("paste fixture extracts");

        let paste = report
            .events
            .iter()
            .find(|event| event.kind == RevisionEventKind::Paste)
            .expect("Paste event exists");
        assert_eq!(paste.inserted_text.as_deref(), Some("synthetic note"));
        assert!(paste.is_revision_like);
    }

    #[test]
    fn input_type_insert_from_paste_extracts_paste() {
        let mut paste = synthetic_event(
            1,
            EventType::Input,
            Some(InputType::InsertFromPaste),
            0,
            6,
            0,
            6,
        );
        paste.inserted_text = Some("pasted".to_string());
        paste.diff_op = Some(DiffOp::Insert);

        let report = extract_revision_events(&[paste]).expect("paste input type extracts");
        let event = report.events.first().expect("paste event exists");

        assert_eq!(event.kind, RevisionEventKind::Paste);
        assert!(event.is_revision_like);
    }

    #[test]
    fn ime_case_extracts_composition_commit() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/ime_composition_case.jsonl",
        );

        let report = extract_revision_events(&events).expect("IME fixture extracts");

        let commit = report
            .events
            .iter()
            .find(|event| event.kind == RevisionEventKind::CompositionCommit)
            .expect("CompositionCommit event exists");
        assert_eq!(commit.inserted_text.as_deref(), Some("ime_token"));
        assert!(commit.is_revision_like);
    }

    #[test]
    fn composition_end_with_inserted_text_extracts_composition_commit() {
        let mut commit = synthetic_event(1, EventType::CompositionEnd, None, 0, 3, 0, 3);
        commit.inserted_text = Some("ime".to_string());
        commit.diff_op = Some(DiffOp::Composition);

        let report = extract_revision_events(&[commit]).expect("composition commit extracts");
        let event = report.events.first().expect("composition event exists");

        assert_eq!(event.kind, RevisionEventKind::CompositionCommit);
        assert!(event.is_revision_like);
    }

    #[test]
    fn simple_typing_extracts_non_revision_like_insertions() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");

        let report = extract_revision_events(&events).expect("simple typing fixture extracts");

        assert_eq!(report.events.len(), 6);
        assert!(report
            .events
            .iter()
            .all(|event| event.kind == RevisionEventKind::Insertion));
        assert!(report.events.iter().all(|event| !event.is_revision_like));
    }

    #[test]
    fn unsupported_event_does_not_panic() {
        let mut events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");
        let mut unsupported = events[0].clone();
        unsupported.seq = 7;
        unsupported.timestamp_ms += 10;
        unsupported.event_type = EventType::Focus;
        unsupported.input_type = None;
        unsupported.inserted_text = None;
        unsupported.deleted_text = None;
        unsupported.cursor_pos_before = Some(13);
        unsupported.cursor_pos_after = Some(13);
        unsupported.doc_len_before = Some(13);
        unsupported.doc_len_after = Some(13);
        events.push(unsupported);

        let report = extract_revision_events(&events).expect("unsupported event should not panic");

        assert_eq!(report.unsupported_event_count, 1);
        assert_eq!(
            report.events.last().map(|event| &event.kind),
            Some(&RevisionEventKind::Unsupported)
        );
    }
}
