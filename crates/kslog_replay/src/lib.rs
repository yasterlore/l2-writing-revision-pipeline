//! Deterministic text replay for validated raw keystroke event sequences.
//!
//! This crate reconstructs document state from `RawEvent` values. It does not
//! extract revision events or construct micro-episodes.

pub mod utf16_offsets;

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
};

use kslog_schema::{EventType, RawEvent};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplayOptions {
    pub verify_hashes: bool,
}

impl Default for ReplayOptions {
    fn default() -> Self {
        Self {
            verify_hashes: true,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplayState {
    text: String,
    cursor_pos: usize,
}

impl ReplayState {
    pub fn new() -> Self {
        Self {
            text: String::new(),
            cursor_pos: 0,
        }
    }

    pub fn text(&self) -> &str {
        &self.text
    }

    pub fn cursor_pos(&self) -> usize {
        self.cursor_pos
    }

    pub fn char_len(&self) -> usize {
        char_count(&self.text)
    }
}

impl Default for ReplayState {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplayReport {
    pub final_text: String,
    pub event_count: usize,
    pub final_cursor_pos: usize,
    pub final_doc_len: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplayDiagnosticReport {
    pub replay_status: ReplayDiagnosticStatus,
    pub event_count: usize,
    pub failure_line: Option<usize>,
    pub failure_kind: Option<ReplayDiagnosticFailureKind>,
    pub source_seq: Option<u64>,
    pub event_type: Option<EventType>,
    pub input_type: Option<String>,
    pub doc_len_before: Option<u32>,
    pub doc_len_after: Option<u32>,
    pub cursor_pos_before: Option<u32>,
    pub cursor_pos_after: Option<u32>,
    pub selection_start_before: Option<u32>,
    pub selection_end_before: Option<u32>,
    pub selection_start_after: Option<u32>,
    pub selection_end_after: Option<u32>,
    pub inserted_text_present: Option<bool>,
    pub inserted_text_len: Option<usize>,
    pub deleted_text_present: Option<bool>,
    pub deleted_text_len: Option<usize>,
    pub diff_op: Option<String>,
    pub quality_flags: Vec<String>,
    pub content_suppressed: bool,
    pub probable_layer: ReplayDiagnosticProbableLayer,
    pub suggested_next_check: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReplayDiagnosticStatus {
    Ok,
    Failed,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReplayDiagnosticFailureKind {
    DocLenBeforeMismatch,
    DocLenAfterMismatch,
    TextHashBeforeMismatch,
    TextHashAfterMismatch,
    CursorOutOfBounds,
    SelectionOutOfBounds,
    SelectionRangeInverted,
    AmbiguousEditLocation,
    DeletedTextMismatch,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReplayDiagnosticProbableLayer {
    LoggerDiffEstimation,
    CursorOrSelectionCapture,
    ReplayAssumption,
    SchemaOrValidation,
    Unknown,
}

pub type ReplayResult<T> = Result<T, ReplayError>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplayError {
    pub event_index: usize,
    pub seq: Option<u64>,
    pub kind: ReplayErrorKind,
}

impl ReplayError {
    fn new(event_index: usize, event: &RawEvent, kind: ReplayErrorKind) -> Self {
        Self {
            event_index,
            seq: Some(event.seq),
            kind,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReplayErrorKind {
    DocLenBeforeMismatch {
        expected: usize,
        actual: usize,
    },
    DocLenAfterMismatch {
        expected: usize,
        actual: usize,
    },
    TextHashBeforeMismatch {
        expected: String,
        actual: String,
    },
    TextHashAfterMismatch {
        expected: String,
        actual: String,
    },
    CursorOutOfBounds {
        cursor: usize,
        doc_len: usize,
    },
    SelectionOutOfBounds {
        start: usize,
        end: usize,
        doc_len: usize,
    },
    SelectionRangeInverted {
        start: usize,
        end: usize,
    },
    AmbiguousEditLocation,
    DeletedTextMismatch {
        expected: String,
        actual: String,
    },
}

impl Display for ReplayError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self.seq {
            Some(seq) => write!(
                formatter,
                "event index {}, seq {}: {}",
                self.event_index, seq, self.kind
            ),
            None => write!(formatter, "event index {}: {}", self.event_index, self.kind),
        }
    }
}

impl Error for ReplayError {}

impl Display for ReplayErrorKind {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::DocLenBeforeMismatch { expected, actual } => write!(
                formatter,
                "doc_len_before mismatch: expected {expected}, got {actual}"
            ),
            Self::DocLenAfterMismatch { expected, actual } => write!(
                formatter,
                "doc_len_after mismatch: expected {expected}, got {actual}"
            ),
            Self::TextHashBeforeMismatch { expected, actual } => write!(
                formatter,
                "text_hash_before mismatch: expected {expected}, got {actual}"
            ),
            Self::TextHashAfterMismatch { expected, actual } => write!(
                formatter,
                "text_hash_after mismatch: expected {expected}, got {actual}"
            ),
            Self::CursorOutOfBounds { cursor, doc_len } => {
                write!(formatter, "cursor out of bounds: {cursor} > {doc_len}")
            }
            Self::SelectionOutOfBounds {
                start,
                end,
                doc_len,
            } => write!(
                formatter,
                "selection out of bounds: {start}..{end} exceeds doc length {doc_len}"
            ),
            Self::SelectionRangeInverted { start, end } => {
                write!(formatter, "selection start exceeds end: {start} > {end}")
            }
            Self::AmbiguousEditLocation => write!(formatter, "ambiguous edit location"),
            Self::DeletedTextMismatch { expected, actual } => write!(
                formatter,
                "deleted text mismatch: expected {expected:?}, got {actual:?}"
            ),
        }
    }
}

pub fn replay_events(events: &[RawEvent]) -> ReplayResult<ReplayReport> {
    replay_events_with_options(events, &ReplayOptions::default())
}

pub fn diagnose_replay_events(events: &[RawEvent]) -> ReplayDiagnosticReport {
    match replay_events(events) {
        Ok(report) => ReplayDiagnosticReport {
            replay_status: ReplayDiagnosticStatus::Ok,
            event_count: report.event_count,
            failure_line: None,
            failure_kind: None,
            source_seq: None,
            event_type: None,
            input_type: None,
            doc_len_before: None,
            doc_len_after: None,
            cursor_pos_before: None,
            cursor_pos_after: None,
            selection_start_before: None,
            selection_end_before: None,
            selection_start_after: None,
            selection_end_after: None,
            inserted_text_present: None,
            inserted_text_len: None,
            deleted_text_present: None,
            deleted_text_len: None,
            diff_op: None,
            quality_flags: vec![],
            content_suppressed: true,
            probable_layer: ReplayDiagnosticProbableLayer::Unknown,
            suggested_next_check:
                "No replay mismatch was detected. Continue with extraction or micro-episode checks."
                    .to_string(),
        },
        Err(error) => diagnostic_from_error(events, &error),
    }
}

fn diagnostic_from_error(events: &[RawEvent], error: &ReplayError) -> ReplayDiagnosticReport {
    let event = events.get(error.event_index);
    ReplayDiagnosticReport {
        replay_status: ReplayDiagnosticStatus::Failed,
        event_count: events.len(),
        failure_line: Some(error.event_index + 1),
        failure_kind: Some(failure_kind_name(&error.kind)),
        source_seq: event.map(|event| event.seq).or(error.seq),
        event_type: event.map(|event| event.event_type.clone()),
        input_type: event
            .and_then(|event| event.input_type.as_ref())
            .map(debug_name),
        doc_len_before: event.and_then(|event| event.doc_len_before),
        doc_len_after: event.and_then(|event| event.doc_len_after),
        cursor_pos_before: event.and_then(|event| event.cursor_pos_before),
        cursor_pos_after: event.and_then(|event| event.cursor_pos_after),
        selection_start_before: event.and_then(|event| event.selection_start_before),
        selection_end_before: event.and_then(|event| event.selection_end_before),
        selection_start_after: event.and_then(|event| event.selection_start_after),
        selection_end_after: event.and_then(|event| event.selection_end_after),
        inserted_text_present: event.map(|event| event.inserted_text.is_some()),
        inserted_text_len: event.map(|event| text_len(event.inserted_text.as_deref())),
        deleted_text_present: event.map(|event| event.deleted_text.is_some()),
        deleted_text_len: event.map(|event| text_len(event.deleted_text.as_deref())),
        diff_op: event
            .and_then(|event| event.diff_op.as_ref())
            .map(debug_name),
        quality_flags: event
            .map(|event| event.quality_flags.clone())
            .unwrap_or_default(),
        content_suppressed: true,
        probable_layer: probable_layer(&error.kind, event),
        suggested_next_check: suggested_next_check(&error.kind, event),
    }
}

fn failure_kind_name(kind: &ReplayErrorKind) -> ReplayDiagnosticFailureKind {
    match kind {
        ReplayErrorKind::DocLenBeforeMismatch { .. } => {
            ReplayDiagnosticFailureKind::DocLenBeforeMismatch
        }
        ReplayErrorKind::DocLenAfterMismatch { .. } => {
            ReplayDiagnosticFailureKind::DocLenAfterMismatch
        }
        ReplayErrorKind::TextHashBeforeMismatch { .. } => {
            ReplayDiagnosticFailureKind::TextHashBeforeMismatch
        }
        ReplayErrorKind::TextHashAfterMismatch { .. } => {
            ReplayDiagnosticFailureKind::TextHashAfterMismatch
        }
        ReplayErrorKind::CursorOutOfBounds { .. } => ReplayDiagnosticFailureKind::CursorOutOfBounds,
        ReplayErrorKind::SelectionOutOfBounds { .. } => {
            ReplayDiagnosticFailureKind::SelectionOutOfBounds
        }
        ReplayErrorKind::SelectionRangeInverted { .. } => {
            ReplayDiagnosticFailureKind::SelectionRangeInverted
        }
        ReplayErrorKind::AmbiguousEditLocation => {
            ReplayDiagnosticFailureKind::AmbiguousEditLocation
        }
        ReplayErrorKind::DeletedTextMismatch { .. } => {
            ReplayDiagnosticFailureKind::DeletedTextMismatch
        }
    }
}

fn probable_layer(
    kind: &ReplayErrorKind,
    event: Option<&RawEvent>,
) -> ReplayDiagnosticProbableLayer {
    match kind {
        ReplayErrorKind::DeletedTextMismatch { .. } => {
            ReplayDiagnosticProbableLayer::LoggerDiffEstimation
        }
        ReplayErrorKind::CursorOutOfBounds { .. }
        | ReplayErrorKind::SelectionOutOfBounds { .. }
        | ReplayErrorKind::SelectionRangeInverted { .. }
        | ReplayErrorKind::AmbiguousEditLocation => {
            ReplayDiagnosticProbableLayer::CursorOrSelectionCapture
        }
        ReplayErrorKind::DocLenBeforeMismatch { .. }
        | ReplayErrorKind::DocLenAfterMismatch { .. } => {
            if event_has_text_change(event) {
                ReplayDiagnosticProbableLayer::LoggerDiffEstimation
            } else {
                ReplayDiagnosticProbableLayer::ReplayAssumption
            }
        }
        ReplayErrorKind::TextHashBeforeMismatch { .. }
        | ReplayErrorKind::TextHashAfterMismatch { .. } => {
            ReplayDiagnosticProbableLayer::SchemaOrValidation
        }
    }
}

fn suggested_next_check(kind: &ReplayErrorKind, event: Option<&RawEvent>) -> String {
    match probable_layer(kind, event) {
        ReplayDiagnosticProbableLayer::LoggerDiffEstimation => {
            "Check synthetic-only logger diff inference for inserted/deleted text lengths and edit range metadata.".to_string()
        }
        ReplayDiagnosticProbableLayer::CursorOrSelectionCapture => {
            "Check synthetic-only cursor and selection capture before and after the failing event.".to_string()
        }
        ReplayDiagnosticProbableLayer::ReplayAssumption => {
            "Check whether the strict Rust replay assumption covers this schema-valid browser event pattern.".to_string()
        }
        ReplayDiagnosticProbableLayer::SchemaOrValidation => {
            "Check schema, validation, and hash policy before changing replay behavior.".to_string()
        }
        ReplayDiagnosticProbableLayer::Unknown => {
            "Check the failing event metadata with content suppressed.".to_string()
        }
    }
}

fn event_has_text_change(event: Option<&RawEvent>) -> bool {
    event
        .map(|event| event.inserted_text.is_some() || event.deleted_text.is_some())
        .unwrap_or(false)
}

fn text_len(text: Option<&str>) -> usize {
    text.map(char_count).unwrap_or(0)
}

fn debug_name<T: fmt::Debug>(value: &T) -> String {
    format!("{value:?}")
}

pub fn replay_events_with_options(
    events: &[RawEvent],
    options: &ReplayOptions,
) -> ReplayResult<ReplayReport> {
    let mut state = ReplayState::new();

    for (event_index, event) in events.iter().enumerate() {
        replay_one_event(&mut state, event, event_index, options)?;
    }

    let final_doc_len = state.char_len();
    Ok(ReplayReport {
        final_text: state.text,
        event_count: events.len(),
        final_cursor_pos: state.cursor_pos,
        final_doc_len,
    })
}

fn replay_one_event(
    state: &mut ReplayState,
    event: &RawEvent,
    event_index: usize,
    options: &ReplayOptions,
) -> ReplayResult<()> {
    let current_len = state.char_len();

    if let Some(doc_len_before) = event.doc_len_before {
        let doc_len_before = doc_len_before as usize;
        if doc_len_before != current_len {
            return Err(ReplayError::new(
                event_index,
                event,
                ReplayErrorKind::DocLenBeforeMismatch {
                    expected: current_len,
                    actual: doc_len_before,
                },
            ));
        }
    }

    if options.verify_hashes {
        check_hash_before(state, event, event_index)?;
    }

    apply_event(state, event, event_index)?;

    let updated_len = state.char_len();
    if let Some(doc_len_after) = event.doc_len_after {
        let doc_len_after = doc_len_after as usize;
        if doc_len_after != updated_len {
            return Err(ReplayError::new(
                event_index,
                event,
                ReplayErrorKind::DocLenAfterMismatch {
                    expected: updated_len,
                    actual: doc_len_after,
                },
            ));
        }
    }

    if options.verify_hashes {
        check_hash_after(state, event, event_index)?;
    }

    if let Some(cursor_pos_after) = event.cursor_pos_after {
        state.cursor_pos = cursor_pos_after as usize;
    }

    Ok(())
}

fn apply_event(state: &mut ReplayState, event: &RawEvent, event_index: usize) -> ReplayResult<()> {
    if matches!(
        event.event_type,
        EventType::CompositionStart | EventType::CompositionUpdate
    ) {
        return Ok(());
    }

    match (&event.inserted_text, &event.deleted_text) {
        (None, None) => Ok(()),
        (Some(inserted_text), None) => {
            let (start, end) = edit_range_for_insert_or_replace(state, event, event_index)?;
            replace_range(state, event, event_index, start, end, inserted_text)
        }
        (None, Some(deleted_text)) => {
            let (start, end) = edit_range_for_delete(state, event, event_index, deleted_text)?;
            check_deleted_text(state, event, event_index, start, end, deleted_text)?;
            replace_range(state, event, event_index, start, end, "")
        }
        (Some(inserted_text), Some(deleted_text)) => {
            let (start, end) = edit_range_for_insert_or_replace(state, event, event_index)?;
            check_deleted_text(state, event, event_index, start, end, deleted_text)?;
            replace_range(state, event, event_index, start, end, inserted_text)
        }
    }
}

fn edit_range_for_insert_or_replace(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
) -> ReplayResult<(usize, usize)> {
    if let Some(range) = selection_range_before(state, event, event_index)? {
        return Ok(range);
    }

    let cursor = event
        .cursor_pos_before
        .map(|cursor| cursor as usize)
        .ok_or_else(|| {
            ReplayError::new(event_index, event, ReplayErrorKind::AmbiguousEditLocation)
        })?;
    ensure_cursor_in_bounds(state, event, event_index, cursor)?;
    Ok((cursor, cursor))
}

fn edit_range_for_delete(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
    deleted_text: &str,
) -> ReplayResult<(usize, usize)> {
    if let Some(range) = selection_range_before(state, event, event_index)? {
        return Ok(range);
    }

    if let (Some(cursor_before), Some(cursor_after)) =
        (event.cursor_pos_before, event.cursor_pos_after)
    {
        let start = cursor_after as usize;
        let end = cursor_before as usize;
        ensure_range_in_bounds(state, event, event_index, start, end)?;
        return Ok((start, end));
    }

    let cursor = event
        .cursor_pos_before
        .map(|cursor| cursor as usize)
        .ok_or_else(|| {
            ReplayError::new(event_index, event, ReplayErrorKind::AmbiguousEditLocation)
        })?;
    ensure_cursor_in_bounds(state, event, event_index, cursor)?;

    let deleted_len = char_count(deleted_text);
    let start = cursor.checked_sub(deleted_len).ok_or_else(|| {
        ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::CursorOutOfBounds {
                cursor,
                doc_len: state.char_len(),
            },
        )
    })?;

    ensure_range_in_bounds(state, event, event_index, start, cursor)?;
    Ok((start, cursor))
}

fn selection_range_before(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
) -> ReplayResult<Option<(usize, usize)>> {
    match (event.selection_start_before, event.selection_end_before) {
        (Some(start), Some(end)) => {
            let start = start as usize;
            let end = end as usize;
            ensure_range_in_bounds(state, event, event_index, start, end)?;
            Ok(Some((start, end)))
        }
        (None, None) => Ok(None),
        _ => Err(ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::AmbiguousEditLocation,
        )),
    }
}

fn ensure_cursor_in_bounds(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
    cursor: usize,
) -> ReplayResult<()> {
    let doc_len = state.char_len();
    if cursor > doc_len {
        return Err(ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::CursorOutOfBounds { cursor, doc_len },
        ));
    }
    Ok(())
}

fn ensure_range_in_bounds(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
    start: usize,
    end: usize,
) -> ReplayResult<()> {
    if start > end {
        return Err(ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::SelectionRangeInverted { start, end },
        ));
    }

    let doc_len = state.char_len();
    if end > doc_len {
        return Err(ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::SelectionOutOfBounds {
                start,
                end,
                doc_len,
            },
        ));
    }

    Ok(())
}

fn check_deleted_text(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
    start: usize,
    end: usize,
    deleted_text: &str,
) -> ReplayResult<()> {
    let actual = slice_chars(&state.text, start, end);
    if actual != deleted_text {
        return Err(ReplayError::new(
            event_index,
            event,
            ReplayErrorKind::DeletedTextMismatch {
                expected: deleted_text.to_string(),
                actual,
            },
        ));
    }
    Ok(())
}

fn replace_range(
    state: &mut ReplayState,
    event: &RawEvent,
    event_index: usize,
    start: usize,
    end: usize,
    inserted_text: &str,
) -> ReplayResult<()> {
    ensure_range_in_bounds(state, event, event_index, start, end)?;

    let start_byte = char_to_byte_index(&state.text, start);
    let end_byte = char_to_byte_index(&state.text, end);
    state
        .text
        .replace_range(start_byte..end_byte, inserted_text);
    state.cursor_pos = start + char_count(inserted_text);
    Ok(())
}

fn check_hash_before(
    state: &ReplayState,
    event: &RawEvent,
    event_index: usize,
) -> ReplayResult<()> {
    if let Some(expected) = event.text_hash_before.as_deref() {
        if should_verify_hash(expected) {
            let actual = deterministic_text_hash(&state.text);
            if expected != actual {
                return Err(ReplayError::new(
                    event_index,
                    event,
                    ReplayErrorKind::TextHashBeforeMismatch {
                        expected: expected.to_string(),
                        actual,
                    },
                ));
            }
        }
    }
    Ok(())
}

fn check_hash_after(state: &ReplayState, event: &RawEvent, event_index: usize) -> ReplayResult<()> {
    if let Some(expected) = event.text_hash_after.as_deref() {
        if should_verify_hash(expected) {
            let actual = deterministic_text_hash(&state.text);
            if expected != actual {
                return Err(ReplayError::new(
                    event_index,
                    event,
                    ReplayErrorKind::TextHashAfterMismatch {
                        expected: expected.to_string(),
                        actual,
                    },
                ));
            }
        }
    }
    Ok(())
}

fn should_verify_hash(hash: &str) -> bool {
    !(hash.is_empty()
        || hash.starts_with("synthetic_hash")
        || hash.starts_with("placeholder")
        || hash.starts_with("synthetic-placeholder"))
}

fn deterministic_text_hash(text: &str) -> String {
    let mut hash = 0xcbf29ce484222325_u64;
    for byte in text.as_bytes() {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    format!("kslog_fnv1a64:{hash:016x}")
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
        diagnose_replay_events, replay_events, ReplayDiagnosticFailureKind,
        ReplayDiagnosticProbableLayer, ReplayDiagnosticStatus, ReplayErrorKind,
    };
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

    fn synthetic_event(seq: u64, doc_len_before: u32, doc_len_after: u32) -> RawEvent {
        RawEvent {
            logger_schema_version: "kslog.raw_event.v1".to_string(),
            session_id: "synthetic_session_inline".to_string(),
            participant_local_id: "synthetic_writer_inline".to_string(),
            task_id: "synthetic_task_inline".to_string(),
            prompt_id: "synthetic_prompt_inline".to_string(),
            seq,
            timestamp_ms: 1_700_000_005_000 + seq,
            event_type: EventType::Input,
            input_type: Some(InputType::InsertText),
            is_composing: false,
            composition_id: None,
            selection_start_before: None,
            selection_end_before: None,
            selection_start_after: None,
            selection_end_after: None,
            cursor_pos_before: Some(doc_len_before),
            cursor_pos_after: Some(doc_len_after),
            doc_len_before: Some(doc_len_before),
            doc_len_after: Some(doc_len_after),
            inserted_text: Some("x".to_string()),
            deleted_text: None,
            text_hash_before: None,
            text_hash_after: None,
            diff_op: Some(DiffOp::Insert),
            quality_flags: vec![],
        }
    }

    #[test]
    fn replays_simple_typing_fixture() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");

        let report = replay_events(&events).expect("simple typing should replay");

        assert_eq!(report.final_text, "I like music.");
        assert_eq!(report.final_doc_len, 13);
    }

    #[test]
    fn diagnose_replay_success_suppresses_content() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl");

        let report = diagnose_replay_events(&events);

        assert_eq!(report.replay_status, ReplayDiagnosticStatus::Ok);
        assert_eq!(report.event_count, 6);
        assert_eq!(report.failure_kind, None);
        assert!(report.content_suppressed);
    }

    #[test]
    fn replays_deletion_fixture() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl");

        let report = replay_events(&events).expect("deletion case should replay");

        assert_eq!(report.final_text, "I like music.");
    }

    #[test]
    fn replays_replacement_fixture() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/replacement_case.jsonl");

        let report = replay_events(&events).expect("replacement case should replay");

        assert_eq!(report.final_text, "I go to school.");
    }

    #[test]
    fn replays_selection_edit_fixture() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/selection_edit_case.jsonl",
        );

        let report = replay_events(&events).expect("selection edit case should replay");

        assert_eq!(report.final_text, "I enjoy music.");
    }

    #[test]
    fn replays_paste_fixture() {
        let events =
            read_valid_fixture("tests/fixtures/synthetic/raw_events/valid/paste_case.jsonl");

        let report = replay_events(&events).expect("paste case should replay");

        assert_eq!(report.final_text, "synthetic note");
    }

    #[test]
    fn replays_cursor_movement_fixture() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/cursor_movement_case.jsonl",
        );

        let report = replay_events(&events).expect("cursor movement case should replay");

        assert_eq!(report.final_text, "I like music.");
    }

    #[test]
    fn replays_minimal_ime_fixture() {
        let events = read_valid_fixture(
            "tests/fixtures/synthetic/raw_events/valid/ime_composition_case.jsonl",
        );

        let report = replay_events(&events).expect("IME case should replay minimally");

        assert_eq!(report.final_text, "ime_token");
    }

    #[test]
    fn doc_len_before_mismatch_returns_error() {
        let event = synthetic_event(1, 1, 2);

        let err = replay_events(&[event]).expect_err("doc_len_before mismatch should fail");

        assert!(matches!(
            err.kind,
            ReplayErrorKind::DocLenBeforeMismatch {
                expected: 0,
                actual: 1
            }
        ));
    }

    #[test]
    fn doc_len_after_mismatch_returns_error() {
        let mut event = synthetic_event(1, 0, 2);
        event.cursor_pos_before = Some(0);

        let err = replay_events(&[event]).expect_err("doc_len_after mismatch should fail");

        assert!(matches!(
            err.kind,
            ReplayErrorKind::DocLenAfterMismatch {
                expected: 1,
                actual: 2
            }
        ));
    }

    #[test]
    fn cursor_out_of_bounds_returns_error() {
        let mut event = synthetic_event(1, 0, 1);
        event.cursor_pos_before = Some(4);
        event.doc_len_before = Some(0);

        let err = replay_events(&[event]).expect_err("cursor out of bounds should fail");

        assert!(matches!(
            err.kind,
            ReplayErrorKind::CursorOutOfBounds {
                cursor: 4,
                doc_len: 0
            }
        ));
    }

    #[test]
    fn selection_out_of_bounds_returns_error() {
        let mut event = synthetic_event(1, 0, 1);
        event.cursor_pos_before = None;
        event.selection_start_before = Some(0);
        event.selection_end_before = Some(4);
        event.doc_len_before = Some(0);

        let err = replay_events(&[event]).expect_err("selection out of bounds should fail");

        assert!(matches!(
            err.kind,
            ReplayErrorKind::SelectionOutOfBounds {
                start: 0,
                end: 4,
                doc_len: 0
            }
        ));
    }

    #[test]
    fn malformed_input_does_not_panic_in_replay_test_path() {
        let malformed = "{not-json";

        let parsed = serde_json::from_str::<RawEvent>(malformed);

        assert!(parsed.is_err());
    }

    #[test]
    fn diagnose_replay_deleted_text_mismatch_uses_lengths_only() {
        let mut insert = synthetic_event(1, 0, 1);
        insert.inserted_text = Some("x".to_string());
        insert.cursor_pos_before = Some(0);
        insert.cursor_pos_after = Some(1);

        let mut delete = synthetic_event(2, 1, 0);
        delete.inserted_text = None;
        delete.deleted_text = Some("LEAK_MARKER_SHOULD_NOT_APPEAR".to_string());
        delete.cursor_pos_before = Some(1);
        delete.cursor_pos_after = Some(0);
        delete.doc_len_before = Some(1);
        delete.doc_len_after = Some(0);
        delete.diff_op = Some(DiffOp::Delete);

        let report = diagnose_replay_events(&[insert, delete]);

        assert_eq!(report.replay_status, ReplayDiagnosticStatus::Failed);
        assert_eq!(
            report.failure_kind,
            Some(ReplayDiagnosticFailureKind::DeletedTextMismatch)
        );
        assert_eq!(
            report.probable_layer,
            ReplayDiagnosticProbableLayer::LoggerDiffEstimation
        );
        assert_eq!(report.deleted_text_present, Some(true));
        assert_eq!(
            report.deleted_text_len,
            Some("LEAK_MARKER_SHOULD_NOT_APPEAR".chars().count())
        );
        assert!(report.content_suppressed);
    }
}
