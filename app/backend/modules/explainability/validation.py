from app.backend.core.exceptions import ProcessingError


def ensure_results_exist(result_count: int) -> None:
    if result_count == 0:
        raise ProcessingError("Run fraud detection before explainability.")
