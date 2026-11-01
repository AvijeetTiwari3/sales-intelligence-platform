"""
Database Ingestion Module
Loads transformed transaction data into normalized SQLite tables with relational integrity.
"""

import sqlite3
from pathlib import Path
import pandas as pd


def get_db_connection(db_path: str = "sales-intelligence-platform/database/sales.db") -> sqlite3.Connection:
    """Creates and returns an active SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str, schema_path: str):
    """Initializes tables and indexes using the schema definition file."""
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    with get_db_connection(db_path) as conn:
        conn.executescript(schema_sql)
    print(f"Database schema initialized at {db_path}")


def ingest_data(parquet_path: str, db_path: str, schema_path: str):
    """Loads normalized entities and fact records into SQLite."""
    init_db(db_path, schema_path)

    print(f"Loading transformed data from {parquet_path}...")
    df = pd.read_parquet(parquet_path)

    # 1. Customers Dimension
    customers = (
        df[["customer_id", "customer_name", "segment"]]
        .drop_duplicates(subset=["customer_id"])
        .reset_index(drop=True)
    )

    # 2. Products Dimension
    products = (
        df[["product_id", "category", "sub_category", "product_name"]]
        .drop_duplicates(subset=["product_id"])
        .reset_index(drop=True)
    )

    # 3. Locations Dimension
    locations = (
        df[["country", "region", "state", "city", "postal_code"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # 4. Orders Fact Table
    order_cols = [
        "row_id",
        "order_id",
        "order_date",
        "ship_date",
        "ship_mode",
        "customer_id",
        "product_id",
        "country",
        "region",
        "state",
        "city",
        "postal_code",
        "sales",
        "quantity",
        "discount",
        "profit",
        "profit_margin",
        "shipping_days",
        "order_year",
        "order_month",
        "order_quarter",
        "year_month",
        "is_profitable",
        "discount_tier",
    ]
    orders = df[order_cols].copy()
    orders["order_date"] = orders["order_date"].astype(str)
    orders["ship_date"] = orders["ship_date"].astype(str)

    with get_db_connection(db_path) as conn:
        print("Inserting Customers Dimension...")
        customers.to_sql("customers", conn, if_exists="append", index=False)

        print("Inserting Products Dimension...")
        products.to_sql("products", conn, if_exists="append", index=False)

        print("Inserting Locations Dimension...")
        locations.to_sql("locations", conn, if_exists="append", index=False)

        print("Inserting Orders Fact Table...")
        orders.to_sql("orders", conn, if_exists="append", index=False)

    print(f"Ingestion successful!")
    print(f"Loaded: {len(customers)} customers, {len(products)} products, {len(orders)} transactions.")


if __name__ == "__main__":
    ingest_data(
        parquet_path="sales-intelligence-platform/data/processed/orders_transformed.parquet",
        db_path="sales-intelligence-platform/database/sales.db",
        schema_path="sales-intelligence-platform/database/schema.sql",
    )
