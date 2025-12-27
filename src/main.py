from src.config import load_config
from src.utils import get_logger


def run() -> None:
    cfg = load_config()
    logger = get_logger(cfg.project_name, cfg.log_level)

    logger.info("Starting pipeline...")
    logger.info("Config loaded: project_name=%s, data_dir=%s, log_level=%s",
                cfg.project_name, cfg.data_dir, cfg.log_level)
    logger.info("Done.")


if __name__ == "__main__":
    run()
