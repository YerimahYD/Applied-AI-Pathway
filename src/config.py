from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "applied-ai-pathway"
    data_dir: Path = Path("data")
    log_level: str = "INFO"


def load_config() -> AppConfig:
    """
    Central place to load configuration.
    Later we can extend this to read from env vars or a YAML file.
    """
    return AppConfig()
