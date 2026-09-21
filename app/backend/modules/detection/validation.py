from app.backend.core.exceptions import ProcessingError


def ensure_detection_sample_size(sample_size: int) -> None:
    if sample_size < 10:
        raise ProcessingError("At least 10 rows are required to run fraud detection.")
