"""
Plotly Chart Factory
Generates responsive, publication-grade interactive charts with dark theme aesthetics.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(15, 23, 42, 0.5)",
    plot_bgcolor="rgba(15, 23, 42, 0.5)",
    font=dict(color="#F8FAFC", family="Inter, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
    yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
)

# Standard State to 2-letter Code mapping for US Choropleth Map
STATE_CODE_MAP = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}


def plot_revenue_profit_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly Revenue and Profit Area/Line Chart."""
    monthly = (
        df.set_index("order_date")
        .resample("ME")[["sales", "profit"]]
        .sum()
        .reset_index()
    )
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["order_date"],
            y=monthly["sales"],
            name="Revenue ($)",
            mode="lines",
            line=dict(color="#3B82F6", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.15)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["order_date"],
            y=monthly["profit"],
            name="Net Profit ($)",
            mode="lines",
            line=dict(color="#10B981", width=2.5),
        )
    )

    fig.update_layout(
        title="<b>Monthly Revenue vs. Net Profit Trajectory</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **DARK_LAYOUT,
    )
    return fig


def plot_geo_choropleth(df: pd.DataFrame) -> go.Figure:
    """US State Sales Choropleth Map."""
    state_sales = (
        df.groupby("state")
        .agg(total_sales=("sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    state_sales["state_code"] = state_sales["state"].map(STATE_CODE_MAP)
    state_sales = state_sales.dropna(subset=["state_code"])

    fig = px.choropleth(
        state_sales,
        locations="state_code",
        locationmode="USA-states",
        color="total_sales",
        scope="usa",
        hover_name="state",
        hover_data={"total_sales": ":$,.2f", "total_profit": ":$,.2f", "orders": ":,", "state_code": False},
        color_continuous_scale="Viridis",
        title="<b>Geographic Revenue Distribution Across US States</b>",
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(15, 23, 42, 0.8)"),
        **DARK_LAYOUT,
    )
    return fig


def plot_discount_elasticity(df: pd.DataFrame) -> go.Figure:
    """Discount rate vs Profit Margin Elasticity Curve."""
    sample_df = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample_df,
        x="discount",
        y="profit_margin",
        color="category",
        color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
        opacity=0.6,
        trendline="ols",
        labels={"discount": "Discount Rate (0.0 to 1.0)", "profit_margin": "Profit Margin"},
        title="<b>Discount Rate vs. Profit Margin Inefficiency</b> (Breakeven Decay)",
    )
    # Add breakeven line
    fig.add_hline(y=0, line_dash="dash", line_color="#EF4444", annotation_text="Breakeven (0% Margin)")
    fig.update_layout(hovermode="closest", **DARK_LAYOUT)
    return fig


def plot_sub_category_performance(df: pd.DataFrame) -> go.Figure:
    """Ranked Sub-Category Profitability Bar Chart."""
    sub_cat = (
        df.groupby("sub_category")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        .sort_values(by="profit", ascending=True)
        .reset_index()
    )

    colors = ["#EF4444" if p < 0 else "#10B981" for p in sub_cat["profit"]]

    fig = go.Figure(
        go.Bar(
            x=sub_cat["profit"],
            y=sub_cat["sub_category"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"${p:,.0f}" for p in sub_cat["profit"]],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="<b>Net Profit by Sub-Category</b> (Red indicates Loss-Leaders)",
        xaxis_title="Profit ($)",
        yaxis_title="Sub-Category",
        **DARK_LAYOUT,
    )
    return fig


def plot_rfm_bubble(rfm_df: pd.DataFrame) -> go.Figure:
    """RFM Segmentation Scatter: Recency vs Frequency with size = Monetary."""
    fig = px.scatter(
        rfm_df,
        x="recency",
        y="frequency",
        size="monetary",
        color="rfm_segment",
        hover_name="customer_name",
        hover_data={"monetary": ":$,.2f", "avg_order_value": ":$,.2f", "recency": True, "frequency": True},
        color_discrete_map={
            "Champions": "#10B981",
            "Loyal Customers": "#3B82F6",
            "At-Risk": "#F59E0B",
            "Hibernating": "#EF4444",
        },
        labels={"recency": "Days Since Last Purchase (Recency)", "frequency": "Lifetime Order Frequency"},
        title="<b>Customer RFM Behavioral Clusters (Size = Total Monetary Spend)</b>",
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def plot_cohort_heatmap(retention_matrix: pd.DataFrame) -> go.Figure:
    """Cohort Customer Retention Rate Heatmap."""
    # Limit to top 15 cohorts and 12 periods for readable visualization
    subset = retention_matrix.iloc[:15, :13]
    fig = px.imshow(
        subset,
        labels=dict(x="Months Since First Order", y="Cohort Acquisition Month", color="Retention (%)"),
        x=subset.columns,
        y=subset.index,
        color_continuous_scale="Blues",
        text_auto=".1f",
        aspect="auto",
        title="<b>Customer Cohort Retention Rate (%) Over Time</b>",
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def plot_forecast_timeline(forecast_df: pd.DataFrame) -> go.Figure:
    """Time Series Sales Projection with Confidence Bounds."""
    fig = go.Figure()

    # Historical Actuals
    hist = forecast_df[forecast_df["is_forecast"] == 0]
    future = forecast_df[forecast_df["is_forecast"] == 1]

    fig.add_trace(
        go.Scatter(
            x=hist["ds"],
            y=hist["y"],
            name="Historical Revenue",
            mode="lines+markers",
            line=dict(color="#3B82F6", width=2.5),
        )
    )

    # In-sample Model Fit
    fig.add_trace(
        go.Scatter(
            x=hist["ds"],
            y=hist["yhat"],
            name="Model Fit",
            mode="lines",
            line=dict(color="#94A3B8", width=1.5, dash="dot"),
        )
    )

    # Future Projection
    fig.add_trace(
        go.Scatter(
            x=future["ds"],
            y=future["yhat"],
            name="6-Month Forward Projection",
            mode="lines+markers",
            line=dict(color="#10B981", width=3),
        )
    )

    # Upper and Lower Confidence Intervals
    fig.add_trace(
        go.Scatter(
            x=pd.concat([future["ds"], future["ds"][::-1]]),
            y=pd.concat([future["yhat_upper"], future["yhat_lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="95% Confidence Interval",
        )
    )

    fig.update_layout(
        title="<b>Holt-Winters Seasonal Sales Forecast (6-Month Projection with 95% CI)</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **DARK_LAYOUT,
    )
    return fig
