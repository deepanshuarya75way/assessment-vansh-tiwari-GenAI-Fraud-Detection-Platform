from app.backend.core.exceptions import ProcessingError


def ensure_analytics_inputs(has_dataset: bool, has_results: bool) -> None:
    if not has_dataset:
        raise ProcessingError("No dataset is available for analytics.")
    if not has_results:
        raise ProcessingError("Run fraud detection before analytics.")
