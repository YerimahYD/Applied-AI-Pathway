import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from src.eval_harness import ErrorCase


def save_failure_report(output_path: Path, report: Dict[str, Any], errors: List[ErrorCase]) -> None:
    """
    Save a JSON file containing:
      - summary metrics (report)
      - per-example error cases (errors)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "summary": report,
        "errors": [asdict(e) for e in errors],
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
