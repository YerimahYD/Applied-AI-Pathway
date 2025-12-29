import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from src.eval_harness import ErrorCase
from src.error_analysis import summarize_buckets


def save_failure_report(
    output_path: Path,
    report: Dict[str, Any],
    errors: List[ErrorCase],
) -> None:
    """
    Save a JSON file containing:
      - summary metrics
      - error bucket summary
      - per-example error cases
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "summary": report,
        "bucket_summary": summarize_buckets(errors),
        "errors": [asdict(e) for e in errors],
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
