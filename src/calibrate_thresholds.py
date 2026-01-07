# src/calibrate_thresholds.py

from __future__ import annotations

import json
from pathlib import Path


THRESHOLDS = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]


def main() -> None:
    frozen_dir = Path("data/frozen")

    candidates = sorted(
        frozen_dir.glob("openai_gpt-4.1-mini_sentiment_sample15*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError("No frozen files found")

    path = candidates[0]
    print("Using frozen file:", path)

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    print(f"\nExamples: {len(rows)}\n")

    for t in THRESHOLDS:
        n = len(rows)
        covered = 0
        correct = 0

        for r in rows:
            conf = r.get("confidence")
            gold = r["gold_label"]
            pred = r.get("pred_label")

            if conf is None or conf < t:
                continue

            covered += 1
            if pred == gold:
                correct += 1

        coverage = covered / n if n else 0.0
        accuracy = (correct / covered) if covered else 0.0
        effective_accuracy = correct / n if n else 0.0

        print(
            f"threshold={t:.2f} | "
            f"coverage={coverage:.2f} | "
            f"accuracy={accuracy:.2f} | "
            f"effective_accuracy={effective_accuracy:.2f}"
        )


if __name__ == "__main__":
    main()

