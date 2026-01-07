# Applied-AI-Pathway
This repo documents my applied AI pathway

## Project Highlights

- Built an evaluation-first sentiment classification pipeline (not just inference)
- Implemented confidence-based abstention (`unknown`) for safer predictions
- Separated live LLM calls from offline evaluation using frozen outputs
- Designed error bucketing to diagnose systematic failures (negation, implicit negativity)
- Calibrated confidence thresholds to balance accuracy vs coverage
- Added production-oriented docs: monitoring, rollback, and rollout plans


# Applied AI Pathway

This repository documents my Applied AI execution pathway.

## Purpose
The goal of this project is to build production-minded applied AI systems with strong evaluation, reliability, and engineering discipline.

## Roadmap
- LLM evaluation framework
- Retrieval-Augmented Generation (RAG) system
- Scaling, reliability, and failure analysis

# Applied AI Pathway — Sentiment Classification Eval Harness

This repository contains a small, evaluation-first sentiment classification project built as part of an Applied AI internship-style pathway.

The focus is not only “getting predictions”, but building a repeatable evaluation workflow:
- run metrics consistently
- inspect error buckets
- calibrate confidence thresholds
- separate live model calls from offline evaluation

---

## What this project does

Given an input sentence, the system predicts one of:
- `positive`
- `negative`
- `unknown` (abstain)

The core idea is: **only return a label when confidence is high enough**. Otherwise, abstain.

---

## Repository structure (key files)

- `src/main.py`  
  Runs the evaluation pipeline (loads dataset → predicts → scores → writes failure report).

- `src/eval_harness.py`  
  Evaluation loop + metrics (accuracy, coverage, abstention rate) + error buckets.

- `src/predictors.py`  
  Predictors:
  - `PromptedStubLLMPredictor` (fast, deterministic; used for eval loops)
  - `OpenAILLMPredictor` (live API; used only for small sampling)

- `data/evals/sentiment_eval_v1.jsonl`  
  Expanded evaluation dataset (60 examples).

- `src/freeze_outputs.py`  
  “Freeze” live model outputs to disk (JSONL) for reproducible offline evaluation.

- `src/eval_frozen.py`  
  Evaluate frozen outputs offline (no API calls).

- `src/calibrate_thresholds.py`  
  Sweep confidence thresholds and report coverage/accuracy trade-offs.

---

## Evaluation approach (important)

This repo uses a **3-layer evaluation approach**:

### 1) Stub evaluation (fast + deterministic)
Use `PromptedStubLLMPredictor` to validate:
- evaluation loop correctness
- error bucketing
- reporting logic
- dataset handling

### 2) Frozen model evaluation (reproducible)
Use `src/freeze_outputs.py` to collect a small number of live model outputs, then evaluate them offline using `src/eval_frozen.py`.

This avoids:
- rate-limit instability
- non-reproducible runs
- unnecessary spend during iteration

### 3) Confidence calibration (threshold selection)
Use `src/calibrate_thresholds.py` to simulate thresholds and choose a defensible operating point.

Policy:
- if confidence ≥ threshold → return label
- else → return `unknown`

---

## How to run

### A) Run the main evaluation (stub mode)
From repo root:

## License
MIT

- [Model comparison](docs/model_comparison.md)


```bash
python3 -m src.main

