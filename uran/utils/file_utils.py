from pathlib import Path


def ensure_dir(path: str | Path):
    Path(path).mkdir(parents=True, exist_ok=True)


def read_text_file(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()