//! Shared schema types for keystroke-level writing-process logs.
//!
//! This crate defines data shapes only. Deterministic validation, text replay,
//! revision-event extraction, and micro-episode construction belong in later
//! Rust crates.

use serde::{Deserialize, Serialize};

/// Browser or logger event category for one raw event row.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    BeforeInput,
    Input,
    KeyDown,
    KeyUp,
    CompositionStart,
    CompositionUpdate,
    CompositionEnd,
    SelectionChange,
    Focus,
    Blur,
    Paste,
    Cut,
}

/// Browser `InputEvent.inputType` values represented by the first schema version.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub enum InputType {
    InsertText,
    InsertLineBreak,
    InsertParagraph,
    InsertFromPaste,
    DeleteContentBackward,
    DeleteContentForward,
    DeleteByCut,
    HistoryUndo,
    HistoryRedo,
}

/// Coarse edit operation hint recorded by the logger or later synthetic fixtures.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DiffOp {
    Insert,
    Delete,
    Replace,
    SelectionOnly,
    Composition,
    NoTextChange,
}

/// One raw browser-event row from a keystroke-level writing log.
///
/// This struct intentionally excludes no-oracle-forbidden fields such as
/// `final_text`, `observed_after_text`, and `gold_label`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RawEvent {
    pub logger_schema_version: String,
    pub session_id: String,
    pub participant_local_id: String,
    pub task_id: String,
    pub prompt_id: String,
    pub seq: u64,
    pub timestamp_ms: u64,
    pub event_type: EventType,
    pub input_type: Option<InputType>,
    pub is_composing: bool,
    pub composition_id: Option<String>,
    pub selection_start_before: Option<u32>,
    pub selection_end_before: Option<u32>,
    pub selection_start_after: Option<u32>,
    pub selection_end_after: Option<u32>,
    pub cursor_pos_before: Option<u32>,
    pub cursor_pos_after: Option<u32>,
    pub doc_len_before: Option<u32>,
    pub doc_len_after: Option<u32>,
    pub inserted_text: Option<String>,
    pub deleted_text: Option<String>,
    pub text_hash_before: Option<String>,
    pub text_hash_after: Option<String>,
    pub diff_op: Option<DiffOp>,
    #[serde(default)]
    pub quality_flags: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::{DiffOp, EventType, InputType, RawEvent};
    use std::{
        fs,
        path::{Path, PathBuf},
    };

    fn synthetic_insert_event() -> RawEvent {
        RawEvent {
            logger_schema_version: "kslog.raw_event.v1".to_string(),
            session_id: "synthetic-session-001".to_string(),
            participant_local_id: "synthetic-participant-001".to_string(),
            task_id: "synthetic-freewrite-task".to_string(),
            prompt_id: "synthetic-prompt-a".to_string(),
            seq: 7,
            timestamp_ms: 1_700_000_000_123,
            event_type: EventType::Input,
            input_type: Some(InputType::InsertText),
            is_composing: false,
            composition_id: None,
            selection_start_before: Some(4),
            selection_end_before: Some(4),
            selection_start_after: Some(5),
            selection_end_after: Some(5),
            cursor_pos_before: Some(4),
            cursor_pos_after: Some(5),
            doc_len_before: Some(4),
            doc_len_after: Some(5),
            inserted_text: Some("x".to_string()),
            deleted_text: None,
            text_hash_before: Some("synthetic-hash-before".to_string()),
            text_hash_after: Some("synthetic-hash-after".to_string()),
            diff_op: Some(DiffOp::Insert),
            quality_flags: vec![],
        }
    }

    #[test]
    fn deserializes_synthetic_valid_json() {
        let json = r#"
        {
          "logger_schema_version": "kslog.raw_event.v1",
          "session_id": "synthetic-session-001",
          "participant_local_id": "synthetic-participant-001",
          "task_id": "synthetic-freewrite-task",
          "prompt_id": "synthetic-prompt-a",
          "seq": 7,
          "timestamp_ms": 1700000000123,
          "event_type": "input",
          "input_type": "insertText",
          "is_composing": false,
          "composition_id": null,
          "selection_start_before": 4,
          "selection_end_before": 4,
          "selection_start_after": 5,
          "selection_end_after": 5,
          "cursor_pos_before": 4,
          "cursor_pos_after": 5,
          "doc_len_before": 4,
          "doc_len_after": 5,
          "inserted_text": "x",
          "deleted_text": null,
          "text_hash_before": "synthetic-hash-before",
          "text_hash_after": "synthetic-hash-after",
          "diff_op": "insert",
          "quality_flags": []
        }
        "#;

        let event: RawEvent = serde_json::from_str(json).expect("synthetic RawEvent JSON parses");

        assert_eq!(event, synthetic_insert_event());
    }

    #[test]
    fn serializes_raw_event_to_json() {
        let event = synthetic_insert_event();

        let json = serde_json::to_string(&event).expect("RawEvent serializes");
        let reparsed: RawEvent = serde_json::from_str(&json).expect("serialized RawEvent reparses");

        assert_eq!(reparsed, event);
    }

    #[test]
    fn handles_event_type_as_enum() {
        let json = r#"
        {
          "logger_schema_version": "kslog.raw_event.v1",
          "session_id": "synthetic-session-002",
          "participant_local_id": "synthetic-participant-002",
          "task_id": "synthetic-freewrite-task",
          "prompt_id": "synthetic-prompt-b",
          "seq": 1,
          "timestamp_ms": 1700000000000,
          "event_type": "composition_start",
          "input_type": null,
          "is_composing": true,
          "composition_id": "synthetic-composition-001",
          "selection_start_before": null,
          "selection_end_before": null,
          "selection_start_after": null,
          "selection_end_after": null,
          "cursor_pos_before": null,
          "cursor_pos_after": null,
          "doc_len_before": null,
          "doc_len_after": null,
          "inserted_text": null,
          "deleted_text": null,
          "text_hash_before": null,
          "text_hash_after": null,
          "diff_op": "composition",
          "quality_flags": ["synthetic_ime_case"]
        }
        "#;

        let event: RawEvent = serde_json::from_str(json).expect("composition event parses");

        assert_eq!(event.event_type, EventType::CompositionStart);
        assert_eq!(event.diff_op, Some(DiffOp::Composition));
    }

    #[test]
    fn deserializes_when_optional_fields_are_missing() {
        let json = r#"
        {
          "logger_schema_version": "kslog.raw_event.v1",
          "session_id": "synthetic-session-003",
          "participant_local_id": "synthetic-participant-003",
          "task_id": "synthetic-freewrite-task",
          "prompt_id": "synthetic-prompt-c",
          "seq": 2,
          "timestamp_ms": 1700000000456,
          "event_type": "selection_change",
          "is_composing": false
        }
        "#;

        let event: RawEvent =
            serde_json::from_str(json).expect("missing optional fields default to None");

        assert_eq!(event.event_type, EventType::SelectionChange);
        assert_eq!(event.input_type, None);
        assert_eq!(event.inserted_text, None);
        assert!(event.quality_flags.is_empty());
    }

    #[test]
    fn rejects_no_oracle_forbidden_unknown_fields() {
        let json = r#"
        {
          "logger_schema_version": "kslog.raw_event.v1",
          "session_id": "synthetic-session-004",
          "participant_local_id": "synthetic-participant-004",
          "task_id": "synthetic-freewrite-task",
          "prompt_id": "synthetic-prompt-d",
          "seq": 3,
          "timestamp_ms": 1700000000789,
          "event_type": "input",
          "input_type": "insertText",
          "is_composing": false,
          "final_text": "forbidden synthetic future text"
        }
        "#;

        let err = serde_json::from_str::<RawEvent>(json).expect_err("final_text is not accepted");

        assert!(err.to_string().contains("final_text"));
    }

    fn repository_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
    }

    fn read_jsonl_fixture(path: &Path) -> Vec<RawEvent> {
        let content = fs::read_to_string(path)
            .unwrap_or_else(|err| panic!("failed to read {}: {err}", path.display()));
        let mut events = Vec::new();

        for (line_index, line) in content.lines().enumerate() {
            if line.trim().is_empty() {
                continue;
            }

            let event = serde_json::from_str::<RawEvent>(line).unwrap_or_else(|err| {
                panic!(
                    "failed to parse {} at line {}: {err}",
                    path.display(),
                    line_index + 1
                )
            });
            events.push(event);
        }

        events
    }

    #[test]
    fn valid_synthetic_jsonl_fixtures_deserialize_line_by_line() {
        let valid_dir = repository_root().join("tests/fixtures/synthetic/raw_events/valid");
        let mut fixture_paths = fs::read_dir(&valid_dir)
            .unwrap_or_else(|err| panic!("failed to read {}: {err}", valid_dir.display()))
            .map(|entry| entry.expect("fixture directory entry is readable").path())
            .filter(|path| path.extension().and_then(|ext| ext.to_str()) == Some("jsonl"))
            .collect::<Vec<_>>();
        fixture_paths.sort();

        assert_eq!(fixture_paths.len(), 7);

        for path in fixture_paths {
            let events = read_jsonl_fixture(&path);
            assert!(
                !events.is_empty(),
                "{} should contain at least one RawEvent",
                path.display()
            );
        }
    }

    #[test]
    fn unknown_forbidden_field_fixture_is_rejected_by_raw_event_schema() {
        let path = repository_root()
            .join("tests/fixtures/synthetic/raw_events/invalid/unknown_forbidden_field.jsonl");
        let content = fs::read_to_string(&path)
            .unwrap_or_else(|err| panic!("failed to read {}: {err}", path.display()));
        let line = content
            .lines()
            .find(|line| !line.trim().is_empty())
            .expect("fixture contains one non-empty JSONL line");

        let err = serde_json::from_str::<RawEvent>(line)
            .expect_err("observed no-oracle forbidden field should be rejected");

        assert!(err.to_string().contains("final_text"));
    }
}
