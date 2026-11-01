"""
Customer Segmentation & Cohort Retention Analytics Page
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import streamlit as st
from dashboard.components.charts import plot_cohort_heatmap, plot_rfm_bubble
from dashboard.components.kpi_cards import render_kpi_card


@st.cache_data
def load_rfm():
    rfm_path = ROOT_DIR / "data" / "processed" / "customer_rfm.parquet"
    if not rfm_path.exists():
        from analysis.rfm_segmentation import compute_rfm_segments
        return compute_rfm_segments()
    return pd.read_parquet(rfm_path)


@st.cache_data
def load_cohorts():
    cohort_path = ROOT_DIR / "data" / "processed" / "cohort_retention_matrix.parquet"
    if not cohort_path.exists():
        from analysis.cohort_analysis import compute_cohort_analysis
        _, retention_matrix = compute_cohort_analysis()
        return retention_matrix
    return pd.read_parquet(cohort_path)


def main():
    st.set_page_config(page_title="Customer Segments | Sales Intelligence", page_icon="👥", layout="wide")
    rfm_df = load_rfm()
    retention_matrix = load_cohorts()

    st.title("👥 Customer Behavioral Segmentation (RFM) & Retention Cohorts")
    st.caption("K-Means machine learning customer clusters and longitudinal retention dynamics.")

    # High Level Segment Metrics
    seg_summary = rfm_df.groupby("rfm_segment").agg(
        count=("customer_id", "count"),
        total_rev=("monetary", "sum"),
        avg_spend=("monetary", "mean"),
    ).to_dict("index")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        champ = seg_summary.get("Champions", {"count": 0, "total_rev": 0, "avg_spend": 0})
        render_kpi_card("Champions", f"{champ['count']} Customers", f"${champ['total_rev']:,.0f} Rev", True, f"Avg Spend: ${champ['avg_spend']:,.0f}")
    with c2:
        loyal = seg_summary.get("Loyal Customers", {"count": 0, "total_rev": 0, "avg_spend": 0})
        render_kpi_card("Loyal Customers", f"{loyal['count']} Customers", f"${loyal['total_rev']:,.0f} Rev", True, f"Avg Spend: ${loyal['avg_spend']:,.0f}")
    with c3:
        at_risk = seg_summary.get("At-Risk", {"count": 0, "total_rev": 0, "avg_spend": 0})
        render_kpi_card("At-Risk Accounts", f"{at_risk['count']} Customers", f"${at_risk['total_rev']:,.0f} at risk", False, f"Avg Spend: ${at_risk['avg_spend']:,.0f}")
    with c4:
        hib = seg_summary.get("Hibernating", {"count": 0, "total_rev": 0, "avg_spend": 0})
        render_kpi_card("Hibernating", f"{hib['count']} Customers", f"${hib['total_rev']:,.0f} Rev", False, f"Avg Spend: ${hib['avg_spend']:,.0f}")

    st.markdown("---")

    # RFM Scatter Bubble Chart
    st.subheader("🎯 RFM Clustering Landscape")
    st.plotly_chart(plot_rfm_bubble(rfm_df), use_container_width=True)

    st.markdown("---")

    # Cohort Retention Matrix
    st.subheader("📅 Longitudinal Cohort Retention Analysis")
    st.caption("Tracks repeat transactions of customer acquisition cohorts across sequential billing months.")
    st.plotly_chart(plot_cohort_heatmap(retention_matrix), use_container_width=True)

    # Top Customers Table
    st.markdown("---")
    st.subheader("⭐ Top 10 Lifetime Value Customers")
    top_customers = (
        rfm_df.sort_values(by="monetary", ascending=False)
        .head(10)[["customer_name", "segment_type", "region", "rfm_segment", "frequency", "monetary", "total_profit", "recency"]]
        .rename(columns={
            "customer_name": "Customer Name",
            "segment_type": "Market Segment",
            "region": "Region",
            "rfm_segment": "RFM Cluster",
            "frequency": "Lifetime Orders",
            "monetary": "Total Spend ($)",
            "total_profit": "Total Profit ($)",
            "recency": "Days Since Last Order",
        })
    )
    st.dataframe(
        top_customers.style.format({
            "Total Spend ($)": "${:,.2f}",
            "Total Profit ($)": "${:,.2f}",
        }),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
