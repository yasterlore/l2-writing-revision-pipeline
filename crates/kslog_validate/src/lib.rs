//! Deterministic JSONL validation for raw keystroke event logs.
//!
//! This crate validates structure, ordering, ranges, and no-oracle field policy.
//! It does not replay text or derive revision events.

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
    io::{self, BufRead, Read},
};

use kslog_schema::RawEvent;

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
        validate_sequence(&event, &mut expected_seq, line_number)?;
        validate_timestamp(&event, &mut previous_timestamp_ms, line_number)?;
        validate_cursor_ranges(&event, line_number)?;
        validate_selection_ranges(&event, line_number)?;

        report.record_event(&event);
    }

    Ok(report)
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
