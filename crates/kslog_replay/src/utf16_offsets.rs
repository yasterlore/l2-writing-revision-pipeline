//! UTF-16 code unit offset conversion for browser-originated text positions.
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

fn utf16_code_unit_len(text: &str) -> usize {
    text.chars().map(char::len_utf16).sum()
}
