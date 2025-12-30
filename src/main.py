from datetime import datetime
from pathlib import Path
from src.config import load_config
from src.utils import get_logger
from src.eval_harness import run_eval
from src.reporting import save_failure_report
from src.predictors import PromptedStubLLMPredictor


def run() -> None:
    cfg = load_config()
    logger = get_logger(cfg.project_name, cfg.log_level)

    logger.info("Starting pipeline...")

    dataset_path = Path("data/evals/toy_classification.jsonl")

    # Switch between v1 and v2 to compare prompt versions
    prompt_path = Path("prompts/classification_v1.txt")
    predictor = PromptedStubLLMPredictor(prompt_path=prompt_path, latency_ms=30)

    report, errors = run_eval(dataset_path, predictor)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_id = prompt_path.stem  # classification_v1 or classification_v2
    output_path = Path(f"data/reports/{prompt_id}_failure_report_{ts}.json")

    save_failure_report(output_path, report, errors)

    if hasattr(predictor, "usage"):
        logger.info("Model usage stats: %s", predictor.usage())

    logger.info("Saved failure report to: %s", output_path)
    logger.info("Final report: %s", report)
    logger.info("Done.")


if __name__ == "__main__":
    run()
