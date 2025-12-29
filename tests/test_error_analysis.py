from src.eval_harness import ErrorCase
from src.error_analysis import summarize_buckets


def test_summarize_buckets_counts_errors():
    errors = [
        ErrorCase(id="1", input="Not worth it", label="negative", prediction="positive"),
        ErrorCase(id="2", input="Worst ever", label="negative", prediction="positive"),
    ]
    buckets = summarize_buckets(errors)
    assert sum(buckets.values()) == 2
