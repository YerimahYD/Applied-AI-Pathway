# src/predictors.py

from __future__ import annotations

import random
import re
import time
from pathlib import Path
from typing import Protocol

from openai import OpenAI
from openai import RateLimitError


# Predictor protocol
class Predictor(Protocol):
    def predict(self, text: str) -> str:
        ...

# STUB PREDICTOR (offline evals)
class PromptedStubLLMPredictor:
    """
    Deterministic stub predictor for evaluation loops.
    Uses keyword rules to simulate an LLM.
    """

    def __init__(self, prompt_path: Path, latency_ms: int = 0):
        self.prompt_path = Path(prompt_path)
        self.latency_ms = latency_ms

    def predict(self, text: str) -> str:
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)

        t = text.lower()

        negative_keywords = [
            "terrible", "waste", "poor", "bad", "awful", "disappointed",
            "broke", "broken", "unhappy", "frustrating", "regret",
            "not worth", "worst", "useless", "faulty"
        ]

        for kw in negative_keywords:
            if kw in t:
                return "negative"

        return "positive"


# OPENAI PREDICTOR (live sampling only)
class OpenAILLMPredictor:
    """
    OpenAI-backed predictor.
    Use ONLY for small sampling, not large eval loops.
    """

    def __init__(
        self,
        prompt_path: Path,
        model: str = "gpt-4.1-mini",
        threshold: float = 0.75,
        rpm_limit: int = 3,
        max_retries: int = 8,
    ):
        self.prompt_path = Path(prompt_path)
        self.model = model
        self.threshold = float(threshold)

        self.rpm_limit = int(rpm_limit)
        self.min_interval_s = 60.0 / max(self.rpm_limit, 1) + 1.0

        self.max_retries = int(max_retries)

        self._client = OpenAI()
        self._last_call_ts = 0.0
        self._total_calls = 0

    def usage(self) -> dict:
        return {
            "prompt_path": str(self.prompt_path),
            "total_calls": self._total_calls,
            "threshold": self.threshold,
            "rpm_limit": self.rpm_limit,
        }

    def _throttle(self) -> None:
        now = time.time()
        elapsed = now - self._last_call_ts
        if elapsed < self.min_interval_s:
            time.sleep(self.min_interval_s - elapsed)
        self._last_call_ts = time.time()

    def _call_openai(self, prompt: str):
        attempt = 0
        while True:
            self._throttle()
            try:
                return self._client.responses.create(
                    model=self.model,
                    input=prompt,
                    temperature=0.0,
                )
            except RateLimitError:
                attempt += 1
                if attempt > self.max_retries:
                    raise
                time.sleep(min(60.0, 2 ** attempt) + random.uniform(0.0, 1.0))

    def predict(self, text: str) -> str:
        template = self.prompt_path.read_text(encoding="utf-8")
        prompt = template.format(text=text)

        self._total_calls += 1
        resp = self._call_openai(prompt)

        out = (resp.output_text or "").strip()

        m_label = re.search(
            r"label:\s*(positive|negative|unknown)",
            out,
            re.IGNORECASE,
        )
        label = m_label.group(1).lower() if m_label else None

        m_conf = re.search(
            r"confidence:\s*([0-9]+(?:[.,][0-9]+)?)",
            out,
            re.IGNORECASE,
        )
        conf = float(m_conf.group(1).replace(",", ".")) if m_conf else None

        if label not in {"positive", "negative", "unknown"}:
            raise ValueError(f"Invalid label from model output: {out!r}")

        if conf is None or not (0.0 <= conf <= 1.0):
            return "unknown"

        if conf < self.threshold:
            return "unknown"

        return label
