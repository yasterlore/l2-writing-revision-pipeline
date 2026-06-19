export type EventType =
  | "before_input"
  | "input"
  | "key_down"
  | "key_up"
  | "composition_start"
  | "composition_update"
  | "composition_end"
  | "selection_change"
  | "focus"
  | "blur"
  | "paste"
  | "cut";

export type InputType =
  | "insertText"
  | "insertLineBreak"
  | "insertParagraph"
  | "insertFromPaste"
  | "deleteContentBackward"
  | "deleteContentForward"
  | "deleteByCut"
  | "historyUndo"
  | "historyRedo";

export type DiffOp =
  | "insert"
  | "delete"
  | "replace"
  | "selection_only"
  | "composition"
  | "no_text_change";

export interface TextSnapshot {
  text: string;
  selectionStart: number;
  selectionEnd: number;
}

export interface SyntheticMetadata {
  logger_schema_version: string;
  session_id: string;
  participant_local_id: string;
  task_id: string;
  prompt_id: string;
}

export interface RawEvent {
  logger_schema_version: string;
  session_id: string;
  participant_local_id: string;
  task_id: string;
  prompt_id: string;
  seq: number;
  timestamp_ms: number;
  event_type: EventType;
  input_type?: InputType;
  is_composing: boolean;
  composition_id?: string;
  selection_start_before?: number;
  selection_end_before?: number;
  selection_start_after?: number;
  selection_end_after?: number;
  cursor_pos_before?: number;
  cursor_pos_after?: number;
  doc_len_before?: number;
  doc_len_after?: number;
  inserted_text?: string;
  deleted_text?: string;
  text_hash_before?: string;
  text_hash_after?: string;
  diff_op?: DiffOp;
  quality_flags: string[];
}

export interface BuildRawEventInput {
  metadata: SyntheticMetadata;
  seq: number;
  timestampMs: number;
  eventType: EventType;
  inputType?: string | null;
  isComposing: boolean;
  compositionId?: string;
  before: TextSnapshot;
  after: TextSnapshot;
  qualityFlags?: string[];
}

export const SYNTHETIC_METADATA: SyntheticMetadata = {
  logger_schema_version: "web_logger_schema_v0_1",
  session_id: "synthetic_session_web_001",
  participant_local_id: "synthetic_writer_web_001",
  task_id: "synthetic_task_web_freewrite_001",
  prompt_id: "synthetic_prompt_web_001"
};

const SUPPORTED_INPUT_TYPES = new Set<InputType>([
  "insertText",
  "insertLineBreak",
  "insertParagraph",
  "insertFromPaste",
  "deleteContentBackward",
  "deleteContentForward",
  "deleteByCut",
  "historyUndo",
  "historyRedo"
]);

export function snapshotFromTextArea(textarea: HTMLTextAreaElement): TextSnapshot {
  return {
    text: textarea.value,
    selectionStart: textarea.selectionStart,
    selectionEnd: textarea.selectionEnd
  };
}

export function buildRawEvent(input: BuildRawEventInput): RawEvent {
  const qualityFlags = [...(input.qualityFlags ?? [])];
  const inputType = normalizeInputType(input.inputType);
  const textChange = inferTextChange(input.before, input.after, inputType);
  const diffOp = inferDiffOp(input.eventType, input.before, input.after, textChange);

  if (input.inputType && !inputType) {
    qualityFlags.push("unsupported_input_type");
  }

  return omitUndefined({
    ...input.metadata,
    seq: input.seq,
    timestamp_ms: input.timestampMs,
    event_type: input.eventType,
    input_type: inputType,
    is_composing: input.isComposing,
    composition_id: input.compositionId,
    selection_start_before: input.before.selectionStart,
    selection_end_before: input.before.selectionEnd,
    selection_start_after: input.after.selectionStart,
    selection_end_after: input.after.selectionEnd,
    cursor_pos_before: input.before.selectionStart,
    cursor_pos_after: input.after.selectionStart,
    doc_len_before: charCount(input.before.text),
    doc_len_after: charCount(input.after.text),
    inserted_text: textChange.insertedText,
    deleted_text: textChange.deletedText,
    text_hash_before: placeholderHash(input.seq, "before"),
    text_hash_after: placeholderHash(input.seq, "after"),
    diff_op: diffOp,
    quality_flags: qualityFlags
  });
}

export function toJsonl(events: RawEvent[]): string {
  return events.map((event) => JSON.stringify(event)).join("\n") + (events.length ? "\n" : "");
}

export function forbiddenFieldNames(): string[] {
  return ["final_text", "observed_after_text", "gold_label"];
}

function normalizeInputType(inputType: string | null | undefined): InputType | undefined {
  if (!inputType) {
    return undefined;
  }

  return SUPPORTED_INPUT_TYPES.has(inputType as InputType) ? (inputType as InputType) : undefined;
}

function inferTextChange(
  before: TextSnapshot,
  after: TextSnapshot,
  inputType: InputType | undefined
): {
  insertedText?: string;
  deletedText?: string;
} {
  if (before.text === after.text) {
    return {};
  }

  if (inputType === "deleteContentBackward") {
    return inferBackwardDeletion(before, after);
  }

  return inferGenericTextChange(before.text, after.text);
}

function inferBackwardDeletion(
  before: TextSnapshot,
  after: TextSnapshot
): {
  insertedText?: string;
  deletedText?: string;
} {
  if (before.selectionStart !== before.selectionEnd) {
    return omitUndefined({
      deletedText: sliceChars(before.text, before.selectionStart, before.selectionEnd) || undefined
    });
  }

  if (after.selectionStart < before.selectionStart) {
    return omitUndefined({
      deletedText: sliceChars(before.text, after.selectionStart, before.selectionStart) || undefined
    });
  }

  const fallback = inferGenericTextChange(before.text, after.text);
  return omitUndefined({
    deletedText: fallback.deletedText,
    insertedText: fallback.insertedText
  });
}

function inferGenericTextChange(
  before: string,
  after: string
): {
  insertedText?: string;
  deletedText?: string;
} {
  let prefix = 0;
  const beforeChars = [...before];
  const afterChars = [...after];
  while (
    prefix < beforeChars.length &&
    prefix < afterChars.length &&
    beforeChars[prefix] === afterChars[prefix]
  ) {
    prefix += 1;
  }

  let suffix = 0;
  while (
    suffix + prefix < beforeChars.length &&
    suffix + prefix < afterChars.length &&
    beforeChars[beforeChars.length - 1 - suffix] === afterChars[afterChars.length - 1 - suffix]
  ) {
    suffix += 1;
  }

  const deletedText = beforeChars.slice(prefix, beforeChars.length - suffix).join("");
  const insertedText = afterChars.slice(prefix, afterChars.length - suffix).join("");

  return omitUndefined({
    insertedText: insertedText || undefined,
    deletedText: deletedText || undefined
  });
}

function inferDiffOp(
  eventType: EventType,
  before: TextSnapshot,
  after: TextSnapshot,
  textChange: { insertedText?: string; deletedText?: string }
): DiffOp {
  if (
    eventType === "composition_start" ||
    eventType === "composition_update" ||
    eventType === "composition_end"
  ) {
    return "composition";
  }

  if (textChange.insertedText && textChange.deletedText) {
    return "replace";
  }

  if (textChange.insertedText) {
    return "insert";
  }

  if (textChange.deletedText) {
    return "delete";
  }

  if (
    before.selectionStart !== after.selectionStart ||
    before.selectionEnd !== after.selectionEnd
  ) {
    return "selection_only";
  }

  return "no_text_change";
}

function placeholderHash(seq: number, side: "before" | "after"): string {
  return `synthetic_hash_web_${side}_${seq}`;
}

function charCount(value: string): number {
  return [...value].length;
}

function sliceChars(value: string, start: number, end: number): string {
  return [...value].slice(start, end).join("");
}

function omitUndefined<T extends Record<string, unknown>>(value: T): T {
  const result: Record<string, unknown> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (entry !== undefined) {
      result[key] = entry;
    }
  }
  return result as T;
}
