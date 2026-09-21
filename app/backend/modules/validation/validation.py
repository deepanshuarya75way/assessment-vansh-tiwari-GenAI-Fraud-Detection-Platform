from app.backend.core.exceptions import ProcessingError
from app.backend.modules.uploads.model import DatasetRecord


def ensure_dataset_is_available(dataset: DatasetRecord | None) -> DatasetRecord:
    if not dataset:
        raise ProcessingError("No dataset is available for this project.")
    return dataset
