# Monitoring & Rollback Plan

## Metrics to monitor
- request rate
- error rate
- abstention rate
- average confidence
- latency (p50 / p95)

## Alerts
Trigger investigation if:
- abstention rate > 40%
- error rate > 5%
- latency p95 > 3s

## Rollback strategy
If alerts fire:
1. Disable live LLM calls
2. Switch to stub predictor
3. Continue serving `unknown` safely
4. Investigate offline using frozen outputs

## Post-incident review
- Identify error buckets
- Adjust threshold or prompt
- Re-freeze outputs before redeploy
