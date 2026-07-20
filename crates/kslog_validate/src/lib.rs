//! Deterministic JSONL validation for raw keystroke event logs.
//!
//! This crate validates structure, ordering, ranges, and no-oracle field policy.
//! It does not replay text or derive revision events.

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
    io::{self, BufRead, Read},
};

use kslog_schema::{
    utf16_offsets::{
        utf16_code_unit_len, utf16_code_unit_offset_to_utf8_byte_index,
        utf16_code_unit_range_to_utf8_byte_range, Utf16OffsetError,
    },
    DiffOp, PositionUnit, PositionUnitPolicyError, RawEvent,
};

pub const DEFAULT_MAX_LINE_BYTES: usize = 64 * 1024;
pub const FORBIDDEN_NO_ORACLE_FIELDS: &[&str] = &[
    "final_text",
    "observed_after_text",
    "gold_label",
    "teacher_correction",
    "teacher_corrections",
    "human_correction",
    "human_corrections",
    "post_hoc_annotation",
    "post_hoc_annotations",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EmptyLinePolicy {
    Reject,
    Ignore,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationOptions {
    pub max_line_bytes: usize,
    pub empty_line_policy: EmptyLinePolicy,
}

impl Default for ValidationOptions {
    fn default() -> Self {
        Self {
            max_line_bytes: DEFAULT_MAX_LINE_BYTES,
            empty_line_policy: EmptyLinePolicy::Reject,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationReport {
    pub event_count: usize,
    pub first_seq: Option<u64>,
    pub last_seq: Option<u64>,
    pub first_timestamp_ms: Option<u64>,
    pub last_timestamp_ms: Option<u64>,
    pub max_line_bytes: usize,
    pub empty_line_policy: EmptyLinePolicy,
}

impl ValidationReport {
    fn new(options: &ValidationOptions) -> Self {
        Self {
            event_count: 0,
            first_seq: None,
            last_seq: None,
            first_timestamp_ms: None,
            last_timestamp_ms: None,
            max_line_bytes: options.max_line_bytes,
            empty_line_policy: options.empty_line_policy,
        }
    }

    fn record_event(&mut self, event: &RawEvent) {
        if self.event_count == 0 {
            self.first_seq = Some(event.seq);
            self.first_timestamp_ms = Some(event.timestamp_ms);
        }

        self.event_count += 1;
        self.last_seq = Some(event.seq);
        self.last_timestamp_ms = Some(event.timestamp_ms);
    }
}

pub type ValidationResult<T> = Result<T, ValidationError>;

#[derive(Debug)]
pub struct ValidationError {
    pub line_number: Option<usize>,
    pub kind: ValidationErrorKind,
}

impl ValidationError {
    fn new(line_number: usize, kind: ValidationErrorKind) -> Self {
        Self {
            line_number: Some(line_number),
            kind,
        }
    }

    fn without_line(kind: ValidationErrorKind) -> Self {
        Self {
            line_number: None,
            kind,
        }
    }
}

#[derive(Debug)]
pub enum ValidationErrorKind {
    Io(String),
    LineTooLong {
        max_line_bytes: usize,
        actual_line_bytes: usize,
    },
    EmptyLine,
    MalformedJson(String),
    JsonLineIsNotObject,
    ForbiddenNoOracleField(String),
    RawEventSchema(String),
    PositionUnitPolicy(PositionUnitPolicyError),
    Utf16NumericMetadata {
        reason: Utf16NumericMetadataReason,
        field: &'static str,
    },
    SequenceGap {
        expected_seq: u64,
        actual_seq: u64,
    },
    SequenceOverflow {
        previous_seq: u64,
    },
    TimestampInversion {
        previous_timestamp_ms: u64,
        actual_timestamp_ms: u64,
    },
    CursorOutOfBounds {
        field: &'static str,
        cursor: u32,
        doc_len_field: &'static str,
        doc_len: u32,
    },
    SelectionRangeInverted {
        start_field: &'static str,
        end_field: &'static str,
        start: u32,
        end: u32,
    },
    SelectionOutOfBounds {
        field: &'static str,
        position: u32,
        doc_len_field: &'static str,
        doc_len: u32,
    },
}

impl Display for ValidationError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self.line_number {
            Some(line_number) => write!(formatter, "line {line_number}: {}", self.kind),
            None => Display::fmt(&self.kind, formatter),
        }
    }
}

impl Error for ValidationError {}

impl Display for ValidationErrorKind {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(message) => write!(formatter, "I/O error: {message}"),
            Self::LineTooLong {
                max_line_bytes,
                actual_line_bytes,
            } => write!(
                formatter,
                "line exceeds max_line_bytes ({actual_line_bytes} > {max_line_bytes})"
            ),
            Self::EmptyLine => write!(formatter, "empty JSONL lines are rejected"),
            Self::MalformedJson(message) => write!(formatter, "malformed JSON: {message}"),
            Self::JsonLineIsNotObject => write!(formatter, "JSONL line is not a JSON object"),
            Self::ForbiddenNoOracleField(field) => {
                write!(formatter, "forbidden no-oracle field present: {field}")
            }
            Self::RawEventSchema(message) => write!(formatter, "RawEvent schema error: {message}"),
            Self::PositionUnitPolicy(error) => {
                write!(
                    formatter,
                    "position_unit policy error: {}",
                    error.reason_code()
                )
            }
            Self::Utf16NumericMetadata { reason, field } => write!(
                formatter,
                "UTF-16 numeric metadata error: {} at {field}",
                reason.reason_code()
            ),
            Self::SequenceGap {
                expected_seq,
                actual_seq,
            } => write!(
                formatter,
                "seq is not consecutive: expected {expected_seq}, got {actual_seq}"
            ),
            Self::SequenceOverflow { previous_seq } => {
                write!(formatter, "seq overflow after {previous_seq}")
            }
            Self::TimestampInversion {
                previous_timestamp_ms,
                actual_timestamp_ms,
            } => write!(
                formatter,
                "timestamp_ms inverted: previous {previous_timestamp_ms}, got {actual_timestamp_ms}"
            ),
            Self::CursorOutOfBounds {
                field,
                cursor,
                doc_len_field,
                doc_len,
            } => write!(
                formatter,
                "{field} exceeds {doc_len_field}: {cursor} > {doc_len}"
            ),
            Self::SelectionRangeInverted {
                start_field,
                end_field,
                start,
                end,
            } => write!(formatter, "{start_field} > {end_field}: {start} > {end}"),
            Self::SelectionOutOfBounds {
                field,
                position,
                doc_len_field,
                doc_len,
            } => write!(
                formatter,
                "{field} exceeds {doc_len_field}: {position} > {doc_len}"
            ),
        }
    }
}

impl ValidationErrorKind {
    pub fn reason_code(&self) -> &'static str {
        match self {
            Self::Io(_) => "io_error",
            Self::LineTooLong { .. } => "line_too_long",
            Self::EmptyLine => "empty_line",
            Self::MalformedJson(_) => "malformed_json",
            Self::JsonLineIsNotObject => "json_line_is_not_object",
            Self::ForbiddenNoOracleField(_) => "forbidden_no_oracle_field",
            Self::RawEventSchema(_) => "raw_event_schema",
            Self::PositionUnitPolicy(error) => error.reason_code(),
            Self::Utf16NumericMetadata { reason, .. } => reason.reason_code(),
            Self::SequenceGap { .. } => "sequence_gap",
            Self::SequenceOverflow { .. } => "sequence_overflow",
            Self::TimestampInversion { .. } => "timestamp_inversion",
            Self::CursorOutOfBounds { .. } => "cursor_out_of_bounds",
            Self::SelectionRangeInverted { .. } => "selection_range_inverted",
            Self::SelectionOutOfBounds { .. } => "selection_out_of_bounds",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Utf16NumericMetadataReason {
    DocLenBeforeMismatch,
    DocLenAfterMismatch,
    StartGreaterThanEnd,
    OffsetBeyondUtf16Length,
    OffsetInsideSurrogatePair,
    InvalidUtf16Boundary,
}

impl Utf16NumericMetadataReason {
    pub fn reason_code(self) -> &'static str {
        match self {
            Self::DocLenBeforeMismatch => "doc_len_before_utf16_mismatch",
            Self::DocLenAfterMismatch => "doc_len_after_utf16_mismatch",
            Self::StartGreaterThanEnd => "start_greater_than_end",
            Self::OffsetBeyondUtf16Length => "offset_beyond_utf16_length",
            Self::OffsetInsideSurrogatePair => "offset_inside_surrogate_pair",
            Self::InvalidUtf16Boundary => "invalid_utf16_boundary",
        }
    }
}

impl From<io::Error> for ValidationError {
    fn from(error: io::Error) -> Self {
        Self::without_line(ValidationErrorKind::Io(error.to_string()))
    }
}

pub fn validate_jsonl_str(input: &str) -> ValidationResult<ValidationReport> {
    validate_jsonl_reader(input.as_bytes(), &ValidationOptions::default())
}

pub fn validate_jsonl_reader<R: BufRead>(
    mut reader: R,
    options: &ValidationOptions,
) -> ValidationResult<ValidationReport> {
    let mut report = ValidationReport::new(options);
    let mut expected_seq = None;
    let mut previous_timestamp_ms = None;
    let mut utf16_state = Utf16NumericMetadataState::default();
    let mut line = Vec::new();
    let mut line_number = 0;

    loop {
        line.clear();
        let bytes_read = reader
            .by_ref()
            .take(options.max_line_bytes.saturating_add(1) as u64)
            .read_until(b'\n', &mut line)?;
        if bytes_read == 0 {
            break;
        }

        line_number += 1;
        if line.len() > options.max_line_bytes {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::LineTooLong {
                    max_line_bytes: options.max_line_bytes,
                    actual_line_bytes: line.len(),
                },
            ));
        }

        let trimmed_line = trim_jsonl_newline(&line);
        if is_ascii_blank(trimmed_line) {
            match options.empty_line_policy {
                EmptyLinePolicy::Reject => {
                    return Err(ValidationError::new(
                        line_number,
                        ValidationErrorKind::EmptyLine,
                    ));
                }
                EmptyLinePolicy::Ignore => continue,
            }
        }

        let event = parse_raw_event_line(trimmed_line, line_number)?;
        validate_position_unit_policy(&event, line_number)?;
        validate_utf16_numeric_metadata(&event, &mut utf16_state, line_number)?;
        validate_sequence(&event, &mut expected_seq, line_number)?;
        validate_timestamp(&event, &mut previous_timestamp_ms, line_number)?;
        validate_cursor_ranges(&event, line_number)?;
        validate_selection_ranges(&event, line_number)?;

        report.record_event(&event);
    }

    Ok(report)
}

#[derive(Debug, Default)]
struct Utf16NumericMetadataState {
    text: Option<String>,
}

fn parse_raw_event_line(line: &[u8], line_number: usize) -> ValidationResult<RawEvent> {
    let value = serde_json::from_slice::<serde_json::Value>(line).map_err(|error| {
        ValidationError::new(
            line_number,
            ValidationErrorKind::MalformedJson(error.to_string()),
        )
    })?;

    let object = value.as_object().ok_or_else(|| {
        ValidationError::new(line_number, ValidationErrorKind::JsonLineIsNotObject)
    })?;

    for field in FORBIDDEN_NO_ORACLE_FIELDS {
        if object.contains_key(*field) {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::ForbiddenNoOracleField((*field).to_string()),
            ));
        }
    }

    serde_json::from_value::<RawEvent>(value).map_err(|error| {
        ValidationError::new(
            line_number,
            ValidationErrorKind::RawEventSchema(error.to_string()),
        )
    })
}

fn validate_position_unit_policy(event: &RawEvent, line_number: usize) -> ValidationResult<()> {
    if !event.is_web_logger_position_unit_target() {
        return Ok(());
    }

    if event.is_legacy_position_unit_missing_allowed() {
        return Ok(());
    }

    event.position_unit_policy().map(|_| ()).map_err(|error| {
        ValidationError::new(line_number, ValidationErrorKind::PositionUnitPolicy(error))
    })
}

fn validate_utf16_numeric_metadata(
    event: &RawEvent,
    state: &mut Utf16NumericMetadataState,
    line_number: usize,
) -> ValidationResult<()> {
    if !should_validate_utf16_numeric_metadata(event) {
        return Ok(());
    }

    if state.text.is_none() && event.doc_len_before == Some(0) {
        state.text = Some(String::new());
    }

    if let (Some(text), Some(doc_len_before)) = (state.text.as_deref(), event.doc_len_before) {
        if utf16_code_unit_len(text) != doc_len_before as usize {
            return Err(utf16_numeric_error(
                line_number,
                Utf16NumericMetadataReason::DocLenBeforeMismatch,
                "doc_len_before",
            ));
        }
    }

    validate_before_utf16_offsets(event, state.text.as_deref(), line_number)?;

    let after_text = compute_after_text(event, state.text.as_deref(), line_number)?;
    if let (Some(text), Some(doc_len_after)) = (after_text.as_deref(), event.doc_len_after) {
        if utf16_code_unit_len(text) != doc_len_after as usize {
            return Err(utf16_numeric_error(
                line_number,
                Utf16NumericMetadataReason::DocLenAfterMismatch,
                "doc_len_after",
            ));
        }
    } else if let (Some(expected_len), Some(doc_len_after)) = (
        expected_doc_len_after_from_metadata(event),
        event.doc_len_after,
    ) {
        if expected_len != doc_len_after as usize {
            return Err(utf16_numeric_error(
                line_number,
                Utf16NumericMetadataReason::DocLenAfterMismatch,
                "doc_len_after",
            ));
        }
    }

    validate_after_utf16_offsets(event, after_text.as_deref(), line_number)?;
    state.text = after_text;

    Ok(())
}

fn should_validate_utf16_numeric_metadata(event: &RawEvent) -> bool {
    event.is_web_logger_position_unit_target()
        && matches!(
            event.position_unit_policy(),
            Ok(PositionUnit::Utf16CodeUnit)
        )
}

fn validate_before_utf16_offsets(
    event: &RawEvent,
    text: Option<&str>,
    line_number: usize,
) -> ValidationResult<()> {
    if let Some(text) = text {
        check_utf16_offset_text(
            text,
            event.cursor_pos_before,
            "cursor_pos_before",
            line_number,
        )?;
        check_utf16_range_text(
            text,
            event.selection_start_before,
            event.selection_end_before,
            "selection_start_before",
            "selection_end_before",
            line_number,
        )
    } else {
        check_utf16_offset_len_only(
            event.cursor_pos_before,
            "cursor_pos_before",
            event.doc_len_before,
            line_number,
        )?;
        check_utf16_range_len_only(
            event.selection_start_before,
            event.selection_end_before,
            "selection_start_before",
            "selection_end_before",
            event.doc_len_before,
            line_number,
        )
    }
}

fn validate_after_utf16_offsets(
    event: &RawEvent,
    text: Option<&str>,
    line_number: usize,
) -> ValidationResult<()> {
    if let Some(text) = text {
        check_utf16_offset_text(
            text,
            event.cursor_pos_after,
            "cursor_pos_after",
            line_number,
        )?;
        check_utf16_range_text(
            text,
            event.selection_start_after,
            event.selection_end_after,
            "selection_start_after",
            "selection_end_after",
            line_number,
        )
    } else {
        check_utf16_offset_len_only(
            event.cursor_pos_after,
            "cursor_pos_after",
            event.doc_len_after,
            line_number,
        )?;
        check_utf16_range_len_only(
            event.selection_start_after,
            event.selection_end_after,
            "selection_start_after",
            "selection_end_after",
            event.doc_len_after,
            line_number,
        )
    }
}

fn compute_after_text(
    event: &RawEvent,
    before_text: Option<&str>,
    line_number: usize,
) -> ValidationResult<Option<String>> {
    let Some(before_text) = before_text else {
        return Ok(None);
    };
    let (Some(start), Some(end)) = (event.selection_start_before, event.selection_end_before)
    else {
        return Ok(None);
    };

    if matches!(
        event.diff_op,
        Some(DiffOp::SelectionOnly | DiffOp::NoTextChange)
    ) {
        return Ok(Some(before_text.to_string()));
    }

    let range = utf16_code_unit_range_to_utf8_byte_range(before_text, start as usize, end as usize)
        .map_err(|error| {
            utf16_error_to_validation_error(
                line_number,
                "selection_start_before",
                "selection_end_before",
                error,
            )
        })?;

    let mut after_text = before_text.to_string();
    after_text.replace_range(range, event.inserted_text.as_deref().unwrap_or(""));
    Ok(Some(after_text))
}

fn expected_doc_len_after_from_metadata(event: &RawEvent) -> Option<usize> {
    let before_len = event.doc_len_before? as usize;
    if matches!(
        event.diff_op,
        Some(DiffOp::SelectionOnly | DiffOp::NoTextChange)
    ) {
        return Some(before_len);
    }

    let start = event.selection_start_before? as usize;
    let end = event.selection_end_before? as usize;
    if start > end || end > before_len {
        return None;
    }

    let inserted_len = event
        .inserted_text
        .as_deref()
        .map(utf16_code_unit_len)
        .unwrap_or(0);
    Some(before_len - (end - start) + inserted_len)
}

fn check_utf16_offset_text(
    text: &str,
    offset: Option<u32>,
    field: &'static str,
    line_number: usize,
) -> ValidationResult<()> {
    if let Some(offset) = offset {
        utf16_code_unit_offset_to_utf8_byte_index(text, offset as usize)
            .map_err(|error| utf16_error_to_validation_error(line_number, field, field, error))?;
    }

    Ok(())
}

fn check_utf16_range_text(
    text: &str,
    start: Option<u32>,
    end: Option<u32>,
    start_field: &'static str,
    end_field: &'static str,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(start), Some(end)) = (start, end) {
        utf16_code_unit_range_to_utf8_byte_range(text, start as usize, end as usize).map_err(
            |error| utf16_error_to_validation_error(line_number, start_field, end_field, error),
        )?;
    }

    Ok(())
}

fn check_utf16_offset_len_only(
    offset: Option<u32>,
    field: &'static str,
    doc_len: Option<u32>,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(offset), Some(doc_len)) = (offset, doc_len) {
        if offset > doc_len {
            return Err(utf16_numeric_error(
                line_number,
                Utf16NumericMetadataReason::OffsetBeyondUtf16Length,
                field,
            ));
        }
    }

    Ok(())
}

fn check_utf16_range_len_only(
    start: Option<u32>,
    end: Option<u32>,
    start_field: &'static str,
    end_field: &'static str,
    doc_len: Option<u32>,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(start), Some(end)) = (start, end) {
        if start > end {
            return Err(utf16_numeric_error(
                line_number,
                Utf16NumericMetadataReason::StartGreaterThanEnd,
                start_field,
            ));
        }
    }

    check_utf16_offset_len_only(start, start_field, doc_len, line_number)?;
    check_utf16_offset_len_only(end, end_field, doc_len, line_number)
}

fn utf16_error_to_validation_error(
    line_number: usize,
    start_field: &'static str,
    end_field: &'static str,
    error: Utf16OffsetError,
) -> ValidationError {
    let (reason, field) = match error {
        Utf16OffsetError::StartAfterEnd { .. } => {
            (Utf16NumericMetadataReason::StartGreaterThanEnd, start_field)
        }
        Utf16OffsetError::OffsetBeyondUtf16Length { .. } => (
            Utf16NumericMetadataReason::OffsetBeyondUtf16Length,
            end_field,
        ),
        Utf16OffsetError::OffsetInsideSurrogatePair { .. } => (
            Utf16NumericMetadataReason::OffsetInsideSurrogatePair,
            end_field,
        ),
        Utf16OffsetError::InvalidBoundary { .. }
        | Utf16OffsetError::UnsupportedPositionUnit { .. }
        | Utf16OffsetError::InternalInvariantViolation => {
            (Utf16NumericMetadataReason::InvalidUtf16Boundary, end_field)
        }
    };

    utf16_numeric_error(line_number, reason, field)
}

fn utf16_numeric_error(
    line_number: usize,
    reason: Utf16NumericMetadataReason,
    field: &'static str,
) -> ValidationError {
    ValidationError::new(
        line_number,
        ValidationErrorKind::Utf16NumericMetadata { reason, field },
    )
}

fn trim_jsonl_newline(line: &[u8]) -> &[u8] {
    let line = line.strip_suffix(b"\n").unwrap_or(line);
    line.strip_suffix(b"\r").unwrap_or(line)
}

fn is_ascii_blank(line: &[u8]) -> bool {
    line.iter().all(u8::is_ascii_whitespace)
}

fn validate_sequence(
    event: &RawEvent,
    expected_seq: &mut Option<u64>,
    line_number: usize,
) -> ValidationResult<()> {
    match expected_seq {
        Some(expected) if event.seq != *expected => Err(ValidationError::new(
            line_number,
            ValidationErrorKind::SequenceGap {
                expected_seq: *expected,
                actual_seq: event.seq,
            },
        )),
        Some(expected) => {
            *expected = event.seq.checked_add(1).ok_or_else(|| {
                ValidationError::new(
                    line_number,
                    ValidationErrorKind::SequenceOverflow {
                        previous_seq: event.seq,
                    },
                )
            })?;
            Ok(())
        }
        None => {
            *expected_seq = event.seq.checked_add(1);
            if expected_seq.is_none() {
                return Err(ValidationError::new(
                    line_number,
                    ValidationErrorKind::SequenceOverflow {
                        previous_seq: event.seq,
                    },
                ));
            }
            Ok(())
        }
    }
}

fn validate_timestamp(
    event: &RawEvent,
    previous_timestamp_ms: &mut Option<u64>,
    line_number: usize,
) -> ValidationResult<()> {
    if let Some(previous) = *previous_timestamp_ms {
        if event.timestamp_ms < previous {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::TimestampInversion {
                    previous_timestamp_ms: previous,
                    actual_timestamp_ms: event.timestamp_ms,
                },
            ));
        }
    }

    *previous_timestamp_ms = Some(event.timestamp_ms);
    Ok(())
}

fn validate_cursor_ranges(event: &RawEvent, line_number: usize) -> ValidationResult<()> {
    check_cursor(
        event.cursor_pos_before,
        "cursor_pos_before",
        event.doc_len_before,
        "doc_len_before",
        line_number,
    )?;
    check_cursor(
        event.cursor_pos_after,
        "cursor_pos_after",
        event.doc_len_after,
        "doc_len_after",
        line_number,
    )
}

fn check_cursor(
    cursor: Option<u32>,
    field: &'static str,
    doc_len: Option<u32>,
    doc_len_field: &'static str,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(cursor), Some(doc_len)) = (cursor, doc_len) {
        if cursor > doc_len {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::CursorOutOfBounds {
                    field,
                    cursor,
                    doc_len_field,
                    doc_len,
                },
            ));
        }
    }

    Ok(())
}

fn validate_selection_ranges(event: &RawEvent, line_number: usize) -> ValidationResult<()> {
    check_selection_pair(
        event.selection_start_before,
        "selection_start_before",
        event.selection_end_before,
        "selection_end_before",
        line_number,
    )?;
    check_selection_pair(
        event.selection_start_after,
        "selection_start_after",
        event.selection_end_after,
        "selection_end_after",
        line_number,
    )?;
    check_selection_bound(
        event.selection_start_before,
        "selection_start_before",
        event.doc_len_before,
        "doc_len_before",
        line_number,
    )?;
    check_selection_bound(
        event.selection_end_before,
        "selection_end_before",
        event.doc_len_before,
        "doc_len_before",
        line_number,
    )?;
    check_selection_bound(
        event.selection_start_after,
        "selection_start_after",
        event.doc_len_after,
        "doc_len_after",
        line_number,
    )?;
    check_selection_bound(
        event.selection_end_after,
        "selection_end_after",
        event.doc_len_after,
        "doc_len_after",
        line_number,
    )
}

fn check_selection_pair(
    start: Option<u32>,
    start_field: &'static str,
    end: Option<u32>,
    end_field: &'static str,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(start), Some(end)) = (start, end) {
        if start > end {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::SelectionRangeInverted {
                    start_field,
                    end_field,
                    start,
                    end,
                },
            ));
        }
    }

    Ok(())
}

fn check_selection_bound(
    position: Option<u32>,
    field: &'static str,
    doc_len: Option<u32>,
    doc_len_field: &'static str,
    line_number: usize,
) -> ValidationResult<()> {
    if let (Some(position), Some(doc_len)) = (position, doc_len) {
        if position > doc_len {
            return Err(ValidationError::new(
                line_number,
                ValidationErrorKind::SelectionOutOfBounds {
                    field,
                    position,
                    doc_len_field,
                    doc_len,
                },
            ));
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        validate_jsonl_reader, EmptyLinePolicy, ValidationErrorKind, ValidationOptions,
        DEFAULT_MAX_LINE_BYTES,
    };
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

    fn validate_fixture(
        relative_path: &str,
    ) -> Result<super::ValidationReport, super::ValidationError> {
        let path = fixture_path(relative_path);
        let content = fs::read_to_string(&path)
            .unwrap_or_else(|error| panic!("failed to read {}: {error}", path.display()));
        validate_jsonl_reader(Cursor::new(content), &ValidationOptions::default())
    }

    fn validate_fixture_public_safe(
        relative_path: &str,
    ) -> Result<super::ValidationReport, super::ValidationError> {
        let path = fixture_path(relative_path);
        let content = fs::read_to_string(&path)
            .unwrap_or_else(|error| panic!("failed to read fixture {relative_path}: {error}"));
        validate_jsonl_reader(Cursor::new(content), &ValidationOptions::default())
    }

    fn assert_position_unit_fixture_fails(relative_path: &str, expected_reason_code: &str) {
        let err = validate_fixture_public_safe(relative_path)
            .expect_err("position_unit Phase 1 fixture should fail");

        assert_eq!(err.kind.reason_code(), expected_reason_code);
        assert!(matches!(
            err.kind,
            ValidationErrorKind::PositionUnitPolicy(_)
        ));
        assert_eq!(err.line_number, Some(1));
    }

    fn assert_position_unit_fixture_fails_with_reason_code(
        relative_path: &str,
        expected_reason_code: &str,
    ) -> super::ValidationError {
        let err = validate_fixture_public_safe(relative_path)
            .expect_err("position_unit fixture should fail");

        assert_eq!(err.kind.reason_code(), expected_reason_code);
        err
    }

    #[test]
    fn valid_simple_typing_fixture_passes() {
        let report =
            validate_fixture("tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl")
                .expect("valid simple_typing fixture should pass");

        assert_eq!(report.event_count, 6);
        assert_eq!(report.first_seq, Some(1));
        assert_eq!(report.last_seq, Some(6));
    }

    #[test]
    fn all_valid_fixtures_pass() {
        let valid_dir = fixture_path("tests/fixtures/synthetic/raw_events/valid");
        let mut paths = fs::read_dir(&valid_dir)
            .unwrap_or_else(|error| panic!("failed to read {}: {error}", valid_dir.display()))
            .map(|entry| entry.expect("valid fixture entry is readable").path())
            .filter(|path| path.extension().and_then(|ext| ext.to_str()) == Some("jsonl"))
            .collect::<Vec<_>>();
        paths.sort();

        assert_eq!(paths.len(), 7);

        for path in paths {
            let content = fs::read_to_string(&path)
                .unwrap_or_else(|error| panic!("failed to read {}: {error}", path.display()));
            let report = validate_jsonl_reader(Cursor::new(content), &ValidationOptions::default())
                .unwrap_or_else(|error| panic!("{} failed validation: {error}", path.display()));
            assert!(
                report.event_count > 0,
                "{} should contain at least one event",
                path.display()
            );
        }
    }

    #[test]
    fn malformed_json_fixture_fails_without_panic() {
        let err =
            validate_fixture("tests/fixtures/synthetic/raw_events/invalid/malformed_json.jsonl")
                .expect_err("malformed JSON fixture should fail");

        assert!(matches!(err.kind, ValidationErrorKind::MalformedJson(_)));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn missing_required_field_fixture_fails() {
        let err = validate_fixture(
            "tests/fixtures/synthetic/raw_events/invalid/missing_required_field.jsonl",
        )
        .expect_err("missing required field fixture should fail");

        assert!(matches!(err.kind, ValidationErrorKind::RawEventSchema(_)));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn unknown_forbidden_field_fixture_fails() {
        let err = validate_fixture(
            "tests/fixtures/synthetic/raw_events/invalid/unknown_forbidden_field.jsonl",
        )
        .expect_err("forbidden no-oracle field fixture should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::ForbiddenNoOracleField(field) if field == "final_text"
        ));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn no_oracle_forbidden_fields_are_rejected() {
        for field in ["final_text", "observed_after_text", "gold_label"] {
            let json = format!(
                r#"{{"logger_schema_version":"kslog.raw_event.v1","session_id":"synthetic_session_forbidden","participant_local_id":"synthetic_writer_forbidden","task_id":"synthetic_task_freewrite_001","prompt_id":"synthetic_prompt_forbidden","seq":1,"timestamp_ms":1700000004000,"event_type":"input","is_composing":false,"{field}":"forbidden synthetic value"}}"#
            );

            let err = validate_jsonl_reader(Cursor::new(json), &ValidationOptions::default())
                .expect_err("forbidden no-oracle field should fail");

            assert!(matches!(
                err.kind,
                ValidationErrorKind::ForbiddenNoOracleField(found) if found == field
            ));
            assert_eq!(err.line_number, Some(1));
        }
    }

    #[test]
    fn position_unit_phase1_valid_fixtures_pass() {
        for relative_path in [
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_ascii_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_japanese_cursor_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_japanese_selection_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_emoji_boundary_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_mixed_japanese_emoji_utf16_position_unit.jsonl",
        ] {
            let report = validate_fixture_public_safe(relative_path)
                .expect("valid position_unit Phase 1 fixture should pass");

            assert!(
                report.event_count > 0,
                "{relative_path} should contain at least one event"
            );
        }
    }

    #[test]
    fn position_unit_phase1_invalid_missing_fails_with_reason_code() {
        assert_position_unit_fixture_fails(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_v0_2_missing_position_unit.jsonl",
            "missing_position_unit",
        );
    }

    #[test]
    fn position_unit_phase1_invalid_unsupported_values_fail_with_reason_code() {
        for relative_path in [
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unsupported_position_unit_byte_index.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unsupported_position_unit_code_point.jsonl",
        ] {
            assert_position_unit_fixture_fails(relative_path, "unsupported_position_unit");
        }
    }

    #[test]
    fn position_unit_phase1_invalid_schema_mismatch_fails_with_reason_code() {
        assert_position_unit_fixture_fails(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_position_unit_schema_mismatch.jsonl",
            "position_unit_schema_mismatch",
        );
    }

    #[test]
    fn position_unit_phase1_invalid_unknown_schema_version_fails_with_reason_code() {
        assert_position_unit_fixture_fails(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unknown_schema_version.jsonl",
            "unknown_schema_version",
        );
    }

    #[test]
    fn position_unit_phase1_legacy_missing_fixture_is_allowed() {
        let report = validate_fixture_public_safe(
            "tests/fixtures/web_logger_position_unit_schema/legacy/legacy_missing_position_unit_explicitly_gated.jsonl",
        )
        .expect("legacy missing position_unit fixture should pass through explicit gate");

        assert_eq!(report.event_count, 1);
    }

    #[test]
    fn position_unit_phase1_failures_are_not_overridden_by_phase2() {
        for (relative_path, expected_reason_code) in [
            (
                "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_v0_2_missing_position_unit.jsonl",
                "missing_position_unit",
            ),
            (
                "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unsupported_position_unit_byte_index.jsonl",
                "unsupported_position_unit",
            ),
            (
                "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unsupported_position_unit_code_point.jsonl",
                "unsupported_position_unit",
            ),
            (
                "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_position_unit_schema_mismatch.jsonl",
                "position_unit_schema_mismatch",
            ),
            (
                "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unknown_schema_version.jsonl",
                "unknown_schema_version",
            ),
        ] {
            assert_position_unit_fixture_fails_with_reason_code(relative_path, expected_reason_code);
        }
    }

    #[test]
    fn position_unit_phase2_valid_fixtures_pass() {
        for relative_path in [
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_ascii_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_japanese_cursor_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_japanese_selection_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_emoji_boundary_utf16_position_unit.jsonl",
            "tests/fixtures/web_logger_position_unit_schema/valid/valid_mixed_japanese_emoji_utf16_position_unit.jsonl",
        ] {
            let report = validate_fixture_public_safe(relative_path)
                .expect("valid position_unit Phase 2 fixture should pass");

            assert!(
                report.event_count > 0,
                "{relative_path} should contain at least one event"
            );
        }
    }

    #[test]
    fn position_unit_phase2_doc_len_before_mismatch_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_doc_len_before_utf16_mismatch.jsonl",
            "doc_len_before_utf16_mismatch",
        );

        assert_eq!(err.line_number, Some(2));
    }

    #[test]
    fn position_unit_phase2_doc_len_after_mismatch_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_doc_len_after_utf16_mismatch.jsonl",
            "doc_len_after_utf16_mismatch",
        );

        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn position_unit_phase2_selection_start_greater_than_end_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_selection_start_greater_than_end.jsonl",
            "start_greater_than_end",
        );

        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn position_unit_phase2_offset_beyond_utf16_length_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_offset_beyond_utf16_length.jsonl",
            "offset_beyond_utf16_length",
        );

        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn position_unit_phase2_surrogate_pair_internal_offset_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_surrogate_pair_internal_offset.jsonl",
            "offset_inside_surrogate_pair",
        );

        assert_eq!(err.line_number, Some(2));
    }

    #[test]
    fn position_unit_phase2_detectable_byte_index_misuse_fails_with_reason_code() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_byte_index_supplied_as_utf16_when_detectable.jsonl",
            "offset_beyond_utf16_length",
        );

        assert_eq!(err.line_number, Some(2));
    }

    #[test]
    fn position_unit_phase2_diagnostics_are_body_free() {
        let err = assert_position_unit_fixture_fails_with_reason_code(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_surrogate_pair_internal_offset.jsonl",
            "offset_inside_surrogate_pair",
        );
        let message = err.to_string();

        assert!(!message.contains('{'));
        assert!(!message.contains('}'));
        assert!(!message.contains("inserted_text"));
        assert!(!message.contains("deleted_text"));
        assert!(!message.contains("source_text"));
        assert!(!message.contains("selected_text"));
        assert!(!message.contains("😀"));
    }

    #[test]
    fn position_unit_phase1_preserves_existing_invalid_synthetic_fixtures() {
        let invalid_dir = fixture_path("tests/fixtures/synthetic/raw_events/invalid");
        let mut paths = fs::read_dir(&invalid_dir)
            .unwrap_or_else(|error| panic!("failed to read invalid fixture directory: {error}"))
            .map(|entry| entry.expect("invalid fixture entry is readable").path())
            .filter(|path| path.extension().and_then(|ext| ext.to_str()) == Some("jsonl"))
            .collect::<Vec<_>>();
        paths.sort();

        assert_eq!(paths.len(), 7);

        for path in paths {
            let relative_path = path
                .strip_prefix(repository_root())
                .expect("fixture path is under repository root")
                .to_string_lossy()
                .into_owned();
            assert!(
                validate_fixture_public_safe(&relative_path).is_err(),
                "{relative_path} should remain invalid"
            );
        }
    }

    #[test]
    fn position_unit_phase1_diagnostics_are_body_free() {
        let err = validate_fixture_public_safe(
            "tests/fixtures/web_logger_position_unit_schema/invalid/invalid_unsupported_position_unit_byte_index.jsonl",
        )
        .expect_err("unsupported position_unit fixture should fail");
        let message = err.to_string();

        assert_eq!(err.kind.reason_code(), "unsupported_position_unit");
        assert!(!message.contains('{'));
        assert!(!message.contains('}'));
        assert!(!message.contains("inserted_text"));
        assert!(!message.contains("deleted_text"));
        assert!(!message.contains("source_text"));
        assert!(!message.contains("selected_text"));
    }

    #[test]
    fn seq_gap_fixture_fails() {
        let err = validate_fixture("tests/fixtures/synthetic/raw_events/invalid/seq_gap.jsonl")
            .expect_err("seq gap fixture should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::SequenceGap {
                expected_seq: 2,
                actual_seq: 3
            }
        ));
        assert_eq!(err.line_number, Some(2));
    }

    #[test]
    fn timestamp_inversion_fixture_fails() {
        let err = validate_fixture(
            "tests/fixtures/synthetic/raw_events/invalid/timestamp_inversion.jsonl",
        )
        .expect_err("timestamp inversion fixture should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::TimestampInversion {
                previous_timestamp_ms: 1700000002000,
                actual_timestamp_ms: 1700000001000
            }
        ));
        assert_eq!(err.line_number, Some(2));
    }

    #[test]
    fn invalid_cursor_range_fixture_fails() {
        let err = validate_fixture(
            "tests/fixtures/synthetic/raw_events/invalid/invalid_cursor_range.jsonl",
        )
        .expect_err("invalid cursor range fixture should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::CursorOutOfBounds {
                field: "cursor_pos_after",
                cursor: 8,
                doc_len_field: "doc_len_after",
                doc_len: 3
            }
        ));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn invalid_selection_range_fixture_fails() {
        let err = validate_fixture(
            "tests/fixtures/synthetic/raw_events/invalid/invalid_selection_range.jsonl",
        )
        .expect_err("invalid selection range fixture should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::SelectionRangeInverted {
                start_field: "selection_start_after",
                end_field: "selection_end_after",
                start: 5,
                end: 2
            }
        ));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn empty_line_is_rejected_by_default() {
        let err = validate_jsonl_reader(Cursor::new("\n"), &ValidationOptions::default())
            .expect_err("empty line should fail by default");

        assert!(matches!(err.kind, ValidationErrorKind::EmptyLine));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn line_too_long_is_rejected() {
        let json = r#"{"logger_schema_version":"kslog.raw_event.v1","session_id":"synthetic_session_too_long","participant_local_id":"synthetic_writer_too_long","task_id":"synthetic_task_freewrite_001","prompt_id":"synthetic_prompt_invalid","seq":1,"timestamp_ms":1700000003000,"event_type":"input","is_composing":false}"#;
        let options = ValidationOptions {
            max_line_bytes: 12,
            empty_line_policy: EmptyLinePolicy::Reject,
        };

        let err = validate_jsonl_reader(Cursor::new(json), &options)
            .expect_err("line exceeding configured limit should fail");

        assert!(matches!(
            err.kind,
            ValidationErrorKind::LineTooLong {
                max_line_bytes: 12,
                ..
            }
        ));
        assert_eq!(err.line_number, Some(1));
    }

    #[test]
    fn default_max_line_bytes_is_nonzero() {
        assert!(DEFAULT_MAX_LINE_BYTES > 0);
    }
}
