"""
Data Transformation and Feature Engineering Module
Transforms raw Superstore transactions into analytics-ready datasets.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def get_discount_tier(discount: float) -> str:
    """Classifies discount percentage into strategic pricing tiers."""
    if discount == 0.0:
        return "0% (Full Price)"
    elif discount <= 0.20:
        return "1% - 20% (Low)"
    elif discount <= 0.40:
        return "21% - 40% (Moderate)"
    else:
        return "> 40% (Aggressive)"


def transform_data(raw_csv_path: str, output_dir: str) -> pd.DataFrame:
    """Cleans raw CSV, engineers analytical features, and saves processed datasets."""
    raw_path = Path(raw_csv_path)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"Reading raw data from {raw_path}...")
    df = pd.read_csv(raw_path, encoding="latin1")

    # 1. Clean missing core transaction entries
    df = df.dropna(subset=["Order ID", "Order Date", "Sales", "Profit"]).copy()

    # 2. Convert types
    df["Row ID"] = pd.to_numeric(df["Row ID"], errors="coerce").astype(int)
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").round(4)
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").round(4)
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").round(4)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype(int)

    # 3. Handle Postal Code
    df["Postal Code"] = df["Postal Code"].fillna(0).astype(int).astype(str).str.zfill(5)

    # 4. Feature Engineering
    df["shipping_days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["profit_margin"] = np.where(df["Sales"] != 0, (df["Profit"] / df["Sales"]).round(4), 0.0)
    df["order_year"] = df["Order Date"].dt.year
    df["order_month"] = df["Order Date"].dt.month
    df["order_quarter"] = df["Order Date"].dt.quarter
    df["year_month"] = df["Order Date"].dt.strftime("%Y-%m")
    df["is_profitable"] = (df["Profit"] > 0).astype(int)
    df["discount_tier"] = df["Discount"].apply(get_discount_tier)

    # 5. Column Renaming to snake_case for standard DB & Python usage
    rename_dict = {
        "Row ID": "row_id",
        "Order ID": "order_id",
        "Order Date": "order_date",
        "Ship Date": "ship_date",
        "Ship Mode": "ship_mode",
        "Customer ID": "customer_id",
        "Customer Name": "customer_name",
        "Segment": "segment",
        "Country": "country",
        "City": "city",
        "State": "state",
        "Postal Code": "postal_code",
        "Region": "region",
        "Product ID": "product_id",
        "Category": "category",
        "Sub-Category": "sub_category",
        "Product Name": "product_name",
        "Sales": "sales",
        "Quantity": "quantity",
        "Discount": "discount",
        "Profit": "profit",
    }
    df = df.rename(columns=rename_dict)

    # 6. Sort chronologically
    df = df.sort_values(by=["order_date", "row_id"]).reset_index(drop=True)

    # 7. Export processed files
    csv_out = out_path / "orders_transformed.csv"
    parquet_out = out_path / "orders_transformed.parquet"

    df.to_csv(csv_out, index=False)
    df.to_parquet(parquet_out, index=False)

    print(f"Transformation complete. Processed {len(df):,} valid transactions.")
    print(f"Saved to:\n - {csv_out}\n - {parquet_out}")
    return df


if __name__ == "__main__":
    transform_data(
        raw_csv_path="sales-intelligence-platform/data/raw/superstore.csv",
        output_dir="sales-intelligence-platform/data/processed",
    )
