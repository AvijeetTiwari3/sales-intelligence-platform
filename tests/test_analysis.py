"""
Unit Tests for Analytical and Forecasting Modules
"""

import json
from pathlib import Path
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_rfm_segmentation_output():
    rfm_path = ROOT_DIR / "data" / "processed" / "customer_rfm.parquet"
    assert rfm_path.exists(), "customer_rfm.parquet missing"

    df = pd.read_parquet(rfm_path)
    assert len(df) == 793, f"Expected 793 customers in RFM, got {len(df)}"

    expected_cols = {"customer_id", "recency", "frequency", "monetary", "rfm_segment"}
    assert expected_cols.issubset(set(df.columns))

    expected_segments = {"Champions", "Loyal Customers", "At-Risk", "Hibernating"}
    assert set(df["rfm_segment"].unique()).issubset(expected_segments)


def test_cohort_matrix_output():
    cohort_path = ROOT_DIR / "data" / "processed" / "cohort_retention_matrix.parquet"
    assert cohort_path.exists(), "cohort_retention_matrix.parquet missing"

    df = pd.read_parquet(cohort_path)
    # Check that Month 0 is 100% retention
    assert (df[0] == 100.0).all(), "Month 0 retention must be 100%"


def test_forecast_output():
    forecast_path = ROOT_DIR / "data" / "processed" / "sales_forecast_results.parquet"
    metrics_path = ROOT_DIR / "data" / "processed" / "forecast_metrics.json"

    assert forecast_path.exists(), "sales_forecast_results.parquet missing"
    assert metrics_path.exists(), "forecast_metrics.json missing"

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    assert "accuracy_pct" in metrics
    assert "mape" in metrics
    assert metrics["forecast_horizon_months"] == 6


if __name__ == "__main__":
    pytest.main([__file__])
