"""
=============================================================================
 Advanced – Alert System
=============================================================================
 Monitors inventory levels and generates alerts when stock falls
 below the reorder point. Alerts are stored in MySQL and optionally
 printed to the console / log.
=============================================================================
"""

import os
import sys
import pandas as pd
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.db_config import get_connection_url
from utils.logger import get_logger

logger = get_logger("advanced.alerts")


def check_stock_alerts() -> pd.DataFrame:
    """
    Query the inventory table for products whose quantity_on_hand
    is below the reorder_point. Store results in the stock_alerts table.

    Returns
    -------
    pd.DataFrame
        Alert records generated.
    """
    from sqlalchemy import create_engine, text

    logger.info("=" * 50)
    logger.info("STOCK ALERT CHECK")
    logger.info("=" * 50)

    engine = create_engine(get_connection_url())

    # ── Query low-stock items ──────────────────────────────────
    query = """
        SELECT
            product_id,
            product_name,
            warehouse_id,
            quantity_on_hand AS current_stock,
            reorder_point,
            supplier_id
        FROM inventory
        WHERE quantity_on_hand < reorder_point
        ORDER BY (reorder_point - quantity_on_hand) DESC
    """
    alerts_df = pd.read_sql(query, engine)

    if alerts_df.empty:
        logger.info("✔ No low-stock items found. All good!")
        engine.dispose()
        return alerts_df

    logger.warning(f"⚠ {len(alerts_df)} low-stock alerts detected!")

    # ── Classify alert severity ────────────────────────────────
    alerts_df["deficit"] = alerts_df["reorder_point"] - alerts_df["current_stock"]
    alerts_df["alert_type"] = alerts_df.apply(_classify_alert, axis=1)
    alerts_df["alert_date"] = datetime.now()
    alerts_df["resolved"]   = 0

    # ── Display top alerts ─────────────────────────────────────
    logger.info("─" * 60)
    logger.info(f"{'Product':<12} {'Warehouse':<16} {'Stock':>6} {'Reorder':>8} {'Type':<15}")
    logger.info("─" * 60)
    for _, row in alerts_df.head(20).iterrows():
        logger.info(
            f"{row['product_id']:<12} "
            f"{row['warehouse_id']:<16} "
            f"{row['current_stock']:>6} "
            f"{row['reorder_point']:>8} "
            f"{row['alert_type']:<15}"
        )
    logger.info("─" * 60)

    # ── Store alerts in MySQL ──────────────────────────────────
    store_cols = [
        "product_id", "warehouse_id", "current_stock",
        "reorder_point", "alert_type", "alert_date", "resolved",
    ]
    alerts_df[store_cols].to_sql(
        "stock_alerts", engine, if_exists="append", index=False, chunksize=500
    )
    logger.info(f"Stored {len(alerts_df)} alerts in stock_alerts table")

    engine.dispose()
    return alerts_df


def _classify_alert(row) -> str:
    """Classify alert severity based on deficit magnitude."""
    ratio = row["current_stock"] / row["reorder_point"] if row["reorder_point"] > 0 else 0

    if row["current_stock"] == 0:
        return "Out of Stock"
    elif ratio < 0.25:
        return "Critical"
    elif ratio < 0.5:
        return "Low Stock"
    else:
        return "Warning"


def get_alert_summary() -> dict:
    """
    Return a dict summarising current unresolved alerts.

    Returns
    -------
    dict
        Keys: total_alerts, critical, low_stock, out_of_stock, warning
    """
    from sqlalchemy import create_engine

    engine = create_engine(get_connection_url())
    query = """
        SELECT
            alert_type,
            COUNT(*) AS cnt
        FROM stock_alerts
        WHERE resolved = 0
        GROUP BY alert_type
    """
    df = pd.read_sql(query, engine)
    engine.dispose()

    summary = {"total_alerts": int(df["cnt"].sum())}
    for _, row in df.iterrows():
        summary[row["alert_type"].lower().replace(" ", "_")] = int(row["cnt"])

    return summary


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    alerts = check_stock_alerts()
    print(f"\nTotal alerts: {len(alerts)}")
    if not alerts.empty:
        print(alerts[["product_id", "warehouse_id", "current_stock", "reorder_point", "alert_type"]].to_string(index=False))
