from typing import Protocol


class Predictor(Protocol):
    def predict(self, text: str) -> str:
        ...

class KeywordBaselinePredictor:
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
