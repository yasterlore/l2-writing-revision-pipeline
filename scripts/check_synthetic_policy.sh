#!/usr/bin/env sh
set -eu

echo "Checking for private or real data paths..."

private_paths=$(
  find . \
    -path './.git' -prune -o \
    -path './target' -prune -o \
    \( \
      -path './private_data' -o \
      -path './private_data/*' -o \
      -path './real_data' -o \
      -path './real_data/*' -o \
      -path './participant_data' -o \
      -path './participant_data/*' -o \
      -name '*.real.jsonl' -o \
      -name '*.private.jsonl' -o \
      -name '.env' \
    \) -print
)

if [ -n "$private_paths" ]; then
  echo "Private or real-data-looking paths are present:" >&2
  printf '%s\n' "$private_paths" >&2
  exit 1
fi

echo "Checking valid synthetic fixture/example data files for no-oracle forbidden fields..."

check_files=$(
  find examples/synthetic tests/fixtures/synthetic/raw_events/valid tests/fixtures/synthetic/safe_views/valid tests/fixtures/synthetic/candidate_sets/valid tests/fixtures/synthetic/candidate_features/valid \
    -type f \( -name '*.jsonl' -o -name '*.json' \) -print 2>/dev/null || true
)

if [ -n "$check_files" ]; then
  if grep -n -E 'final_text|observed_after_text|gold_label|teacher_correction|answer_key|future_context' $check_files; then
    echo "Forbidden no-oracle field found in public example data or valid fixtures." >&2
    echo "Note: invalid fixtures and Markdown documentation are intentionally excluded from this check." >&2
    exit 1
  fi
fi

echo "Synthetic policy checks passed."
