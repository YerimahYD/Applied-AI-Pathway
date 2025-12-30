from pathlib import Path
from typing import Dict, Protocol

from src.prompts import load_prompt



class Predictor(Protocol):
    def predict(self, text: str) -> str:
        ...

class KeywordBaselinePredictor:
    import time
from typing import Dict


class StubLLMPredictor:
    """
    Simulates an LLM call without external dependencies.
    Useful for testing system behavior.
    """

    def __init__(self, latency_ms: int = 50, cost_per_call: float = 0.00001):
        self.latency_ms = latency_ms
        self.cost_per_call = cost_per_call
        self.total_cost = 0.0
        self.total_calls = 0

    def predict(self, text: str) -> str:
        # Simulate latency
        time.sleep(self.latency_ms / 1000.0)

        # Track usage
        self.total_calls += 1
        self.total_cost += self.cost_per_call

        # Very naive "model" logic
        if "not" in text.lower() or "worst" in text.lower():
            return "negative"
        return "positive"

    def usage(self) -> Dict[str, float]:
        return {
            "total_calls": self.total_calls,
            "total_cost": round(self.total_cost, 6),
        }

    def predict(self, text: str) -> str:
        negative_keywords = [
            "worst", "broke", "disappointed", "terrible",
            "regret", "waste", "poor", "not worth",
        ]
        t = text.lower()
        for kw in negative_keywords:
            if kw in t:
                return "negative"
        return "positive"

class PromptedStubLLMPredictor:
    """
    Simulates a prompt + model pipeline (no external API).
    Uses different heuristics depending on prompt 'strength'.
    """

    def __init__(self, prompt_path: Path, latency_ms: int = 30, cost_per_call: float = 0.00001):
        self.prompt_path = prompt_path
        self.prompt = load_prompt(prompt_path)
        self.latency_ms = latency_ms
        self.cost_per_call = cost_per_call
        self.total_cost = 0.0
        self.total_calls = 0

        # Basic signal: stronger prompt tends to do better (simulate that)
        self.is_v2 = "Rules:" in self.prompt

    def predict(self, text: str) -> str:
        import time

        time.sleep(self.latency_ms / 1000.0)
        self.total_calls += 1
        self.total_cost += self.cost_per_call

        t = text.lower()

        # v1 is intentionally weaker
        if not self.is_v2:
            if "worst" in t or "broke" in t:
                return "negative"
            return "positive"

        # v2 is stronger: broader negative cues + negation
        negative_cues = [
            "worst", "broke", "disappointed", "terrible", "regret", "waste", "poor", "not worth",
            "hate", "awful", "bad", "refund", "never again"
        ]
        if any(cue in t for cue in negative_cues):
            return "negative"

        # simple negation handling
        if "not" in t and ("good" in t or "great" in t or "worth" in t):
            return "negative"

        return "positive"

    def usage(self) -> dict:
        return {
            "prompt_path": str(self.prompt_path),
            "total_calls": self.total_calls,
            "total_cost": round(self.total_cost, 6),
        }
