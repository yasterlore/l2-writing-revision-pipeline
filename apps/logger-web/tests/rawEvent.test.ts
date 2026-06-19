import {
  buildRawEvent,
  forbiddenFieldNames,
  SYNTHETIC_METADATA,
  toJsonl,
  type RawEvent
} from "../src/rawEvent";

function assert(condition: unknown, message: string): void {
  if (!condition) {
    throw new Error(message);
  }
}

function assertNoForbiddenFields(event: RawEvent): void {
  const keys = Object.keys(event);
  for (const forbidden of forbiddenFieldNames()) {
    assert(!keys.includes(forbidden), `forbidden field was generated: ${forbidden}`);
  }
}

const event = buildRawEvent({
  metadata: SYNTHETIC_METADATA,
  seq: 1,
  timestampMs: 1_700_000_000_000,
  eventType: "input",
  inputType: "insertText",
  isComposing: false,
  before: {
    text: "",
    selectionStart: 0,
    selectionEnd: 0
  },
  after: {
    text: "A",
    selectionStart: 1,
    selectionEnd: 1
  },
  qualityFlags: []
});

assert(event.logger_schema_version === "web_logger_schema_v0_1", "schema version is set");
assert(event.session_id === "synthetic_session_web_001", "session id is synthetic");
assert(event.participant_local_id === "synthetic_writer_web_001", "participant id is synthetic");
assert(event.seq === 1, "seq is set");
assert(event.timestamp_ms === 1_700_000_000_000, "timestamp is set");
assert(event.event_type === "input", "event type is set");
assert(event.input_type === "insertText", "input type is set");
assert(event.inserted_text === "A", "inserted text is inferred");
assert(event.deleted_text === undefined, "deleted text is absent");
assert(event.diff_op === "insert", "diff op is inferred");
assert(event.quality_flags.length === 0, "quality flags are present");
assertNoForbiddenFields(event);

const deletion = buildRawEvent({
  metadata: SYNTHETIC_METADATA,
  seq: 2,
  timestampMs: 1_700_000_000_001,
  eventType: "input",
  inputType: "deleteContentBackward",
  isComposing: false,
  before: {
    text: "AB",
    selectionStart: 2,
    selectionEnd: 2
  },
  after: {
    text: "A",
    selectionStart: 1,
    selectionEnd: 1
  }
});

assert(deletion.deleted_text === "B", "deleted text is inferred");
assert(deletion.diff_op === "delete", "delete op is inferred");
assert(deletion.cursor_pos_before === 2, "collapsed delete cursor before is preserved");
assert(deletion.cursor_pos_after === 1, "collapsed delete cursor after is preserved");
assert(deletion.doc_len_before === 2, "collapsed delete doc_len_before is char count");
assert(deletion.doc_len_after === 1, "collapsed delete doc_len_after is char count");
assertNoForbiddenFields(deletion);

const selectionDeletion = buildRawEvent({
  metadata: SYNTHETIC_METADATA,
  seq: 3,
  timestampMs: 1_700_000_000_002,
  eventType: "input",
  inputType: "deleteContentBackward",
  isComposing: false,
  before: {
    text: "ABCDE",
    selectionStart: 1,
    selectionEnd: 4
  },
  after: {
    text: "AE",
    selectionStart: 1,
    selectionEnd: 1
  }
});

assert(selectionDeletion.deleted_text === "BCD", "selection delete text is inferred from selected range");
assert(selectionDeletion.inserted_text === undefined, "selection delete has no inserted text");
assert(selectionDeletion.diff_op === "delete", "selection delete op is inferred");
assert(selectionDeletion.selection_start_before === 1, "selection delete start before is preserved");
assert(selectionDeletion.selection_end_before === 4, "selection delete end before is preserved");
assert(selectionDeletion.cursor_pos_before === 1, "selection delete cursor before follows selection start");
assert(selectionDeletion.cursor_pos_after === 1, "selection delete cursor after is collapsed");
assertNoForbiddenFields(selectionDeletion);

const movedCursorDeletion = buildRawEvent({
  metadata: SYNTHETIC_METADATA,
  seq: 4,
  timestampMs: 1_700_000_000_003,
  eventType: "input",
  inputType: "deleteContentBackward",
  isComposing: false,
  before: {
    text: "ABCDE",
    selectionStart: 3,
    selectionEnd: 3
  },
  after: {
    text: "ABDE",
    selectionStart: 2,
    selectionEnd: 2
  }
});

assert(movedCursorDeletion.deleted_text === "C", "moved cursor delete text is inferred from cursor range");
assert(movedCursorDeletion.inserted_text === undefined, "moved cursor delete has no inserted text");
assert(movedCursorDeletion.diff_op === "delete", "moved cursor delete op is inferred");
assert(movedCursorDeletion.cursor_pos_before === 3, "moved cursor delete cursor before is preserved");
assert(movedCursorDeletion.cursor_pos_after === 2, "moved cursor delete cursor after is preserved");
assertNoForbiddenFields(movedCursorDeletion);

const jsonl = toJsonl([event, deletion, selectionDeletion, movedCursorDeletion]);
assert(jsonl.split("\n").length === 5, "JSONL has four records and trailing newline");

const reparsed = jsonl
  .trim()
  .split("\n")
  .map((line) => JSON.parse(line) as RawEvent);

assert(reparsed.length === 4, "JSONL records can be reparsed");
for (const rawEvent of reparsed) {
  assertNoForbiddenFields(rawEvent);
}
