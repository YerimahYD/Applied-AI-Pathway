# src/freeze_outputs.py

from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set

from openai import OpenAI, RateLimitError


@dataclass
class FrozenRow:
    id: str
    input: str
    gold_label: str
    raw_output: str
    pred_label: Optional[str]
    confidence: Optional[float]


def parse_output(out: str) -> tuple[Optional[str], Optional[float]]:
    m_label = re.search(r"label:\s*(positive|negative|unknown)", out, re.IGNORECASE)
    label = m_label.group(1).lower() if m_label else None

    m_conf = re.search(r"confidence:\s*([0-9]+(?:[.,][0-9]+)?)", out, re.IGNORECASE)
    conf = float(m_conf.group(1).replace(",", ".")) if m_conf else None

    return label, conf


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_done_ids(out_path: Path) -> Set[str]:
    done: Set[str] = set()
    if not out_path.exists():
        return done
    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "id" in obj:
                    done.add(str(obj["id"]))
            except json.JSONDecodeError:
                continue
    return done


def main() -> None:
    # Inputs
    dataset_path = Path("data/evals/sentiment_eval_v1_sample15.jsonl")
    prompt_path = Path("prompts/classification_v1.txt")

    # Output (stable filename so resume works)
    out_dir = Path("data/frozen")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "openai_gpt-4.1-mini_sentiment_sample15_frozen.jsonl"

    # How many examples to freeze this run (start small to avoid RPM pain)
    # Example usage: MAX_EXAMPLES=5 python3 -m src.freeze_outputs
    max_examples = int(os.environ.get("MAX_EXAMPLES", "5"))

    # OpenAI setup
    client = OpenAI()
    model = "gpt-4.1-mini"

    # Very conservative pacing for 3 RPM rolling window
    INITIAL_COOLDOWN_S = 75.0      # clears rolling window reliably
    MIN_INTERVAL_S = 25.0          # safe spacing between successful calls
    RETRY_SLEEP_S = 25.0           # fixed sleep on 429 (no exponential spam)

    template = prompt_path.read_text(encoding="utf-8")
    data = load_jsonl(dataset_path)

    done_ids = load_done_ids(out_path)

    print("Dataset:", dataset_path)
    print("Prompt:", prompt_path)
    print("Output:", out_path)
    print("Model:", model)
    print("Already frozen:", len(done_ids))
    print("MAX_EXAMPLES this run:", max_examples)
    print("Initial cooldown (s):", INITIAL_COOLDOWN_S)
    print("Min interval (s):", MIN_INTERVAL_S)
    print("Retry sleep (s):", RETRY_SLEEP_S)
    print("----")

    # Cool down first to clear any prior calls in the rolling RPM window
    if len(done_ids) == 0:
        print(f"Cooling down for {INITIAL_COOLDOWN_S:.0f}s to clear RPM window...")
        time.sleep(INITIAL_COOLDOWN_S)

    last_success_ts = 0.0
    written = 0

    for ex in data:
        if written >= max_examples:
            break

        ex_id = str(ex["id"])
        if ex_id in done_ids:
            continue

        text = str(ex["input"])
        gold = str(ex["label"]).strip().lower()

        # Ensure spacing from last successful call
        now = time.time()
        elapsed = now - last_success_ts
        if elapsed < MIN_INTERVAL_S:
            time.sleep(MIN_INTERVAL_S - elapsed)

        prompt = template.format(text=text)

        # Retry forever on 429 (fixed sleep), because this is a rolling window constraint
        while True:
            try:
                resp = client.responses.create(
                    model=model,
                    input=prompt,
                    temperature=0.0,
                )
                last_success_ts = time.time()
                break
            except RateLimitError as e:
                # Honor the server hint if present in the message; otherwise fixed sleep.
                msg = str(e)
                hint = None
                m = re.search(r"try again in (\d+)s", msg, re.IGNORECASE)
                if m:
                    hint = float(m.group(1))
                sleep_s = (hint if hint is not None else RETRY_SLEEP_S) + random.uniform(0.0, 2.0)
                print(f"[{ex_id}] 429 rate limit. Sleeping {sleep_s:.1f}s then retrying...")
                time.sleep(sleep_s)

        out = (resp.output_text or "").strip()
        pred_label, conf = parse_output(out)

        frozen = FrozenRow(
            id=ex_id,
            input=text,
            gold_label=gold,
            raw_output=out,
            pred_label=pred_label,
            confidence=conf,
        )

        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(frozen.__dict__, ensure_ascii=False) + "\n")

        done_ids.add(ex_id)
        written += 1

        print(f"[{ex_id}] gold={gold} pred={pred_label} conf={conf}")

    print("\nWrote", written, "new rows.")
    print("Frozen file:", out_path)
    print("Total frozen rows:", len(done_ids))


if __name__ == "__main__":
    main()
