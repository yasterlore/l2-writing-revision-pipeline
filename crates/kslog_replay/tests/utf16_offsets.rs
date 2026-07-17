use kslog_replay::utf16_offsets::{
    utf16_code_unit_offset_to_utf8_byte_index, utf16_code_unit_range_to_utf8_byte_range,
    Utf16OffsetError,
};
use serde_json::Value;

#[test]
fn empty_string_offset_zero_maps_to_byte_zero() {
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("", 0), Ok(0));
    assert_eq!(utf16_code_unit_range_to_utf8_byte_range("", 0, 0), Ok(0..0));
}

#[test]
fn ascii_offsets_map_one_to_one() {
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("abcde", 3), Ok(3));
    assert_eq!(
        utf16_code_unit_range_to_utf8_byte_range("abcde", 1, 4),
        Ok(1..4)
    );
}

#[test]
fn japanese_text_maps_utf16_offsets_to_utf8_bytes() {
    let text = "あい";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 0), Ok(0));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(3));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(6));
    assert_eq!(
        utf16_code_unit_range_to_utf8_byte_range(text, 0, 1),
        Ok(0..3)
    );
}

#[test]
fn full_width_text_maps_utf16_offsets_to_utf8_bytes() {
    let text = "Ａ１";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(3));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(6));
}

#[test]
fn emoji_surrogate_pair_accepts_only_scalar_boundaries() {
    let text = "😀";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 0), Ok(0));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(4));

    let error = utf16_code_unit_offset_to_utf8_byte_index(text, 1).unwrap_err();
    assert_eq!(
        error,
        Utf16OffsetError::OffsetInsideSurrogatePair {
            offset: 1,
            utf16_len: 2
        }
    );
    assert_eq!(error.reason_code(), "offset_inside_surrogate_pair");
}

#[test]
fn mixed_japanese_and_emoji_offsets_map_correctly() {
    let text = "あ😀い";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(3));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 3), Ok(7));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 4), Ok(10));
    assert_eq!(
        utf16_code_unit_range_to_utf8_byte_range(text, 1, 3),
        Ok(3..7)
    );

    let error = utf16_code_unit_offset_to_utf8_byte_index(text, 2).unwrap_err();
    assert_eq!(error.reason_code(), "offset_inside_surrogate_pair");
}

#[test]
fn combining_sequence_remains_unnormalized() {
    let text = "e\u{301}";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(1));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(3));
    assert_eq!(
        utf16_code_unit_range_to_utf8_byte_range(text, 1, 2),
        Ok(1..3)
    );
}

#[test]
fn precomposed_accent_remains_distinct() {
    let text = "é";

    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(2));
}

#[test]
fn line_endings_trailing_newline_and_tab_are_preserved() {
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("a\nb", 2), Ok(2));
    assert_eq!(
        utf16_code_unit_offset_to_utf8_byte_index("a\r\nb", 3),
        Ok(3)
    );
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("a\n", 2), Ok(2));
    assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("a\tb", 2), Ok(2));
}

#[test]
fn beyond_utf16_length_fails_closed() {
    let error = utf16_code_unit_offset_to_utf8_byte_index("abc", 4).unwrap_err();

    assert_eq!(
        error,
        Utf16OffsetError::OffsetBeyondUtf16Length {
            offset: 4,
            utf16_len: 3
        }
    );
    assert_eq!(error.reason_code(), "offset_beyond_utf16_length");
}

#[test]
fn start_greater_than_end_fails_closed() {
    let error = utf16_code_unit_range_to_utf8_byte_range("abc", 2, 1).unwrap_err();

    assert_eq!(error, Utf16OffsetError::StartAfterEnd { start: 2, end: 1 });
    assert_eq!(error.reason_code(), "start_greater_than_end");
}

#[test]
fn end_offset_maps_to_text_len() {
    let text = "あ😀";

    assert_eq!(
        utf16_code_unit_offset_to_utf8_byte_index(text, 3),
        Ok(text.len())
    );
}

#[test]
fn range_conversion_allows_empty_range_at_valid_boundary() {
    assert_eq!(
        utf16_code_unit_range_to_utf8_byte_range("あ😀い", 3, 3),
        Ok(7..7)
    );
}

#[test]
fn reason_codes_are_stable() {
    assert_eq!(
        Utf16OffsetError::OffsetBeyondUtf16Length {
            offset: 9,
            utf16_len: 2,
        }
        .reason_code(),
        "offset_beyond_utf16_length"
    );
    assert_eq!(
        Utf16OffsetError::OffsetInsideSurrogatePair {
            offset: 1,
            utf16_len: 2,
        }
        .reason_code(),
        "offset_inside_surrogate_pair"
    );
    assert_eq!(
        Utf16OffsetError::StartAfterEnd { start: 2, end: 1 }.reason_code(),
        "start_greater_than_end"
    );
    assert_eq!(
        Utf16OffsetError::InvalidBoundary {
            offset: 1,
            utf16_len: 2,
        }
        .reason_code(),
        "invalid_utf16_boundary"
    );
    assert_eq!(
        Utf16OffsetError::UnsupportedPositionUnit {
            position_unit: "grapheme_cluster".to_string(),
        }
        .reason_code(),
        "unsupported_position_unit"
    );
    assert_eq!(
        Utf16OffsetError::InternalInvariantViolation.reason_code(),
        "internal_invariant_violation"
    );
}

#[test]
fn error_output_does_not_include_source_text() {
    let source = "diagnostic_probe";
    let error = utf16_code_unit_offset_to_utf8_byte_index(source, 99).unwrap_err();

    assert!(!format!("{error}").contains(source));
    assert!(!format!("{error:?}").contains(source));
}

#[test]
fn shared_unicode_hash_vectors_valid_offsets_match_expected_bytes() {
    let fixture = load_fixture();
    let vectors = fixture["vectors"]
        .as_array()
        .expect("vectors must be an array");

    for vector in vectors {
        let vector_id = vector["vector_id"].as_str().expect("vector_id is required");
        let text = vector["source_text"]
            .as_str()
            .expect("source_text is required");
        assert_eq!(
            utf16_code_unit_len(text),
            value_as_usize(&vector["utf16_code_unit_length"]),
            "UTF-16 length mismatch for {vector_id}"
        );
        assert_eq!(
            text.len(),
            value_as_usize(&vector["utf8_byte_length"]),
            "UTF-8 byte length mismatch for {vector_id}"
        );

        let offset_cases = vector["offset_cases"]
            .as_array()
            .expect("offset_cases must be an array");
        for case in offset_cases {
            let case_id = case["case_id"].as_str().expect("case_id is required");
            let start = value_as_usize(&case["utf16_start"]);
            let end = value_as_usize(&case["utf16_end"]);
            let expected_start = value_as_usize(&case["expected_utf8_start_byte"]);
            let expected_end = value_as_usize(&case["expected_utf8_end_byte"]);

            let range = utf16_code_unit_range_to_utf8_byte_range(text, start, end).unwrap_or_else(
                |error| {
                    panic!(
                        "valid offset case failed for {vector_id}/{case_id}: {}",
                        error.reason_code()
                    )
                },
            );
            assert_eq!(
                range,
                expected_start..expected_end,
                "byte range mismatch for {vector_id}/{case_id}"
            );
        }
    }
}

#[test]
fn shared_unicode_hash_vectors_expected_failures_fail_closed() {
    let fixture = load_fixture();
    let vectors = fixture["vectors"]
        .as_array()
        .expect("vectors must be an array");
    let mut checked_failures = 0usize;

    for vector in vectors {
        let vector_id = vector["vector_id"].as_str().expect("vector_id is required");
        let text = vector["source_text"]
            .as_str()
            .expect("source_text is required");
        let expected_failures = vector["expected_failures"]
            .as_array()
            .expect("expected_failures must be an array");

        for failure in expected_failures {
            let failure_id = failure["failure_id"]
                .as_str()
                .expect("failure_id is required");
            let start = value_as_usize(&failure["utf16_start"]);
            let end = value_as_usize(&failure["utf16_end"]);

            assert!(
                utf16_code_unit_range_to_utf8_byte_range(text, start, end).is_err(),
                "expected failure unexpectedly passed for {vector_id}/{failure_id}"
            );
            checked_failures += 1;
        }
    }

    assert_eq!(checked_failures, 11);
}

fn load_fixture() -> Value {
    serde_json::from_str(include_str!(
        "../../../tests/fixtures/web_logger_unicode_hash_vectors/vectors.json"
    ))
    .expect("fixture JSON parse failed")
}

fn utf16_code_unit_len(text: &str) -> usize {
    text.chars().map(char::len_utf16).sum()
}

fn value_as_usize(value: &Value) -> usize {
    value
        .as_u64()
        .and_then(|value| usize::try_from(value).ok())
        .expect("fixture numeric field must fit usize")
}
