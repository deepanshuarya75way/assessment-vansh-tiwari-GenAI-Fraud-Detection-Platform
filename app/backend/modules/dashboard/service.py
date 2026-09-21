from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.analytics.service import AnalyticsService
from app.backend.db.enterprise_models import DashboardSnapshot
from app.backend.modules.dashboard.repository import DashboardRepository
from app.backend.modules.dashboard.utility import build_filters
from app.backend.modules.dashboard.validation import ensure_dashboard_payload
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DashboardRepository(session)
        self.log_service = LogService(session)

    def generate(self, project_id: str) -> DashboardSnapshot:
        analytics_payload = AnalyticsService(self.session).generate(project_id).payload
        ensure_dashboard_payload(analytics_payload)

        fraud_summary = analytics_payload["fraud_statistics"]
        payload = {
            "kpis": {
                "total_records": analytics_payload["dataset_statistics"]["row_count"],
                "fraud_records": fraud_summary["fraud_count"],
                "review_records": fraud_summary["review_count"],
                "safe_records": fraud_summary["safe_count"],
                "average_risk_score": fraud_summary["average_risk_score"],
            },
            "charts": analytics_payload["charts"],
            "tables": analytics_payload["tables"],
            "filters": build_filters(analytics_payload),
        }

        snapshot = DashboardSnapshot(project_id=project_id, payload=payload)
        created = self.repository.add(snapshot)
        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.DASHBOARD_READY
        self.session.commit()
        self.log_service.record(
            "dashboard.completed",
            "Dashboard payload generated.",
            project_id=project_id,
            details={"kpis": payload["kpis"]},
        )
        return created

    def latest(self, project_id: str) -> DashboardSnapshot | None:
        return self.repository.latest_for_project(project_id)
