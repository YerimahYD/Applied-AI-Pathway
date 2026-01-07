# Rollout Plan

## Phase 1 — Offline validation
- Run stub evaluation
- Run frozen-output evaluation
- Calibrate threshold

## Phase 2 — Shadow mode
- Call LLM in parallel
- Do not return results to users
- Log predictions and confidence

## Phase 3 — Partial rollout
- Enable for 5–10% of traffic
- Monitor metrics closely

## Phase 4 — Full rollout
- Enable for all traffic
- Continue monitoring and periodic re-evaluation
