from pathlib import Path

from sqlalchemy.orm import Session

from app.backend.modules.cleaning.repository import CleaningRepository
from app.backend.modules.detection.repository import DetectionRepository
from app.backend.utils.storage import read_dataframe


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.cleaning_repository = CleaningRepository(session)
        self.detection_repository = DetectionRepository(session)

    def latest_assets(self, project_id: str):
        dataset, cleaned = self.detection_repository.latest_dataset_and_cleaned(project_id)
        if not dataset or not cleaned:
            return None, None, []
        frame = read_dataframe(Path(cleaned.cleaned_parquet_path))
        results = self.detection_repository.result_repository.list_for_dataset(dataset.id)
        return dataset, frame, results
