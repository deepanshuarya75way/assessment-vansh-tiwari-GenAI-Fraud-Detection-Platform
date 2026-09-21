from sqlalchemy import delete, desc, select

from app.backend.common.repository import BaseRepository
from app.backend.modules.cleaning.repository import CleaningRepository
from app.backend.db.enterprise_models import FraudResult


class FraudResultRepository(BaseRepository[FraudResult]):
    model = FraudResult

    def clear_for_dataset(self, dataset_id: str) -> None:
        self.session.execute(delete(FraudResult).where(FraudResult.dataset_id == dataset_id))

    def list_for_dataset(self, dataset_id: str) -> list[FraudResult]:
        stmt = select(FraudResult).where(FraudResult.dataset_id == dataset_id).order_by(desc(FraudResult.risk_score))
        return list(self.session.scalars(stmt))


class DetectionRepository:
    def __init__(self, session) -> None:
        self.session = session
        self.cleaning_repository = CleaningRepository(session)
        self.result_repository = FraudResultRepository(session)

    def latest_dataset_and_cleaned(self, project_id: str):
        dataset = self.cleaning_repository.latest_dataset(project_id)
        if not dataset:
            return None, None
        return dataset, self.cleaning_repository.cleaned_repository.latest_for_dataset(dataset.id)
