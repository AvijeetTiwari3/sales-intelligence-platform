"""
Cohort Retention Analysis Module
Analyzes monthly customer acquisition cohorts and retention trajectories over time.
"""

from pathlib import Path
import pandas as pd


def compute_cohort_analysis(
    parquet_path: str = "sales-intelligence-platform/data/processed/orders_transformed.parquet",
    output_dir: str = "sales-intelligence-platform/data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generates cohort size and retention percentage matrices."""
    print("Computing Customer Cohort Retention Analysis...")
    df = pd.read_parquet(parquet_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # 1. Order Month (period format YYYY-MM)
    df["order_month_period"] = df["order_date"].dt.to_period("M")

    # 2. First purchase month per customer (Cohort Group)
    df["cohort_group"] = df.groupby("customer_id")["order_month_period"].transform("min")

    # 3. Cohort Period Index (number of months elapsed since first order)
    df["cohort_index"] = (
        (df["order_month_period"].dt.year - df["cohort_group"].dt.year) * 12
        + (df["order_month_period"].dt.month - df["cohort_group"].dt.month)
    )

    # 4. Group by Cohort and Period Index to count active customers
    cohort_data = (
        df.groupby(["cohort_group", "cohort_index"])["customer_id"]
        .nunique()
        .reset_index()
    )

    # 5. Pivot into Cohort Matrix
    cohort_pivot = cohort_data.pivot(
        index="cohort_group", columns="cohort_index", values="customer_id"
    )

    # Cohort base size (Month 0 active customer count)
    cohort_size = cohort_pivot.iloc[:, 0]

    # Retention percentage matrix
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0).round(4) * 100

    # Format cohort_group index as string YYYY-MM
    retention_matrix.index = retention_matrix.index.astype(str)
    cohort_pivot.index = cohort_pivot.index.astype(str)

    # Save to disk
    out_dir = Path(output_dir)
    retention_matrix.to_parquet(out_dir / "cohort_retention_matrix.parquet")
    retention_matrix.to_csv(out_dir / "cohort_retention_matrix.csv")

    cohort_pivot.to_parquet(out_dir / "cohort_counts_matrix.parquet")
    cohort_pivot.to_csv(out_dir / "cohort_counts_matrix.csv")

    print(f"Cohort matrix generated: {retention_matrix.shape[0]} cohorts tracked.")
    return cohort_pivot, retention_matrix


if __name__ == "__main__":
    compute_cohort_analysis()
