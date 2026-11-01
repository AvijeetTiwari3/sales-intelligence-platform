"""
Predictive Sales Forecasting & Time Series Decomposition Page
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.components.charts import DARK_LAYOUT, plot_forecast_timeline
from dashboard.components.kpi_cards import render_kpi_card


@st.cache_data
def load_forecast_data():
    forecast_path = ROOT_DIR / "data" / "processed" / "sales_forecast_results.parquet"
    metrics_path = ROOT_DIR / "data" / "processed" / "forecast_metrics.json"
    decomp_path = ROOT_DIR / "data" / "processed" / "sales_decomposition.parquet"

    if not forecast_path.exists() or not metrics_path.exists():
        from analysis.forecasting import run_sales_forecasting
        run_sales_forecasting()

    forecast_df = pd.read_parquet(forecast_path)
    decomp_df = pd.read_parquet(decomp_path)
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    return forecast_df, decomp_df, metrics


def main():
    st.set_page_config(page_title="Sales Forecasting | Sales Intelligence", page_icon="🔮", layout="wide")
    forecast_df, decomp_df, metrics = load_forecast_data()

    st.title("🔮 Predictive Revenue Forecasting & Seasonal Dynamics")
    st.caption("Exponential smoothing model forward projections, uncertainty bounds, and backtesting accuracy.")

    # Model Evaluation KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Model Accuracy", f"{metrics['accuracy_pct']}%", "Out-of-Sample", True, f"MAPE: {metrics['mape']}%")
    with c2:
        render_kpi_card("Mean Absolute Error (MAE)", f"${metrics['mae']:,.0f}", "Monthly Revenue", True, "Avg deviation")
    with c3:
        render_kpi_card("Root Mean Sq Error (RMSE)", f"${metrics['rmse']:,.0f}", "Penalty on Outliers", True)
    with c4:
        render_kpi_card("Forecast Horizon", f"{metrics['forecast_horizon_months']} Months", "Forward Looking", True, "Monthly Granularity")

    st.markdown("---")

    # Forecast Timeline Chart
    st.plotly_chart(plot_forecast_timeline(forecast_df), use_container_width=True)

    st.markdown("---")

    # Seasonal Decomposition Subplots
    st.subheader("📊 Time Series Seasonal Decomposition")
    st.caption("Separates underlying macro trend from annual retail seasonality and irregular residuals.")

    col1, col2 = st.columns(2)
    with col1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=decomp_df["ds"], y=decomp_df["trend"], mode="lines", line=dict(color="#3B82F6", width=2.5)))
        fig_trend.update_layout(title="<b>Underlying Long-Term Trend</b>", yaxis_title="Trend Component ($)", **DARK_LAYOUT)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        fig_season = go.Figure()
        fig_season.add_trace(go.Scatter(x=decomp_df["ds"], y=decomp_df["seasonal"], mode="lines", line=dict(color="#10B981", width=2.5)))
        fig_season.update_layout(title="<b>Annual Seasonal Pattern (Q4 Holiday Surge)</b>", yaxis_title="Seasonality ($)", **DARK_LAYOUT)
        st.plotly_chart(fig_season, use_container_width=True)

    # Future Projection Pro-forma Table
    st.subheader("📋 6-Month Forward Revenue Estimates")
    future_table = (
        forecast_df[forecast_df["is_forecast"] == 1][["ds", "yhat", "yhat_lower", "yhat_upper"]]
        .rename(columns={
            "ds": "Forecast Month",
            "yhat": "Projected Revenue ($)",
            "yhat_lower": "Conservative Bound (95% CI)",
            "yhat_upper": "Optimistic Bound (95% CI)",
        })
    )
    future_table["Forecast Month"] = pd.to_datetime(future_table["Forecast Month"]).dt.strftime("%B %Y")
    st.dataframe(
        future_table.style.format({
            "Projected Revenue ($)": "${:,.2f}",
            "Conservative Bound (95% CI)": "${:,.2f}",
            "Optimistic Bound (95% CI)": "${:,.2f}",
        }),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
