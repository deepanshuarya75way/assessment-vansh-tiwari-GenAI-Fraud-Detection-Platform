from app.backend.core.exceptions import ProcessingError


def ensure_dashboard_payload(payload: dict) -> None:
    if not payload:
        raise ProcessingError("Analytics payload is required to generate the dashboard.")
