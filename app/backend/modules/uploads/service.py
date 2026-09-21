from pathlib import Path

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.backend.core.config import get_settings
from app.backend.core.enums import ProjectStatus, UploadStatus
from app.backend.modules.logs.service import LogService
from app.backend.db.enterprise_models import Project, UploadRecord
from app.backend.modules.projects.validation import ensure_project_owner
from app.backend.modules.uploads.model import DatasetRecord
from app.backend.modules.uploads.repository import DatasetRepository, UploadRepository
from app.backend.modules.uploads.utility import preview_from_dataframe
from app.backend.modules.uploads.validation import validate_upload_file
from app.backend.utils.dataframe import (
    coerce_datetime_columns,
    coerce_numeric_candidates,
    dataframe_profile,
    infer_semantic_columns,
    load_dataframe,
    merge_dataframes,
)
from app.backend.utils.storage import save_bytes, sha256_bytes, write_dataframe


class UploadService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.upload_repository = UploadRepository(session)
        self.dataset_repository = DatasetRepository(session)
        self.log_service = LogService(session)
        self.settings = get_settings()

    async def upload_files(
        self,
        project: Project,
        uploads: list[UploadFile],
    ) -> tuple[list[UploadRecord], DatasetRecord, dict]:
        dataframes: list[pd.DataFrame] = []
        persisted_uploads: list[UploadRecord] = []

        for upload in uploads:
            validate_upload_file(upload)
            content = await upload.read()
            checksum = sha256_bytes(content)
            extension = Path(upload.filename or "").suffix.lower()
            target = self.settings.upload_directory / project.id / (checksum + extension)
            save_bytes(target, content)
            frame = load_dataframe(target)
            frame = coerce_numeric_candidates(frame)
            semantic_columns = infer_semantic_columns(frame)
            frame = coerce_datetime_columns(frame, semantic_columns)

            upload_record = UploadRecord(
                project_id=project.id,
                original_filename=upload.filename or target.name,
                stored_path=str(target),
                file_type=extension.lstrip("."),
                checksum=checksum,
                size_bytes=len(content),
                row_count=int(len(frame)),
                column_count=int(len(frame.columns)),
                upload_status=UploadStatus.STORED.value,
            )
            persisted_uploads.append(self.upload_repository.add(upload_record))
            dataframes.append(frame)

        merged = merge_dataframes(dataframes)
        semantic_columns = infer_semantic_columns(merged)
        merged = coerce_datetime_columns(merged, semantic_columns)
        raw_target = self.settings.processed_directory / project.id / "raw_dataset.parquet"
        write_dataframe(merged, raw_target)
        profile = dataframe_profile(merged)
        dataset = DatasetRecord(
            project_id=project.id,
            source_upload_ids=[item.id for item in persisted_uploads],
            raw_parquet_path=str(raw_target),
            schema_profile=profile,
            row_count=int(len(merged)),
            label_column=semantic_columns.get("label"),
            date_column=semantic_columns.get("date"),
            amount_column=semantic_columns.get("amount"),
            category_column=semantic_columns.get("category"),
            merchant_column=semantic_columns.get("merchant"),
            location_column=semantic_columns.get("location"),
        )
        created_dataset = self.dataset_repository.add(dataset)
        project.status = ProjectStatus.UPLOADED
        self.session.commit()

        preview = preview_from_dataframe(merged)
        self.log_service.record(
            "upload.completed",
            "Files uploaded and dataset materialized.",
            project_id=project.id,
            details={"files": [item.original_filename for item in persisted_uploads]},
        )
        return persisted_uploads, created_dataset, {"preview": preview.rows, "columns": preview.columns}

    def list_uploads(self, project_id: str) -> list[UploadRecord]:
        return self.upload_repository.list_for_project(project_id)

    def latest_dataset(self, project_id: str) -> DatasetRecord:
        dataset = self.dataset_repository.latest_for_project(project_id)
        if not dataset:
            raise ValueError("No dataset is available for this project yet.")
        return dataset
