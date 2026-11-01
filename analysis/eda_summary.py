"""
Exploratory Data Analysis & Strategic Insights Generator
Computes deep business analytics metrics and key findings for executive reporting.
"""

import json
from pathlib import Path
import pandas as pd


def generate_executive_insights(
    parquet_path: str = "sales-intelligence-platform/data/processed/orders_transformed.parquet",
    output_dir: str = "sales-intelligence-platform/data/processed",
) -> dict:
    print("Generating Executive Business Analytics Insights...")
    df = pd.read_parquet(parquet_path)

    # 1. High-level KPIs
    total_sales = float(df["sales"].sum())
    total_profit = float(df["profit"].sum())
    overall_margin = round((total_profit / total_sales) * 100, 2)
    total_orders = int(df["order_id"].nunique())
    total_customers = int(df["customer_id"].nunique())
    avg_order_value = round(total_sales / total_orders, 2)

    # 2. Discount Impact Analysis
    discount_perf = (
        df.groupby("discount_tier")
        .agg(
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            order_count=("order_id", "nunique"),
            avg_margin=("profit_margin", lambda x: round(x.mean() * 100, 2)),
        )
        .reset_index()
    )

    # Calculate revenue leakage from aggressive discounts (> 40%)
    deep_discount_loss = float(df[df["discount"] > 0.40]["profit"].sum())

    # 3. Category Performance
    category_perf = (
        df.groupby("category")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
        )
        .assign(profit_margin=lambda x: (x["profit"] / x["sales"] * 100).round(2))
        .reset_index()
    )

    # 4. Regional Performance
    region_perf = (
        df.groupby("region")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
        )
        .assign(profit_margin=lambda x: (x["profit"] / x["sales"] * 100).round(2))
        .reset_index()
    )

    # 5. Customer Pareto Analysis (Top 20% customer revenue share)
    cust_sales = df.groupby("customer_id")["sales"].sum().sort_values(ascending=False)
    top_20_count = int(len(cust_sales) * 0.20)
    top_20_rev = float(cust_sales.iloc[:top_20_count].sum())
    pareto_share = round((top_20_rev / total_sales) * 100, 2)

    # 6. Assemble Insights dictionary
    insights = {
        "kpis": {
            "total_sales": round(total_sales, 2),
            "total_profit": round(total_profit, 2),
            "overall_margin_pct": overall_margin,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "avg_order_value": avg_order_value,
        },
        "discount_leakage": {
            "deep_discount_loss_usd": round(deep_discount_loss, 2),
            "tiers": discount_perf.to_dict(orient="records"),
        },
        "category_summary": category_perf.to_dict(orient="records"),
        "regional_summary": region_perf.to_dict(orient="records"),
        "pareto_principle": {
            "top_20_pct_customers_count": top_20_count,
            "top_20_pct_revenue_share": pareto_share,
        },
    }

    out_path = Path(output_dir)
    with open(out_path / "executive_insights.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2)

    print("Executive Insights successfully compiled!")
    print(f"Total Sales: ${total_sales:,.2f} | Profit: ${total_profit:,.2f} | Margin: {overall_margin}%")
    print(f"Discount Leakage (>40% discount): ${deep_discount_loss:,.2f} in losses")
    print(f"Top 20% Customers drive: {pareto_share}% of total revenue")
    return insights


if __name__ == "__main__":
    generate_executive_insights()
