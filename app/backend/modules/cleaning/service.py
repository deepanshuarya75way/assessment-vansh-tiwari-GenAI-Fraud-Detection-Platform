from pathlib import Path

from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.db.enterprise_models import CleanedData
from app.backend.modules.cleaning.repository import CleaningRepository
from app.backend.modules.cleaning.utility import clean_dataframe
from app.backend.modules.cleaning.validation import ensure_dataset_rows
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.storage import read_dataframe, write_dataframe, write_json


class CleaningService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = CleaningRepository(session)
        self.log_service = LogService(session)

    def run(self, project_id: str) -> CleanedData:
        dataset = self.repository.latest_dataset(project_id)
        if not dataset:
            raise ValueError("No dataset is available for cleaning.")
        ensure_dataset_rows(dataset)
        df = read_dataframe(Path(dataset.raw_parquet_path))
        cleaned_df, summary = clean_dataframe(df)
        target = Path(dataset.raw_parquet_path).with_name("cleaned_dataset.parquet")
        write_dataframe(cleaned_df, target)
        write_json(target.with_name("cleaning_summary.json"), summary)

        cleaned_record = CleanedData(
            dataset_id=dataset.id,
            cleaned_parquet_path=str(target),
            cleaning_summary=summary,
            preprocessing_summary=None,
        )
        created = self.repository.cleaned_repository.add(cleaned_record)
        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.CLEANED
        self.session.commit()
        self.log_service.record(
            "cleaning.completed",
            "Dataset cleaning completed.",
            project_id=project_id,
            details=summary,
        )
        return created

    def latest(self, project_id: str) -> CleanedData | None:
        dataset = self.repository.latest_dataset(project_id)
        if not dataset:
            return None
        return self.repository.cleaned_repository.latest_for_dataset(dataset.id)
