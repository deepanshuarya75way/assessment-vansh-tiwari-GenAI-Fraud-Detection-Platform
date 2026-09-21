from app.backend.core.exceptions import ProcessingError


def ensure_report_inputs(analytics_payload: dict, dashboard_payload: dict | None) -> None:
    if not analytics_payload:
        raise ProcessingError("Analytics data is required to generate a report.")
    if not dashboard_payload:
        raise ProcessingError("Dashboard data is required to generate a report.")
