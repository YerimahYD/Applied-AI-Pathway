from pathlib import Path
from src.prompts import load_prompt


def test_load_prompt_reads_text():
    p = Path("prompts/classification_v1.txt")
    text = load_prompt(p)
    assert "{text}" in text
