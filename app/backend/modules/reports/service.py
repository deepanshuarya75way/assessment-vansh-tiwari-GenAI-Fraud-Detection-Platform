from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.analytics.service import AnalyticsService
from app.backend.modules.dashboard.service import DashboardService
from app.backend.modules.detection.repository import DetectionRepository
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.db.enterprise_models import ReportArtifact
from app.backend.modules.reports.repository import ReportRepository
from app.backend.modules.reports.utility import recommendations_from_analytics
from app.backend.modules.reports.validation import ensure_report_inputs


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ReportRepository(session)
        self.log_service = LogService(session)

    def generate(self, project_id: str, current_user) -> ReportArtifact:
        ProjectService(self.session).get_project(project_id, current_user)

        analytics_payload = AnalyticsService(self.session).generate(project_id).payload
        dashboard_snapshot = DashboardService(self.session).latest(project_id)
        if not dashboard_snapshot:
            dashboard_snapshot = DashboardService(self.session).generate(project_id)

        ensure_report_inputs(analytics_payload, dashboard_snapshot.payload)

        dataset, _ = DetectionRepository(self.session).latest_dataset_and_cleaned(project_id)
        results = []
        if dataset:
            results = DetectionRepository(self.session).result_repository.list_for_dataset(dataset.id)
        top_risk = max(results, key=lambda item: item.risk_score, default=None)

        payload = {
            "executive_summary": {
                "total_records": analytics_payload["dataset_statistics"]["row_count"],
                "fraud_records": analytics_payload["fraud_statistics"]["fraud_count"],
                "review_records": analytics_payload["fraud_statistics"]["review_count"],
                "safe_records": analytics_payload["fraud_statistics"]["safe_count"],
                "average_risk_score": analytics_payload["fraud_statistics"]["average_risk_score"],
            },
            "technical_summary": {
                "strategy": dashboard_snapshot.payload.get("strategy", "dataset_driven_analysis"),
                "metrics": analytics_payload["fraud_statistics"],
                "thresholds": analytics_payload.get("thresholds", {}),
            },
            "fraud_summary": {
                "top_risk_row": top_risk.row_identifier if top_risk else None,
                "top_risk_score": top_risk.risk_score if top_risk else None,
                "top_risk_label": top_risk.predicted_label if top_risk else None,
            },
            "dashboard_summary": dashboard_snapshot.payload,
            "recommendations": recommendations_from_analytics(analytics_payload),
            "charts": analytics_payload["charts"],
            "tables": analytics_payload["tables"],
        }

        artifact = self.repository.add(ReportArtifact(project_id=project_id, payload=payload))
        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.REPORT_READY
        self.session.commit()
        self.log_service.record(
            "report.completed",
            "PDF-ready JSON report generated.",
            project_id=project_id,
            user_id=current_user.id,
            details={"report_id": artifact.id},
        )
        return artifact

    def latest(self, project_id: str) -> ReportArtifact | None:
        return self.repository.latest_for_project(project_id)

    def history(self, project_id: str) -> list[ReportArtifact]:
        return self.repository.list_for_project(project_id)