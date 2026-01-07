# src/eval_frozen.py

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict


NEGATIVE_KEYWORDS = {
    "terrible", "poor", "bad", "worst", "waste", "regret", "broken",
    "disappointed", "frustrating", "not worth", "awful", "hate",
}

NEGATION_MARKERS = {"not", "no", "never", "n't"}


def bucket_error(text: str, gold: str, pred: str) -> str:
    t = text.lower()

    if pred == "unknown":
        return "abstained"

    if gold == "negative" and pred == "positive":
        if any(k in t for k in NEGATIVE_KEYWORDS):
            return "keyword_miss_negative"
        if any(n in t.split() for n in NEGATION_MARKERS) or "not " in t:
            return "negation_or_scope"
        return "other_negative_miss"

    if gold == "positive" and pred == "negative":
        return "false_negative"

    return "other"


def main() -> None:
    frozen_dir = Path("data/frozen")

    if not frozen_dir.exists():
        raise FileNotFoundError("data/frozen/ directory does not exist")

    candidates = sorted(
        frozen_dir.glob("openai_gpt-4.1-mini_sentiment_sample15*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError("No frozen output files found in data/frozen/")

    frozen_path = candidates[0]
    print("Using frozen file:", frozen_path)

    rows = []
    with frozen_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    n_examples = len(rows)
    n_unknown = 0
    n_known = 0
    n_known_correct = 0
    n_errors = 0

    buckets = Counter()

    for r in rows:
        gold = str(r["gold_label"]).strip().lower()
        pred = (r.get("pred_label") or "unknown").strip().lower()
        text = str(r["input"])

        if pred == "unknown":
            n_unknown += 1
        else:
            n_known += 1
            if pred == gold:
                n_known_correct += 1

        if pred != gold:
            n_errors += 1
            b = bucket_error(text, gold, pred)
            buckets[b] += 1

    accuracy = (n_examples - n_errors) / n_examples if n_examples else 0.0
    abstention_rate = (n_unknown / n_examples) if n_examples else 0.0
    coverage = 1.0 - abstention_rate
    known_accuracy = (n_known_correct / n_known) if n_known else 0.0
    effective_accuracy = (n_known_correct / n_examples) if n_examples else 0.0

    report: Dict = {
        "n_examples": float(n_examples),
        "accuracy": float(accuracy),
        "n_errors": float(n_errors),
        "abstention_rate": float(abstention_rate),
        "coverage": float(coverage),
        "known_accuracy": float(known_accuracy),
        "effective_accuracy": float(effective_accuracy),
        "bucket_summary": dict(buckets),
        "frozen_path": str(frozen_path),
    }

    print("\nFinal report:", report)


if __name__ == "__main__":
    main()

