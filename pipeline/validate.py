"""
Data Quality Validation Suite
Implements enterprise-grade assertions and data integrity verifications.
"""

import sqlite3
import sys
from pathlib import Path
import pandas as pd


class DataQualityValidator:
    def __init__(self, db_path: str = "sales-intelligence-platform/database/sales.db"):
        self.db_path = db_path
        self.failures = []
        self.passed = 0

    def assert_true(self, condition: bool, check_name: str, error_msg: str):
        if condition:
            self.passed += 1
            print(f"  [PASS] {check_name}")
        else:
            self.failures.append(f"{check_name}: {error_msg}")
            print(f"  [FAIL] {check_name}: {error_msg}")

    def run_all_checks(self):
        print(f"\n{'='*60}")
        print(f"Running Data Quality & Integrity Validation on: {self.db_path}")
        print(f"{'='*60}")

        conn = sqlite3.connect(self.db_path)

        # 1. Row count validation
        count_df = pd.read_sql("SELECT COUNT(*) AS total FROM orders;", conn)
        total_rows = count_df["total"].iloc[0]
        self.assert_true(total_rows == 9994, "Row Count Check", f"Expected 9,994 rows, found {total_rows}")

        # 2. Primary Key Uniqueness
        pk_df = pd.read_sql("SELECT COUNT(row_id) AS total, COUNT(DISTINCT row_id) AS distinct_total FROM orders;", conn)
        self.assert_true(
            pk_df["total"].iloc[0] == pk_df["distinct_total"].iloc[0],
            "Primary Key Uniqueness",
            "Duplicate row_ids found in orders table"
        )

        # 3. Non-Null Constraints
        null_df = pd.read_sql(
            """
            SELECT
                SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_orders,
                SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_cust,
                SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
                SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END) AS null_profit,
                SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_dates
            FROM orders;
            """,
            conn
        )
        total_nulls = int(null_df.sum(axis=1).iloc[0])
        self.assert_true(total_nulls == 0, "Non-Null Check for Key Columns", f"Found {total_nulls} null values")

        # 4. Numerical Range Assertions
        invalid_sales = pd.read_sql("SELECT COUNT(*) AS c FROM orders WHERE sales <= 0;", conn)["c"].iloc[0]
        self.assert_true(invalid_sales == 0, "Positive Sales Value Check", f"Found {invalid_sales} records with sales <= 0")

        invalid_quantities = pd.read_sql("SELECT COUNT(*) AS c FROM orders WHERE quantity < 1;", conn)["c"].iloc[0]
        self.assert_true(invalid_quantities == 0, "Valid Quantity Check", f"Found {invalid_quantities} records with quantity < 1")

        invalid_discounts = pd.read_sql("SELECT COUNT(*) AS c FROM orders WHERE discount < 0.0 OR discount > 1.0;", conn)["c"].iloc[0]
        self.assert_true(invalid_discounts == 0, "Discount Range [0.0 - 1.0] Check", f"Found {invalid_discounts} out of range discounts")

        # 5. Temporal Consistency Check
        date_inconsistencies = pd.read_sql("SELECT COUNT(*) AS c FROM orders WHERE shipping_days < 0;", conn)["c"].iloc[0]
        self.assert_true(
            date_inconsistencies == 0,
            "Ship Date >= Order Date Check",
            f"Found {date_inconsistencies} orders where ship date precedes order date"
        )

        # 6. Referential Integrity (Foreign Keys)
        orphan_customers = pd.read_sql(
            """
            SELECT COUNT(*) AS c
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
            """,
            conn
        )["c"].iloc[0]
        self.assert_true(orphan_customers == 0, "Customer Foreign Key Integrity", f"Found {orphan_customers} orphan customer keys")

        orphan_products = pd.read_sql(
            """
            SELECT COUNT(*) AS c
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.product_id
            WHERE p.product_id IS NULL;
            """,
            conn
        )["c"].iloc[0]
        self.assert_true(orphan_products == 0, "Product Foreign Key Integrity", f"Found {orphan_products} orphan product keys")

        conn.close()

        # Summary
        print(f"{'='*60}")
        print(f"Validation Summary: {self.passed} Passed, {len(self.failures)} Failed")
        print(f"{'='*60}\n")

        if self.failures:
            print("FAILED CHECKS:")
            for failure in self.failures:
                print(f" - {failure}")
            sys.exit(1)
        else:
            print("All Data Quality & Governance Checks PASSED successfully!")


if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.run_all_checks()
