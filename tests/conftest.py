import os
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.modules.analytics.utility import risk_distribution, timeline_counts, top_counts


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def sample_transactions_df():
    return pd.DataFrame(
        {
            "transaction_id": ["txn-1", "txn-2", "txn-3"],
            "amount": [1200, 25000, 850],
            "merchant": ["North Axis", "North Axis", "BluePeak"],
            "category": ["Wire Transfer", "Wire Transfer", "Card Payment"],
            "location": ["New York", "London", "Chicago"],
            "created_at": pd.to_datetime(["2024-01-03", "2024-02-14", "2024-02-20"]),
            "risk_score": [88, 74, 31],
        }
    )


@pytest.fixture()
def fraud_dataset_path(tmp_path: Path) -> Path:
    dataset_path = tmp_path / "fraud_dataset.csv"
    dataset_path.write_text(
        "transaction_id,amount,merchant,category,location,created_at,risk_score\n"
        "txn-1,1200,North Axis,Wire Transfer,New York,2024-01-03,88\n"
        "txn-2,25000,North Axis,Wire Transfer,London,2024-02-14,74\n"
        "txn-3,850,BluePeak,Card Payment,Chicago,2024-02-20,31\n",
        encoding="utf-8",
    )
    return dataset_path


@pytest.fixture()
def invalid_dataset_path(tmp_path: Path) -> Path:
    dataset_path = tmp_path / "invalid_dataset.csv"
    dataset_path.write_text(
        "transaction_id,amount,merchant\n"
        "txn-1,1200,North Axis\n",
        encoding="utf-8",
    )
    return dataset_path


@pytest.fixture()
def session_payload() -> dict[str, str]:
    return {"session_id": "qa-session-001", "project_id": "proj-qa-001"}
