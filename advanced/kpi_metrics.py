"""
=============================================================================
 Advanced – KPI Metrics
=============================================================================
 Computes key performance indicators from the supply chain database
 and stores them in the kpi_metrics table for Power BI consumption.
=============================================================================
"""

import os
import sys
import pandas as pd
from datetime import date

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.db_config import get_connection_url
from utils.logger import get_logger

logger = get_logger("advanced.kpis")


def compute_and_store_kpis() -> pd.DataFrame:
    """
    Calculate key supply chain KPIs and store them in MySQL.

    KPIs computed:
        1. Average Delivery Time (days)
        2. On-Time Delivery Rate (%)
        3. Order Fulfillment Rate (%)
        4. Average Order Value ($)
        5. Inventory Turnover Ratio
        6. Stockout Rate (%)
        7. Total Revenue
        8. Average Shipping Cost
        9. Supplier Performance Score
       10. Critical Stock Percentage

    Returns
    -------
    pd.DataFrame
        The computed KPI records.
    """
    from sqlalchemy import create_engine

    logger.info("=" * 50)
    logger.info("COMPUTING KPI METRICS")
    logger.info("=" * 50)

    engine = create_engine(get_connection_url())
    today  = date.today()
    kpis   = []

    # ── 1. Average Delivery Time ───────────────────────────────
    result = pd.read_sql("""
        SELECT AVG(DATEDIFF(actual_delivery, ship_date)) AS val
        FROM shipments
        WHERE actual_delivery IS NOT NULL
    """, engine)
    avg_delivery = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Average Delivery Time (days)", avg_delivery, "Delivery"))
    logger.info(f"  Avg Delivery Time: {avg_delivery} days")

    # ── 2. On-Time Delivery Rate ───────────────────────────────
    result = pd.read_sql("""
        SELECT
            COUNT(CASE WHEN actual_delivery <= estimated_delivery THEN 1 END) * 100.0
            / NULLIF(COUNT(*), 0) AS val
        FROM shipments
        WHERE actual_delivery IS NOT NULL
    """, engine)
    on_time_rate = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("On-Time Delivery Rate (%)", on_time_rate, "Delivery"))
    logger.info(f"  On-Time Rate: {on_time_rate}%")

    # ── 3. Order Fulfillment Rate ──────────────────────────────
    result = pd.read_sql("""
        SELECT
            COUNT(DISTINCT s.order_id) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0) AS val
        FROM orders o
        LEFT JOIN shipments s ON o.order_id = s.order_id
    """, engine)
    fulfillment = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Order Fulfillment Rate (%)", fulfillment, "Orders"))
    logger.info(f"  Fulfillment Rate: {fulfillment}%")

    # ── 4. Average Order Value ─────────────────────────────────
    result = pd.read_sql("SELECT AVG(total_amount) AS val FROM orders", engine)
    avg_order_val = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Average Order Value ($)", avg_order_val, "Orders"))
    logger.info(f"  Avg Order Value: ${avg_order_val}")

    # ── 5. Inventory Turnover Ratio ────────────────────────────
    result = pd.read_sql("""
        SELECT
            COALESCE(SUM(o.quantity), 0) / NULLIF(AVG(i.quantity_on_hand), 0) AS val
        FROM orders o
        CROSS JOIN (SELECT AVG(quantity_on_hand) AS quantity_on_hand FROM inventory) i
    """, engine)
    turnover = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Inventory Turnover Ratio", turnover, "Inventory"))
    logger.info(f"  Inventory Turnover: {turnover}")

    # ── 6. Stockout Rate ───────────────────────────────────────
    result = pd.read_sql("""
        SELECT
            COUNT(CASE WHEN quantity_on_hand = 0 THEN 1 END) * 100.0
            / NULLIF(COUNT(*), 0) AS val
        FROM inventory
    """, engine)
    stockout = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Stockout Rate (%)", stockout, "Inventory"))
    logger.info(f"  Stockout Rate: {stockout}%")

    # ── 7. Total Revenue ───────────────────────────────────────
    result = pd.read_sql("SELECT SUM(total_amount) AS val FROM orders", engine)
    revenue = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Total Revenue ($)", revenue, "Financial"))
    logger.info(f"  Total Revenue: ${revenue:,.2f}")

    # ── 8. Average Shipping Cost ───────────────────────────────
    result = pd.read_sql("SELECT AVG(shipping_cost) AS val FROM shipments", engine)
    avg_shipping = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Average Shipping Cost ($)", avg_shipping, "Financial"))
    logger.info(f"  Avg Shipping Cost: ${avg_shipping}")

    # ── 9. Supplier Performance Score ──────────────────────────
    result = pd.read_sql("SELECT AVG(rating) AS val FROM suppliers WHERE active = 1", engine)
    supplier_score = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Avg Supplier Rating", supplier_score, "Suppliers"))
    logger.info(f"  Avg Supplier Rating: {supplier_score}")

    # ── 10. Critical Stock Percentage ──────────────────────────
    result = pd.read_sql("""
        SELECT
            COUNT(CASE WHEN quantity_on_hand < reorder_point THEN 1 END) * 100.0
            / NULLIF(COUNT(*), 0) AS val
        FROM inventory
    """, engine)
    critical_pct = round(float(result["val"].iloc[0] or 0), 2)
    kpis.append(("Critical Stock Percentage (%)", critical_pct, "Inventory"))
    logger.info(f"  Critical Stock: {critical_pct}%")

    # ── Store KPIs ─────────────────────────────────────────────
    kpi_df = pd.DataFrame(kpis, columns=["metric_name", "metric_value", "metric_category"])
    kpi_df["metric_date"] = today

    kpi_df.to_sql("kpi_metrics", engine, if_exists="append", index=False, chunksize=100)
    logger.info(f"Stored {len(kpi_df)} KPI metrics")

    engine.dispose()
    return kpi_df


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    kpis = compute_and_store_kpis()
    print("\n" + kpis.to_string(index=False))
