[# Model Comparison: Stub vs LLM (Evaluation-First)

This document compares two predictors evaluated under the same harness:

1. A deterministic keyword-based stub (baseline)
2. A real LLM with confidence-based abstention (frozen outputs)

The goal is not to maximize accuracy, but to understand *failure modes* and *decision trade-offs*.

---

## Models compared

### 1) Stub predictor
- Type: rule-based (keyword heuristics)
- Purpose: baseline + eval harness validation
- Strengths:
  - Fast
  - Deterministic
  - Full coverage
- Weaknesses:
  - Misses subtle sentiment
  - Fails on negation and implicit negativity

### 2) LLM predictor (frozen outputs)
- Type: instruction-following LLM
- Purpose: semantic understanding
- Strengths:
  - Better handling of nuance
  - Confidence signal enables abstention
- Weaknesses:
  - Rate-limited
  - Requires calibration
  - Can still mis-handle scope/negation

---

## Evaluation results

### Stub predictor (60 examples)

| Metric | Value |
|------|------|
| Accuracy | 0.80 |
| Coverage | 1.00 |
| Errors | 12 |
| Abstention | 0.00 |

Top error buckets:
- other_negative_miss
- negation_or_scope

---

### LLM predictor (frozen sample)

| Metric | Value |
|------|------|
| Accuracy | (see frozen eval output) |
| Coverage | (depends on threshold) |
| Abstention | enabled |

Notes:
- Even with limited samples, the LLM shows stronger semantic understanding.
- Confidence enables explicit trade-offs between coverage and accuracy.

---

## Key takeaways

1. **Evaluation harness matters more than the model**
   - Same metrics, same buckets, comparable analysis

2. **Accuracy alone is misleading**
   - Stub achieves 80% but fails systematically
   - LLM may have similar accuracy but different error types

3. **Confidence enables safer deployment**
   - Abstention prevents low-confidence errors
   - Threshold selection is a policy decision

4. **Offline evaluation is essential**
   - Frozen outputs allow reproducible analysis under strict API limits

---

## Conclusion

A simple baseline can perform surprisingly well, but only structured evaluation reveals *why* it fails.

The LLM improves semantic understanding, but still requires:
- calibration
- abstention policies
- careful evaluation

This project demonstrates an evaluation-first approach to Applied AI.
