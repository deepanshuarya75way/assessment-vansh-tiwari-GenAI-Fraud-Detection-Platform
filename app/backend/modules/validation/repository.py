from sqlalchemy.orm import Session

from app.backend.modules.uploads.model import DatasetRecord
from app.backend.modules.uploads.repository import DatasetRepository


class ValidationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.dataset_repository = DatasetRepository(session)

    def latest_dataset(self, project_id: str) -> DatasetRecord | None:
        return self.dataset_repository.latest_for_project(project_id)
