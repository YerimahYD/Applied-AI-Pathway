from pathlib import Path

from src.reporting import save_failure_report
from src.eval_harness import ErrorCase


def test_save_failure_report_writes_file(tmp_path: Path):
    out = tmp_path / "report.json"
    report = {"accuracy": 1.0, "n_examples": 1.0, "n_errors": 0.0}
    errors = [ErrorCase(id="1", input="x", label="positive", prediction="negative")]

    save_failure_report(out, report, errors)

    assert out.exists()
    assert out.read_text(encoding="utf-8").strip() != ""
