from pathlib import Path

from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.modules.validation.model import ValidationArtifact
from app.backend.modules.validation.repository import ValidationRepository
from app.backend.modules.validation.utility import detect_numeric_outliers, validation_messages
from app.backend.modules.validation.validation import ensure_dataset_is_available
from app.backend.utils.storage import read_dataframe, write_json


class ValidationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ValidationRepository(session)
        self.log_service = LogService(session)

    def run(self, project_id: str) -> ValidationArtifact:
        dataset = ensure_dataset_is_available(self.repository.latest_dataset(project_id))
        df = read_dataframe(Path(dataset.raw_parquet_path))
        profile = dataset.schema_profile
        outliers = detect_numeric_outliers(df)
        warnings, issues = validation_messages(profile, outliers)

        artifact = ValidationArtifact(
            row_count=profile["row_count"],
            column_count=profile["column_count"],
            duplicate_rows=profile["duplicate_rows"],
            missing_by_column=profile["missing_by_column"],
            outlier_columns=outliers,
            semantic_columns=profile["semantic_columns"],
            dtypes=profile["dtypes"],
            warnings=warnings,
            issues=issues,
            preview_columns=profile["columns"][:12],
            metadata={"numeric_summary": profile["numeric_summary"]},
        )
        dataset.schema_profile = {**profile, "validation": artifact.__dict__}
        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.VALIDATED
        write_json(Path(dataset.raw_parquet_path).with_name("validation_summary.json"), dataset.schema_profile)
        self.session.commit()
        self.log_service.record(
            "validation.completed",
            "Dataset validation completed.",
            project_id=project_id,
            details={"issues": issues, "warnings": warnings},
        )
        return artifact
