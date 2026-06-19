# Data Quality Policy

Data quality checks must begin with synthetic data.

## Raw Input Quality

Raw JSONL input must be treated as untrusted. Future validators should check:

- parse failures
- missing required fields
- unknown fields where disallowed
- timestamp monotonicity where required
- impossible cursor or text states
- oversized payloads
- invalid encodings
- adversarial structures

## Derived Data Quality

Derived artifacts should document:

- source input hash or identifier
- validation status
- transformation version
- no-oracle audit status where applicable

## Testing

Malformed, adversarial, and invalid inputs should be covered when each implementation component is added.
