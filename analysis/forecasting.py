"""
Time Series Sales Forecasting Module
Leverages Holt-Winters Triple Exponential Smoothing & SARIMAX (Statsmodels)
to produce forward projections, confidence intervals, and evaluation metrics (MAE, RMSE, MAPE).
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose


def run_sales_forecasting(
    parquet_path: str = "sales-intelligence-platform/data/processed/orders_transformed.parquet",
    output_dir: str = "sales-intelligence-platform/data/processed",
    forecast_months: int = 6,
) -> dict:
    """Trains time-series models on monthly revenue and generates forward forecasts."""
    print("Executing Time Series Sales Forecasting with Statsmodels...")
    df = pd.read_parquet(parquet_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Monthly aggregation (standard for retail executive planning)
    monthly_sales = (
        df.set_index("order_date")
        .resample("ME")["sales"]
        .sum()
        .reset_index()
        .rename(columns={"order_date": "ds", "sales": "y"})
    )
    monthly_sales["ds"] = monthly_sales["ds"].dt.to_period("M").dt.to_timestamp()

    # Out-of-sample backtesting: last 6 months as validation
    train_size = len(monthly_sales) - 6
    train_data = monthly_sales.iloc[:train_size].copy()
    test_data = monthly_sales.iloc[train_size:].copy()

    # Fit Holt-Winters model with additive trend and seasonality (12-month period)
    model_eval = ExponentialSmoothing(
        train_data["y"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)

    test_preds = model_eval.forecast(6)
    actuals = test_data["y"].values
    preds = np.maximum(test_preds.values, 0)

    # Calculate Evaluation Metrics
    mae = float(np.mean(np.abs(actuals - preds)))
    rmse = float(np.sqrt(np.mean((actuals - preds) ** 2)))
    mape = float(np.mean(np.abs((actuals - preds) / actuals)) * 100)
    accuracy_pct = round(max(0.0, 100.0 - mape), 2)

    # Full Model Fit on all historical data
    full_model = ExponentialSmoothing(
        monthly_sales["y"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)

    # In-sample fitted values
    in_sample_fitted = full_model.fittedvalues

    # Future forecast
    future_preds = full_model.forecast(forecast_months)

    # Create future date range
    last_date = monthly_sales["ds"].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_months, freq="MS")

    # Standard error estimation for confidence intervals
    residual_std = float(np.std(full_model.resid))
    # 95% Confidence Interval multiplier (1.96 * residual_std)
    margin = 1.96 * residual_std

    # Prepare complete historical + future timeline dataframe
    hist_records = pd.DataFrame({
        "ds": monthly_sales["ds"],
        "y": monthly_sales["y"],
        "yhat": in_sample_fitted,
        "yhat_lower": np.maximum(in_sample_fitted - margin, 0),
        "yhat_upper": in_sample_fitted + margin,
        "is_forecast": 0,
    })

    future_records = pd.DataFrame({
        "ds": future_dates,
        "y": np.nan,
        "yhat": np.maximum(future_preds.values, 0),
        "yhat_lower": np.maximum(future_preds.values - margin, 0),
        "yhat_upper": future_preds.values + margin,
        "is_forecast": 1,
    })

    forecast_df = pd.concat([hist_records, future_records], ignore_index=True)

    # Seasonal Decomposition (12 month seasonal cycle)
    decomp = seasonal_decompose(monthly_sales.set_index("ds")["y"], model="additive", period=12)
    decomp_df = pd.DataFrame({
        "ds": monthly_sales["ds"],
        "trend": decomp.trend.values,
        "seasonal": decomp.seasonal.values,
        "residual": decomp.resid.values,
    })

    out_path = Path(output_dir)
    forecast_df.to_parquet(out_path / "sales_forecast_results.parquet", index=False)
    forecast_df.to_csv(out_path / "sales_forecast_results.csv", index=False)
    decomp_df.to_parquet(out_path / "sales_decomposition.parquet", index=False)

    metrics = {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "accuracy_pct": accuracy_pct,
        "total_historical_months": len(monthly_sales),
        "forecast_horizon_months": forecast_months,
    }

    with open(out_path / "forecast_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Forecasting successfully completed!")
    print(f"Validation Metrics: MAE = ${mae:,.2f}, RMSE = ${rmse:,.2f}, MAPE = {mape:.2f}%, Accuracy = {accuracy_pct}%")
    return metrics


if __name__ == "__main__":
    run_sales_forecasting()
