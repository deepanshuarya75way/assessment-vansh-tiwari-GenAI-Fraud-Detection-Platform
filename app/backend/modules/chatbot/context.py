from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.backend.modules.analytics.repository import AnalyticsRepository
from app.backend.modules.chatbot.history import ConversationHistoryManager
from app.backend.modules.detection.repository import DetectionRepository
from app.backend.db.enterprise_models import DashboardSnapshot
from app.backend.modules.projects.service import ProjectService
from app.backend.db.enterprise_models import ReportArtifact
from app.backend.modules.validation.repository import ValidationRepository
from app.backend.utils.storage import read_dataframe


@dataclass(slots=True)
class ChatSessionContext:
    session_id: str
    dataset_id: str | None
    project_id: str
    question: str
    intent: str
    data_frame: pd.DataFrame | None = None
    validation_report: dict[str, Any] | None = None
    detection_results: list[Any] = field(default_factory=list)
    dashboard_payload: dict[str, Any] | None = None
    report_payload: dict[str, Any] | None = None
    analytics_payload: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ChatContextEngine:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.project_service = ProjectService(session)
        self.validation_repository = ValidationRepository(session)
        self.detection_repository = DetectionRepository(session)
        self.analytics_repository = AnalyticsRepository(session)
        self.history_manager = ConversationHistoryManager(session)

    def build(self, session_id: str, current_user, question: str, intent: str) -> ChatSessionContext:
        project = self.project_service.get_project(session_id, current_user)
        dataset = self.validation_repository.latest_dataset(session_id)

        if not dataset:
            return ChatSessionContext(
                session_id=session_id,
                dataset_id=None,
                project_id=project.id,
                question=question,
                intent=intent,
                history=self.history_manager.list_turns(session_id, current_user),
                metadata={"status": "empty_dataset"},
            )

        dataset_pair = self.detection_repository.latest_dataset_and_cleaned(session_id)
        detection_results = list(self.detection_repository.result_repository.list_for_dataset(dataset.id)) if dataset_pair[0] else []

        analytics_dataset, analytics_frame, analytics_results = self.analytics_repository.latest_assets(session_id)
        analytics_payload: dict[str, Any] | None = None
        if analytics_dataset and analytics_frame is not None:
            analytics_payload = {
                "dataset": analytics_dataset.id,
                "row_count": len(analytics_frame),
                "column_count": len(analytics_frame.columns),
                "columns": list(analytics_frame.columns),
                "fraud_count": sum(1 for item in analytics_results if item.predicted_label == "fraud"),
                "review_count": sum(1 for item in analytics_results if item.predicted_label == "review"),
                "safe_count": sum(1 for item in analytics_results if item.predicted_label == "safe"),
            }

        dashboard_snapshot = self.session.scalar(
            select(DashboardSnapshot).where(DashboardSnapshot.project_id == session_id).order_by(desc(DashboardSnapshot.created_at))
        )
        report_snapshot = self.session.scalar(
            select(ReportArtifact).where(ReportArtifact.project_id == session_id).order_by(desc(ReportArtifact.created_at))
        )

        frame = None
        if dataset.raw_parquet_path:
            try:
                frame = read_dataframe(dataset.raw_parquet_path)
            except Exception:
                frame = None

        return ChatSessionContext(
            session_id=session_id,
            dataset_id=dataset.id,
            project_id=project.id,
            question=question,
            intent=intent,
            data_frame=frame,
            validation_report=dataset.schema_profile.get("validation") if dataset.schema_profile else None,
            detection_results=detection_results,
            dashboard_payload=dashboard_snapshot.payload if dashboard_snapshot else None,
            report_payload=report_snapshot.payload if report_snapshot else None,
            analytics_payload=analytics_payload,
            history=self.history_manager.list_turns(session_id, current_user),
            metadata={
                "session_id": session_id,
                "project_id": project.id,
                "dataset_id": dataset.id,
                "dashboard_ready": bool(dashboard_snapshot),
                "report_ready": bool(report_snapshot),
            },
        )