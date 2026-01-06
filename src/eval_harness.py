from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from src.predictors import Predictor


@dataclass(frozen=True)
class EvalExample:
    id: str
    input: str
    label: str

@dataclass(frozen=True)
class ErrorCase:
    id: str
    input: str
    label: str
    prediction: str
    bucket: str


NEGATIVE_KEYWORDS = {
    "terrible", "poor", "bad", "worst", "waste", "regret", "broken",
    "disappointed", "frustrating", "not worth", "awful", "hate",
}
NEGATION_MARKERS = {"not", "no", "never", "n't"}


def _load_jsonl(path: Path) -> List[EvalExample]:
    examples: List[EvalExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            # Expect: {"id": "...", "input": "...", "label": "..."}
            # If your schema differs, adjust these keys.
            ex = EvalExample(
                id=str(obj.get("id", line_no)),
                input=str(obj["input"]),
                label=str(obj["label"]).lower().strip(),
            )
            examples.append(ex)
    return examples


def _bucket_error(ex: EvalExample, pred: str) -> str:
    """
    Rough bucketing for error analysis (matches what you showed earlier).
    Adjust as your taxonomy evolves.
    """
    text = ex.input.lower()

    # If model predicted positive but label is negative and the text contains obvious negative cues
    if ex.label == "negative" and pred == "positive":
        if any(k in text for k in NEGATIVE_KEYWORDS):
            return "keyword_miss_negative"
        if any(n in text.split() for n in NEGATION_MARKERS) or "not " in text:
            return "negation_or_scope"
        return "other_negative_miss"

    # If model predicted negative but label is positive (you can add buckets later)
    if ex.label == "positive" and pred == "negative":
        return "false_negative"

    # unknown-related buckets
    if pred == "unknown":
        return "abstained"

    return "other"


def run_eval(dataset_path: Path, predictor: Predictor) -> Tuple[Dict, List[ErrorCase]]:
    """
    Runs evaluation over the dataset and returns:
      - report: dict of metrics and summaries
      - errors: list of per-example error records
    """
    dataset_path = Path(dataset_path)
    examples = _load_jsonl(dataset_path)

    n_examples = len(examples)
    errors: List[Dict] = []

    n_unknown = 0
    n_known = 0
    n_known_correct = 0

    # Existing-style 
    n_errors = 0

    # Bucket-counts
    bucket_summary: Dict[str, int] = {}

    for ex in examples:
        pred = predictor.predict(ex.input)
        pred = str(pred).lower().strip()

        # Track abstention
        if pred == "unknown":
            n_unknown += 1
        else:
            n_known += 1
            if pred == ex.label:
                n_known_correct += 1

        # Traditional-accuracy-counts
        if pred != ex.label:
            n_errors += 1

            bucket = _bucket_error(ex, pred)
            bucket_summary[bucket] = bucket_summary.get(bucket, 0) + 1

            errors.append(
    ErrorCase(
        id=ex.id,
        input=ex.input,
        label=ex.label,
        prediction=pred,
        bucket=bucket,
    )
)


    # Existing accuracy
    accuracy = (n_examples - n_errors) / n_examples if n_examples else 0.0

    
    abstention_rate = (n_unknown / n_examples) if n_examples else 0.0
    coverage = 1.0 - abstention_rate
    known_accuracy = (n_known_correct / n_known) if n_known > 0 else 0.0
    effective_accuracy = (n_known_correct / n_examples) if n_examples else 0.0

    report: Dict = {
        "n_examples": float(n_examples),
        "accuracy": float(accuracy),           
        "n_errors": float(n_errors),

        
        "abstention_rate": float(abstention_rate),
        "coverage": float(coverage),
        "known_accuracy": float(known_accuracy),
        "effective_accuracy": float(effective_accuracy),

        
        "bucket_summary": bucket_summary,
    }

    return report, errors
