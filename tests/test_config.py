from src.config import load_config


def test_load_config_returns_defaults():
    cfg = load_config()
    assert cfg.project_name == "applied-ai-pathway"
    assert str(cfg.data_dir) == "data"
    assert cfg.log_level == "INFO"
