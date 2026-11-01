"""
RFM (Recency, Frequency, Monetary) Customer Segmentation Module
Combines statistical quintiles and K-Means Clustering to segment customers.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_rfm_segments(
    parquet_path: str = "sales-intelligence-platform/data/processed/orders_transformed.parquet",
    output_dir: str = "sales-intelligence-platform/data/processed",
) -> pd.DataFrame:
    """Computes RFM metrics, performs K-Means clustering, and maps segments."""
    print("Computing Customer RFM Segments...")
    df = pd.read_parquet(parquet_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Reference date for recency calculation (snapshot = latest transaction + 1 day)
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    # Aggregate by customer
    rfm = (
        df.groupby("customer_id")
        .agg(
            recency=("order_date", lambda x: (snapshot_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_order_value=("sales", "mean"),
            customer_name=("customer_name", "first"),
            segment_type=("segment", "first"),
            region=("region", "first"),
        )
        .reset_index()
    )

    # Log transformation for skewed monetary & frequency features
    rfm_log = pd.DataFrame()
    rfm_log["recency_log"] = np.log1p(rfm["recency"])
    rfm_log["frequency_log"] = np.log1p(rfm["frequency"])
    rfm_log["monetary_log"] = np.log1p(rfm["monetary"])

    # Standardization
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    # K-Means Clustering (k=4)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm["cluster"] = kmeans.fit_predict(rfm_scaled)

    # Cluster profiling: rank clusters based on monetary spend & recency
    cluster_means = rfm.groupby("cluster").agg(
        mean_recency=("recency", "mean"),
        mean_frequency=("frequency", "mean"),
        mean_monetary=("monetary", "mean"),
    )

    # Assign meaningful business names based on metric profiles
    # Sorted by monetary spend
    sorted_clusters = cluster_means.sort_values(by="mean_monetary", ascending=False).index.tolist()
    # 0 = Top spender (Champions), 1 = Loyal, 2 = At-Risk (high recency), 3 = Low engagement
    segment_mapping = {
        sorted_clusters[0]: "Champions",
        sorted_clusters[1]: "Loyal Customers",
        sorted_clusters[2]: "At-Risk",
        sorted_clusters[3]: "Hibernating",
    }

    # Further refine At-Risk vs Hibernating based on Recency
    if cluster_means.loc[sorted_clusters[2], "mean_recency"] < cluster_means.loc[sorted_clusters[3], "mean_recency"]:
        # If cluster 2 has lower recency than cluster 3, swap names appropriately
        pass

    rfm["rfm_segment"] = rfm["cluster"].map(segment_mapping)

    # Calculate RFM Quartile Scores (1 to 4)
    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)  # Lower recency is better
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    # Round numerical metrics
    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["total_profit"] = rfm["total_profit"].round(2)
    rfm["avg_order_value"] = rfm["avg_order_value"].round(2)

    # Save processed RFM
    out_dir = Path(output_dir)
    rfm.to_parquet(out_dir / "customer_rfm.parquet", index=False)
    rfm.to_csv(out_dir / "customer_rfm.csv", index=False)

    print("RFM Segmentation Summary:")
    summary = rfm.groupby("rfm_segment").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("monetary", "sum"),
        avg_recency_days=("recency", "mean"),
        avg_orders=("frequency", "mean"),
        avg_spend=("monetary", "mean"),
    )
    print(summary)
    return rfm


if __name__ == "__main__":
    compute_rfm_segments()
