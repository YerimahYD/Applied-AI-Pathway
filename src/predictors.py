from typing import Protocol


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
