from app.backend.core.exceptions import ProcessingError
from app.backend.modules.uploads.model import DatasetRecord


def ensure_dataset_rows(dataset: DatasetRecord) -> None:
    if dataset.row_count <= 0:
        raise ProcessingError("Dataset has no rows to clean.")
