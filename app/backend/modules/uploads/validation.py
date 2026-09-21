from pathlib import Path

from fastapi import UploadFile

from app.backend.core.config import get_settings
from app.backend.core.exceptions import ProcessingError


def validate_upload_file(upload: UploadFile) -> None:
    settings = get_settings()
    extension = Path(upload.filename or "").suffix.lower().lstrip(".")
    if extension not in settings.allowed_file_extensions:
        raise ProcessingError(f"Unsupported file extension '{extension}'.")
