from pathlib import Path


class TestPlan:
    """Static QA plan describing the enterprise testing strategy for the platform."""

    def __init__(self) -> None:
        self.modules = [
            "Frontend UI",
            "Backend APIs",
            "Database and session isolation",
            "AI agents and analytics",
            "Dashboard and reporting",
            "Security and performance",
        ]
        self.checklist = [
            "Verify responsive navigation and form flows",
            "Validate REST API error handling and authentication",
            "Ensure session-scoped dashboard, reports, and chatbot context",
            "Exercise large and malformed datasets",
            "Confirm logging, observability, and recovery flows",
        ]

    def summary(self) -> str:
        return "Enterprise QA coverage for the fraud detection platform."


def test_test_plan_summary() -> None:
    plan = TestPlan()
    assert plan.summary().startswith("Enterprise QA")
    assert len(plan.modules) >= 6
    assert "Security" in plan.modules[5]
