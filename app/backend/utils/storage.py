import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.backend.core.config import get_settings


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_bytes(target: Path, content: bytes) -> Path:
    ensure_directory(target.parent)
    target.write_bytes(content)
    return target


def write_json(target: Path, payload: dict[str, Any]) -> Path:
    ensure_directory(target.parent)
    target.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return target


def write_dataframe(df: pd.DataFrame, target: Path) -> Path:
    ensure_directory(target.parent)
    df.to_parquet(target, index=False)
    return target


def read_dataframe(target: Path) -> pd.DataFrame:
    return pd.read_parquet(target)


def project_storage_path(project_id: str, *parts: str) -> Path:
    settings = get_settings()
    base_path = settings.processed_directory / project_id
    ensure_directory(base_path)
    return base_path.joinpath(*parts)
