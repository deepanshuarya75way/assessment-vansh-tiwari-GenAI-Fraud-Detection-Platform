from dataclasses import dataclass


@dataclass
class BugReportTemplate:
    title: str
    severity: str
    steps: list[str]
    expected: str
    actual: str


def test_bug_report_template_structure() -> None:
    report = BugReportTemplate(
        title="Dashboard shows wrong metrics for uploaded dataset",
        severity="High",
        steps=["Upload dataset", "Open dashboard", "Apply filters"],
        expected="Metrics match uploaded records",
        actual="Metrics remain from previous session",
    )
    assert report.severity == "High"
    assert len(report.steps) == 3
