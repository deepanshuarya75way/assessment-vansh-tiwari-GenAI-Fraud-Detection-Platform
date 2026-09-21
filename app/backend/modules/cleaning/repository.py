from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import CleanedData
from app.backend.modules.uploads.repository import DatasetRepository


class CleanedDataRepository(BaseRepository[CleanedData]):
    model = CleanedData

    def latest_for_dataset(self, dataset_id: str) -> CleanedData | None:
        stmt = (
            select(CleanedData)
            .where(CleanedData.dataset_id == dataset_id)
            .order_by(desc(CleanedData.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)


class CleaningRepository:
    def __init__(self, session) -> None:
        self.session = session
        self.dataset_repository = DatasetRepository(session)
        self.cleaned_repository = CleanedDataRepository(session)

    def latest_dataset(self, project_id: str):
        return self.dataset_repository.latest_for_project(project_id)
