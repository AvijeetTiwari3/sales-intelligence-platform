"""
Sales Deep Dive & Operational Performance Page
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.components.charts import (
    DARK_LAYOUT,
    plot_discount_elasticity,
    plot_geo_choropleth,
)
from dashboard.components.filters import render_sidebar_filters


@st.cache_data
def load_data():
    df = pd.read_parquet(ROOT_DIR / "data" / "processed" / "orders_transformed.parquet")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def main():
    st.set_page_config(page_title="Sales Deep Dive | Sales Intelligence", page_icon="🔍", layout="wide")
    raw_df = load_data()
    df = render_sidebar_filters(raw_df)

    st.title("🔍 Sales Deep Dive & Discount Analysis")
    st.caption("Drill-down into geographic performance, discount destruction, and shipping logistics.")

    # Geo Map Section
    st.plotly_chart(plot_geo_choropleth(df), use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📉 Discount Tier Economics")
        tier_summary = (
            df.groupby("discount_tier")
            .agg(
                sales=("sales", "sum"),
                profit=("profit", "sum"),
                orders=("order_id", "nunique"),
                margin=("profit_margin", lambda x: round(x.mean() * 100, 2)),
            )
            .reset_index()
        )
        fig_tier = px.bar(
            tier_summary,
            x="discount_tier",
            y="profit",
            color="profit",
            color_continuous_scale="RdYlGn",
            text="profit",
            title="<b>Operating Profit by Discount Tier</b>",
        )
        fig_tier.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_tier.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig_tier, use_container_width=True)

    with col2:
        st.subheader("🚚 Shipping Mode SLA & Profitability")
        ship_summary = (
            df.groupby("ship_mode")
            .agg(
                avg_delivery_days=("shipping_days", "mean"),
                total_sales=("sales", "sum"),
                total_profit=("profit", "sum"),
            )
            .assign(avg_delivery_days=lambda x: x["avg_delivery_days"].round(1))
            .reset_index()
        )
        fig_ship = px.scatter(
            ship_summary,
            x="avg_delivery_days",
            y="total_profit",
            size="total_sales",
            color="ship_mode",
            hover_name="ship_mode",
            title="<b>Delivery Lead Time vs. Total Profit (Bubble Size = Sales)</b>",
        )
        fig_ship.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig_ship, use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 Discount Inefficiency Elasticity")
    st.plotly_chart(plot_discount_elasticity(df), use_container_width=True)


if __name__ == "__main__":
    main()
