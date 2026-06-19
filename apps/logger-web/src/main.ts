import "./styles.css";
import {
  buildRawEvent,
  snapshotFromTextArea,
  SYNTHETIC_METADATA,
  toJsonl,
  type EventType,
  type RawEvent,
  type TextSnapshot
} from "./rawEvent";

const textarea = requireElement<HTMLTextAreaElement>("#writingArea");
const downloadButton = requireElement<HTMLButtonElement>("#downloadButton");
const clearButton = requireElement<HTMLButtonElement>("#clearButton");
const eventCount = requireElement<HTMLElement>("#eventCount");
const lastEventType = requireElement<HTMLElement>("#lastEventType");
const statusText = requireElement<HTMLElement>("#statusText");

let events: RawEvent[] = [];
let seq = 1;
let lastSnapshot: TextSnapshot = snapshotFromTextArea(textarea);
let activeCompositionId: string | undefined;
let compositionCounter = 1;

function recordEvent(
  eventType: EventType,
  before: TextSnapshot,
  after: TextSnapshot,
  options: {
    inputType?: string | null;
    isComposing?: boolean;
    compositionId?: string;
    qualityFlags?: string[];
  } = {}
): void {
  const event = buildRawEvent({
    metadata: SYNTHETIC_METADATA,
    seq,
    timestampMs: Date.now(),
    eventType,
    inputType: options.inputType,
    isComposing: options.isComposing ?? Boolean(activeCompositionId),
    compositionId: options.compositionId ?? activeCompositionId,
    before,
    after,
    qualityFlags: options.qualityFlags
  });

  events = [...events, event];
  seq += 1;
  lastSnapshot = after;
  updateSummary(event.event_type);
}

function updateSummary(lastType: string): void {
  eventCount.textContent = String(events.length);
  lastEventType.textContent = lastType;
  statusText.textContent = events.length
    ? "Recording synthetic raw events in memory."
    : "Ready. Synthetic metadata only.";
}

function currentSnapshot(): TextSnapshot {
  return snapshotFromTextArea(textarea);
}

function inputEventType(event: Event): string | null {
  return "inputType" in event && typeof event.inputType === "string" ? event.inputType : null;
}

function inputIsComposing(event: Event): boolean {
  return "isComposing" in event && event.isComposing === true;
}

function requireElement<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Required UI element not found: ${selector}`);
  }
  return element;
}

textarea.addEventListener("focus", () => {
  const snapshot = currentSnapshot();
  recordEvent("focus", lastSnapshot, snapshot, { isComposing: false });
});

textarea.addEventListener("blur", () => {
  const snapshot = currentSnapshot();
  recordEvent("blur", lastSnapshot, snapshot, { isComposing: false });
});

textarea.addEventListener("keydown", () => {
  const snapshot = currentSnapshot();
  recordEvent("key_down", snapshot, snapshot);
});

textarea.addEventListener("keyup", () => {
  const snapshot = currentSnapshot();
  recordEvent("key_up", lastSnapshot, snapshot);
});

textarea.addEventListener("beforeinput", (event) => {
  const snapshot = currentSnapshot();
  recordEvent("before_input", snapshot, snapshot, {
    inputType: inputEventType(event),
    isComposing: inputIsComposing(event)
  });
});

textarea.addEventListener("input", (event) => {
  const snapshot = currentSnapshot();
  recordEvent("input", lastSnapshot, snapshot, {
    inputType: inputEventType(event),
    isComposing: inputIsComposing(event)
  });
});

textarea.addEventListener("compositionstart", () => {
  activeCompositionId = `synthetic_composition_web_${compositionCounter}`;
  compositionCounter += 1;
  const snapshot = currentSnapshot();
  recordEvent("composition_start", lastSnapshot, snapshot, {
    compositionId: activeCompositionId,
    isComposing: true
  });
});

textarea.addEventListener("compositionupdate", () => {
  const snapshot = currentSnapshot();
  recordEvent("composition_update", lastSnapshot, snapshot, {
    compositionId: activeCompositionId,
    isComposing: true
  });
});

textarea.addEventListener("compositionend", () => {
  const snapshot = currentSnapshot();
  const compositionId = activeCompositionId;
  recordEvent("composition_end", lastSnapshot, snapshot, {
    compositionId,
    isComposing: false
  });
  activeCompositionId = undefined;
});

textarea.addEventListener("paste", () => {
  const snapshot = currentSnapshot();
  recordEvent("paste", snapshot, snapshot, {
    inputType: "insertFromPaste",
    qualityFlags: ["paste_payload_not_logged_on_paste_event"]
  });
});

document.addEventListener("selectionchange", () => {
  if (document.activeElement !== textarea) {
    return;
  }
  const snapshot = currentSnapshot();
  recordEvent("selection_change", lastSnapshot, snapshot);
});

downloadButton.addEventListener("click", () => {
  const blob = new Blob([toJsonl(events)], { type: "application/jsonl;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${SYNTHETIC_METADATA.session_id}.raw_events.jsonl`;
  link.rel = "noopener";
  link.click();
  URL.revokeObjectURL(url);
});

clearButton.addEventListener("click", () => {
  events = [];
  seq = 1;
  textarea.value = "";
  lastSnapshot = currentSnapshot();
  activeCompositionId = undefined;
  updateSummary("none");
});

updateSummary("none");
