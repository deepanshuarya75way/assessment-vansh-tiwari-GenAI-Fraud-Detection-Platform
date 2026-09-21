from pathlib import Path


def test_frontend_build_entry_exists() -> None:
    entry = Path("app/frontend/index.html")
    assert entry.exists()


def test_dashboard_page_exists() -> None:
    page = Path("app/frontend/pages/Dashboard/DashboardPage.tsx")
    assert page.exists()


def test_reports_page_exists() -> None:
    page = Path("app/frontend/pages/Reports/ReportsPage.tsx")
    assert page.exists()
