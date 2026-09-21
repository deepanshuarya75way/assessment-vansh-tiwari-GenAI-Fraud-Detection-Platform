from __future__ import annotations


class IntentEngine:
    def detect(self, question: str) -> str:
        text = question.lower().strip()
        rules: list[tuple[str, tuple[str, ...]]] = [
            ("fraud_count", ("how many fraud", "fraud count", "fraud transactions", "show fraud")),
            ("high_risk_only", ("only high risk", "high risk only", "show high risk", "high-risk")),
            ("medium_risk_only", ("only medium risk", "medium risk only")),
            ("low_risk_only", ("only low risk", "low risk only")),
            ("highest_risk_transaction", ("highest risk transaction", "top risk transaction", "most risky record")),
            ("highest_risk_merchant", ("highest risk merchant", "most risky merchant", "risky merchant")),
            ("highest_risk_category", ("highest risk category", "most risky category", "risky category")),
            ("highest_risk_location", ("highest risk location", "most risky location", "risky location")),
            ("time_analysis", ("which hour", "monthly fraud trend", "daily fraud trend", "time analysis", "trend")),
            ("dashboard_explain", ("explain dashboard", "dashboard explanation", "explain chart", "explain kpi", "fraud distribution")),
            ("report_explain", ("summarize report", "generate executive summary", "explain recommendations", "report explanation")),
            ("risk_analysis", ("overall risk score", "risk analysis", "risk score")),
            ("business_insight", ("business insight", "business recommendations", "important observations", "fraud pattern")),
            ("dataset_summary", ("dataset summary", "how many rows", "how many columns", "missing values", "duplicate records")),
            ("export_request", ("export", "download", "save as")),
            ("follow_up", ("only", "them", "those", "show them", "export them")),
        ]

        for intent, triggers in rules:
            if any(trigger in text for trigger in triggers):
                return intent
        return "dataset_summary"