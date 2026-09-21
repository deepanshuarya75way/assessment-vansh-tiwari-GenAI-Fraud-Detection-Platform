import pandas as pd

from app.backend.modules.analytics.utility import risk_distribution, timeline_counts, top_counts


def test_top_counts_returns_expected_groups(sample_transactions_df: pd.DataFrame) -> None:
    result = top_counts(sample_transactions_df["merchant"])
    assert result[0]["label"] == "North Axis"
    assert result[0]["value"] == 2


def test_risk_distribution_bins_scores(sample_transactions_df: pd.DataFrame) -> None:
    scores = sample_transactions_df["risk_score"].tolist()
    result = risk_distribution(scores)
    assert {entry["label"] for entry in result} == {"0-25", "26-50", "51-75", "76-100"}
    assert sum(entry["value"] for entry in result) == len(scores)


def test_timeline_counts_returns_month_labels(sample_transactions_df: pd.DataFrame) -> None:
    result = timeline_counts(sample_transactions_df, "created_at")
    assert result[0]["label"] == "2024-01"
    assert len(result) >= 1
