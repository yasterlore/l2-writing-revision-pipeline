//! Compatibility re-export for shared UTF-16 code unit offset helpers.
//!
//! The helper source-of-truth lives in `kslog_schema::utf16_offsets` so replay
//! and future validator Phase 2 checks can share the same boundary behavior.

pub use kslog_schema::utf16_offsets::{
    utf16_code_unit_len, utf16_code_unit_offset_to_utf8_byte_index,
    utf16_code_unit_range_to_utf8_byte_range, Utf16OffsetError,
};
