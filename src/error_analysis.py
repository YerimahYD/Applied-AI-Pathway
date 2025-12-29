from dataclasses import asdict
from typing import Dict, List

from src.eval_harness import ErrorCase


def bucket_error(error: ErrorCase) -> str:
    """
    Simple, explainable bucketing rules.
    We'll refine these into more robust heuristics later.
    """
    text = error.input.lower()

    # Baseline keyword heuristic can miss negation or subtlety
    negation_terms = ["not", "never", "no"]
    if any(n in text for n in negation_terms):
        return "negation_or_scope"

    # Short texts tend to be ambiguous
    if len(text.split()) <= 4:
        return "too_short_ambiguous"

    # Keyword miss: label negative but we predicted positive
    if error.label == "negative" and error.prediction == "positive":
        return "keyword_miss_negative"

    # Keyword over-trigger: label positive but we predicted negative
    if error.label == "positive" and error.prediction == "negative":
        return "keyword_overtrigger"

    return "other"


def summarize_buckets(errors: List[ErrorCase]) -> Dict[str, int]:
    buckets: Dict[str, int] = {}
    for e in errors:
        b = bucket_error(e)
        buckets[b] = buckets.get(b, 0) + 1
    return buckets
