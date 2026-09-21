from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.modules.uploads.model import DatasetRecord
from app.backend.db.enterprise_models import UploadRecord


class UploadRepository(BaseRepository[UploadRecord]):
    model = UploadRecord

    def list_for_project(self, project_id: str) -> list[UploadRecord]:
        stmt = select(UploadRecord).where(UploadRecord.project_id == project_id).order_by(desc(UploadRecord.created_at))
        return list(self.session.scalars(stmt))


class DatasetRepository(BaseRepository[DatasetRecord]):
    model = DatasetRecord

    def latest_for_project(self, project_id: str) -> DatasetRecord | None:
        stmt = (
            select(DatasetRecord)
            .where(DatasetRecord.project_id == project_id)
            .order_by(desc(DatasetRecord.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)
