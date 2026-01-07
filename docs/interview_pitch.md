# 60-Second Interview Pitch

This project is a small sentiment classification system, but the focus is evaluation and decision-making rather than just model accuracy.

I built a reusable evaluation harness that measures accuracy, coverage, and abstention, and I compared a simple baseline against a real LLM under the same metrics.

To manage cost and rate limits, I froze live model outputs and evaluated them offline, which made results reproducible and cheaper to iterate on.

Finally, I calibrated confidence thresholds so the system only returns a label when it’s confident, otherwise it safely abstains. I also documented production guardrails like monitoring, rollback, and safe rollout.

The result is a portfolio project that demonstrates applied AI engineering, not just prompt usage.
