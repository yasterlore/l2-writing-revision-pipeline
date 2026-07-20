//! Shared UTF-16 code unit offset conversion helpers.
//!
//! Browser selection and cursor offsets are UTF-16 code unit offsets. Rust
//! string slicing requires UTF-8 byte offsets at valid char boundaries.

use std::{
    error::Error,
    fmt::{self, Display, Formatter},
    ops::Range,
};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Utf16OffsetError {
    OffsetBeyondUtf16Length { offset: usize, utf16_len: usize },
    OffsetInsideSurrogatePair { offset: usize, utf16_len: usize },
    StartAfterEnd { start: usize, end: usize },
    InvalidBoundary { offset: usize, utf16_len: usize },
    UnsupportedPositionUnit { position_unit: String },
    InternalInvariantViolation,
}

impl Utf16OffsetError {
    pub fn reason_code(&self) -> &'static str {
        match self {
            Self::OffsetBeyondUtf16Length { .. } => "offset_beyond_utf16_length",
            Self::OffsetInsideSurrogatePair { .. } => "offset_inside_surrogate_pair",
            Self::StartAfterEnd { .. } => "start_greater_than_end",
            Self::InvalidBoundary { .. } => "invalid_utf16_boundary",
            Self::UnsupportedPositionUnit { .. } => "unsupported_position_unit",
            Self::InternalInvariantViolation => "internal_invariant_violation",
        }
    }
}

impl Display for Utf16OffsetError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::OffsetBeyondUtf16Length { offset, utf16_len } => write!(
                formatter,
                "UTF-16 offset exceeds UTF-16 length: {offset} > {utf16_len}"
            ),
            Self::OffsetInsideSurrogatePair { offset, utf16_len } => write!(
                formatter,
                "UTF-16 offset is not a scalar boundary: offset {offset}, UTF-16 length {utf16_len}"
            ),
            Self::StartAfterEnd { start, end } => {
                write!(formatter, "UTF-16 range start exceeds end: {start} > {end}")
            }
            Self::InvalidBoundary { offset, utf16_len } => write!(
                formatter,
                "UTF-16 offset is not a valid boundary: offset {offset}, UTF-16 length {utf16_len}"
            ),
            Self::UnsupportedPositionUnit { .. } => {
                write!(formatter, "unsupported position unit")
            }
            Self::InternalInvariantViolation => {
                write!(
                    formatter,
                    "internal UTF-16 offset conversion invariant violation"
                )
            }
        }
    }
}

impl Error for Utf16OffsetError {}

pub fn utf16_code_unit_len(text: &str) -> usize {
    text.chars().map(char::len_utf16).sum()
}

pub fn utf16_code_unit_offset_to_utf8_byte_index(
    text: &str,
    utf16_offset: usize,
) -> Result<usize, Utf16OffsetError> {
    if utf16_offset == 0 {
        return Ok(0);
    }

    let utf16_len = utf16_code_unit_len(text);
    if utf16_offset > utf16_len {
        return Err(Utf16OffsetError::OffsetBeyondUtf16Length {
            offset: utf16_offset,
            utf16_len,
        });
    }

    let mut cumulative_utf16 = 0usize;
    let mut cumulative_utf8 = 0usize;

    for (_, ch) in text.char_indices() {
        cumulative_utf16 += ch.len_utf16();
        cumulative_utf8 += ch.len_utf8();

        if cumulative_utf16 == utf16_offset {
            return Ok(cumulative_utf8);
        }

        if cumulative_utf16 > utf16_offset {
            return Err(Utf16OffsetError::OffsetInsideSurrogatePair {
                offset: utf16_offset,
                utf16_len,
            });
        }
    }

    if cumulative_utf16 == utf16_len && cumulative_utf8 == text.len() {
        Err(Utf16OffsetError::InvalidBoundary {
            offset: utf16_offset,
            utf16_len,
        })
    } else {
        Err(Utf16OffsetError::InternalInvariantViolation)
    }
}

pub fn utf16_code_unit_range_to_utf8_byte_range(
    text: &str,
    utf16_start: usize,
    utf16_end: usize,
) -> Result<Range<usize>, Utf16OffsetError> {
    if utf16_start > utf16_end {
        return Err(Utf16OffsetError::StartAfterEnd {
            start: utf16_start,
            end: utf16_end,
        });
    }

    let start_byte = utf16_code_unit_offset_to_utf8_byte_index(text, utf16_start)?;
    let end_byte = utf16_code_unit_offset_to_utf8_byte_index(text, utf16_end)?;
    Ok(start_byte..end_byte)
}

#[cfg(test)]
mod tests {
    use super::{
        utf16_code_unit_len, utf16_code_unit_offset_to_utf8_byte_index,
        utf16_code_unit_range_to_utf8_byte_range, Utf16OffsetError,
    };

    #[test]
    fn utf16_ascii_offsets_map_one_to_one() {
        let text = "abc";

        assert_eq!(utf16_code_unit_len(text), 3);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 0), Ok(0));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(1));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(2));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 3), Ok(3));
    }

    #[test]
    fn utf16_japanese_offsets_map_to_utf8_boundaries() {
        let text = "あい";

        assert_eq!(utf16_code_unit_len(text), 2);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(3));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(6));
    }

    #[test]
    fn utf16_mixed_japanese_and_emoji_offsets_map_correctly() {
        let text = "Aあ😀B";

        assert_eq!(utf16_code_unit_len(text), 5);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(1));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(4));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 4), Ok(8));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 5), Ok(9));
    }

    #[test]
    fn utf16_full_width_text_maps_correctly() {
        let text = "ＡＢ";

        assert_eq!(utf16_code_unit_len(text), 2);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(3));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(6));
    }

    #[test]
    fn utf16_emoji_surrogate_pair_accepts_only_scalar_boundaries() {
        let text = "😀";

        assert_eq!(utf16_code_unit_len(text), 2);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 0), Ok(0));
        assert!(matches!(
            utf16_code_unit_offset_to_utf8_byte_index(text, 1),
            Err(Utf16OffsetError::OffsetInsideSurrogatePair {
                offset: 1,
                utf16_len: 2
            })
        ));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(4));
    }

    #[test]
    fn utf16_offset_beyond_length_fails_closed() {
        let err = utf16_code_unit_offset_to_utf8_byte_index("ab", 3)
            .expect_err("offset beyond UTF-16 length should fail");

        assert_eq!(err.reason_code(), "offset_beyond_utf16_length");
    }

    #[test]
    fn utf16_start_greater_than_end_fails_closed() {
        let err = utf16_code_unit_range_to_utf8_byte_range("abc", 2, 1)
            .expect_err("range start after end should fail");

        assert_eq!(err.reason_code(), "start_greater_than_end");
    }

    #[test]
    fn utf16_empty_range_at_valid_boundary_is_allowed() {
        assert_eq!(
            utf16_code_unit_range_to_utf8_byte_range("あい", 1, 1),
            Ok(3..3)
        );
    }

    #[test]
    fn utf16_empty_string_offset_zero_maps_to_byte_zero() {
        assert_eq!(utf16_code_unit_len(""), 0);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index("", 0), Ok(0));
    }

    #[test]
    fn utf16_end_offset_maps_to_text_length() {
        let text = "a😀\n";

        assert_eq!(
            utf16_code_unit_offset_to_utf8_byte_index(text, utf16_code_unit_len(text)),
            Ok(text.len())
        );
    }

    #[test]
    fn utf16_combining_sequence_remains_unnormalized() {
        let text = "e\u{301}";

        assert_eq!(utf16_code_unit_len(text), 2);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(1));
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 2), Ok(3));
    }

    #[test]
    fn utf16_precomposed_accent_remains_distinct() {
        let text = "é";

        assert_eq!(utf16_code_unit_len(text), 1);
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 1), Ok(2));
    }

    #[test]
    fn utf16_line_endings_trailing_newline_and_tab_are_preserved() {
        let text = "a\tb\r\n";

        assert_eq!(utf16_code_unit_len(text), 5);
        assert_eq!(
            utf16_code_unit_range_to_utf8_byte_range(text, 1, 4),
            Ok(1..4)
        );
        assert_eq!(utf16_code_unit_offset_to_utf8_byte_index(text, 5), Ok(5));
    }

    #[test]
    fn utf16_reason_code_strings_are_stable() {
        assert_eq!(
            Utf16OffsetError::OffsetBeyondUtf16Length {
                offset: 4,
                utf16_len: 3
            }
            .reason_code(),
            "offset_beyond_utf16_length"
        );
        assert_eq!(
            Utf16OffsetError::OffsetInsideSurrogatePair {
                offset: 1,
                utf16_len: 2
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
                utf16_len: 1
            }
            .reason_code(),
            "invalid_utf16_boundary"
        );
    }

    #[test]
    fn utf16_error_output_does_not_include_source_text() {
        let text = "secret😀text";
        let err = utf16_code_unit_offset_to_utf8_byte_index(text, 7)
            .expect_err("surrogate-internal offset should fail");
        let message = err.to_string();

        assert!(!message.contains(text));
        assert!(!message.contains("secret"));
        assert_eq!(err.reason_code(), "offset_inside_surrogate_pair");
    }
}
