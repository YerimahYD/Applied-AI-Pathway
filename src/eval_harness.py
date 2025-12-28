import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from src.config import load_config
from src.utils import get_logger


@dataclass(frozen=True)
class Example:
    id: str
    input: str
    label: str


def load_jsonl(path: Path) -> List[Example]:
    examples: List[Example] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            examples.append(
                Example(id=obj["id"], input=obj["input"], label=obj["label"])
            )
    return examples


def baseline_predictor(text: str) -> str:
    """
    Intentionally naive baseline. We'll replace with model calls later.
    """
    negative_keywords = [
        "worst", "broke", "disappointed", "terrible", "regret",
        "waste", "poor", "not worth"
    ]
    t = text.lower()
    for kw in negative_keywords:
        if kw in t:
            return "negative"
    return "positive"


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    correct = 0
    total = len(y_true)
    for a, b in zip(y_true, y_pred):
        if a == b:
            correct += 1
    return correct / total if total else 0.0


def run_eval(dataset_path: Path) -> Dict[str, float]:
    cfg = load_config()
    logger = get_logger("eval_harness", cfg.log_level)

    examples = load_jsonl(dataset_path)
    logger.info("Loaded %d examples from %s", len(examples), dataset_path)

    y_true: List[str] = []
    y_pred: List[str] = []

    for ex in examples:
        pred = baseline_predictor(ex.input)
        y_true.append(ex.label)
        y_pred.append(pred)

    report = {
        "n_examples": float(len(examples)),
        "accuracy": accuracy(y_true, y_pred),
    }

    logger.info("Evaluation report: %s", report)
    return report
