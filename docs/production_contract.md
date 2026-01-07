# Production Contract — Sentiment Predictor

## Input
- A single UTF-8 text string
- Max length: 1,000 characters

## Output
One of:
- positive
- negative
- unknown

## Guarantees
- Never returns free-form text
- Never raises an exception to the caller
- Always returns a valid label

## Failure behavior
- If model confidence < threshold → return `unknown`
- If API call fails → return `unknown`
- If parsing fails → return `unknown`

## Latency targets
- P50: < 1.5s
- P95: < 3.0s

## Cost guardrails
- Max requests per minute enforced
- Frozen outputs used for evaluation
