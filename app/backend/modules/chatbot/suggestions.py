from __future__ import annotations


class SuggestionEngine:
    def suggest(self, intent: str, context) -> list[str]:
        base = ["Generate Summary", "Explain Dashboard", "Business Insights", "Generate Report"]
        if intent == "fraud_count":
            return ["Show High Risk Transactions", "Highest Risk Merchant", "Generate Summary", "Explain Fraud Distribution"]
        if intent == "highest_risk_transaction":
            return ["Show Only High Risk", "Generate Report", "Explain Recommendations", "Export Top Risk Records"]
        if intent in {"dashboard_explain", "report_explain"}:
            return ["Show Fraud Table", "Business Insights", "Highest Risk Transaction", "Generate Executive Summary"]
        if intent == "time_analysis":
            return ["Monthly Fraud Trend", "Daily Fraud Trend", "Show Top Fraud Transactions", "Generate Summary"]
        if getattr(context, "dashboard_payload", None):
            return base + ["Show Dashboard Cards", "Show Top Fraud Transactions"]
        return base