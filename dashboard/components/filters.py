"""
Sidebar Filter Component
Manages global analytical filters and slicing across dashboard pages.
"""

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders interactive multi-select filters and returns filtered dataframe."""
    st.sidebar.header("🔍 Global Analytics Filters")

    # Date Range Filter
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Region Filter
    regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

    # Category Filter
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories)

    # Customer Segment Filter
    segments = sorted(df["segment"].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect("Customer Segment", options=segments, default=segments)

    # Apply Filters
    filtered_df = df.copy()

    # Handle single date vs range tuple safely
    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_d, end_d = selected_date_range
        filtered_df = filtered_df[
            (filtered_df["order_date"].dt.date >= start_d)
            & (filtered_df["order_date"].dt.date <= end_d)
        ]

    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

    if selected_segments:
        filtered_df = filtered_df[filtered_df["segment"].isin(selected_segments)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"📊 Active Records: **{len(filtered_df):,}** / {len(df):,}")
    return filtered_df
