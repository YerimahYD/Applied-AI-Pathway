from pathlib import Path

from src.config import load_config
from src.utils import get_logger
from src.eval_harness import run_eval


def run() -> None:
    cfg = load_config()
    logger = get_logger(cfg.project_name, cfg.log_level)

    logger.info("Starting pipeline...")

    dataset_path = Path("data/evals/toy_classification.jsonl")
    report = run_eval(dataset_path)

    logger.info("Final report: %s", report)
    logger.info("Done.")


if __name__ == "__main__":
    run()
