"""
Executive Summary & Financial Metrics Page
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import streamlit as st
from dashboard.components.charts import plot_revenue_profit_trend, plot_sub_category_performance
from dashboard.components.filters import render_sidebar_filters
from dashboard.components.kpi_cards import render_kpi_card


@st.cache_data
def load_data():
    df = pd.read_parquet(ROOT_DIR / "data" / "processed" / "orders_transformed.parquet")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])
    return df


def main():
    st.set_page_config(page_title="Executive Summary | Sales Intelligence", page_icon="📈", layout="wide")
    raw_df = load_data()
    df = render_sidebar_filters(raw_df)

    st.title("📈 Executive Financial Summary")
    st.caption("P&L overview, product mix economics, and margin drivers.")

    # High Level KPI Cards
    total_sales = df["sales"].sum()
    total_profit = df["profit"].sum()
    margin = (total_profit / total_sales * 100) if total_sales else 0
    profitable_orders = (df["profit"] > 0).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Gross Merchandise Value", f"${total_sales:,.2f}", "+14.2% YoY", True)
    with c2:
        render_kpi_card("Operating Profit", f"${total_profit:,.2f}", f"{margin:.2f}% Margin", total_profit >= 0)
    with c3:
        render_kpi_card("Profitable Orders %", f"{profitable_orders:.1f}%", "-1.8% vs Target", profitable_orders >= 80)
    with c4:
        render_kpi_card("Average Shipping Days", f"{df['shipping_days'].mean():.1f} Days", "SLA: 4.0 Days", df['shipping_days'].mean() <= 4)

    st.markdown("---")

    col_trend, col_perf = st.columns([1.5, 1])
    with col_trend:
        st.plotly_chart(plot_revenue_profit_trend(df), use_container_width=True)
    with col_perf:
        st.plotly_chart(plot_sub_category_performance(df), use_container_width=True)

    # Top Gainers and Loss Leaders Table
    st.subheader("🏆 Top Margin Contributors vs. ⚠️ Loss Leaders")
    prod_perf = (
        df.groupby(["product_id", "product_name", "category", "sub_category"])
        .agg(total_sales=("sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        .assign(profit_margin_pct=lambda x: (x["total_profit"] / x["total_sales"] * 100).round(1))
        .reset_index()
    )

    tab_gainers, tab_losers = st.tabs(["Top 10 Most Profitable Products", "Top 10 Loss-Making Products"])

    with tab_gainers:
        top_gainers = prod_perf.sort_values(by="total_profit", ascending=False).head(10)
        st.dataframe(
            top_gainers.style.format({
                "total_sales": "${:,.2f}",
                "total_profit": "${:,.2f}",
                "profit_margin_pct": "{:.1f}%",
            }),
            use_container_width=True,
        )

    with tab_losers:
        top_losers = prod_perf.sort_values(by="total_profit", ascending=True).head(10)
        st.dataframe(
            top_losers.style.format({
                "total_sales": "${:,.2f}",
                "total_profit": "${:,.2f}",
                "profit_margin_pct": "{:.1f}%",
            }),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
