from src.predictors import KeywordBaselinePredictor, StubLLMPredictor

from pathlib import Path

from src.config import load_config
from src.utils import get_logger
from src.eval_harness import run_eval
from src.reporting import save_failure_report


def run() -> None:
    cfg = load_config()
    logger = get_logger(cfg.project_name, cfg.log_level)

    logger.info("Starting pipeline...")

    dataset_path = Path("data/evals/toy_classification.jsonl")

    predictor = StubLLMPredictor(latency_ms=30)

    report, errors = run_eval(dataset_path, predictor)

    if hasattr(predictor, "usage"):
        logger.info("Model usage stats: %s", predictor.usage())

    output_path = Path("data/reports/toy_classification_failure_report.json")
    save_failure_report(output_path, report, errors)

    logger.info("Saved failure report to: %s", output_path)
    logger.info("Final report: %s", report)
    logger.info("Done.")


if __name__ == "__main__":
    run()
