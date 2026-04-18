"""
=============================================================================
 ETL – Transform Module
=============================================================================
 Cleans, enriches, and joins the raw DataFrames:
   • Handle missing / null values
   • Convert data types (dates, numerics)
   • Create derived features: delivery_delay, stock_status, etc.
   • Join datasets for analytics-ready tables
=============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.logger import get_logger

logger = get_logger("etl.transform")


# =============================================================================
# 1. Clean Suppliers
# =============================================================================
def clean_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning suppliers …")
    df = df.copy()

    # Fill missing emails / phones
    df["contact_email"] = df["contact_email"].fillna("unknown@example.com")
    df["phone"]         = df["phone"].fillna("N/A")

    # Ensure numeric types
    df["rating"]         = pd.to_numeric(df["rating"], errors="coerce").fillna(3.0)
    df["lead_time_days"] = pd.to_numeric(df["lead_time_days"], errors="coerce").fillna(7).astype(int)
    df["active"]         = df["active"].fillna(1).astype(int)

    # Supplier tier based on rating
    df["supplier_tier"] = pd.cut(
        df["rating"],
        bins=[0, 2, 3.5, 5],
        labels=["Bronze", "Silver", "Gold"],
        include_lowest=True,
    )

    logger.info(f"  → suppliers cleaned: {len(df):,} rows")
    return df


# =============================================================================
# 2. Clean Inventory
# =============================================================================
def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning inventory …")
    df = df.copy()

    # Fill missing values
    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce").fillna(0).astype(int)
    df["reorder_point"]    = pd.to_numeric(df["reorder_point"], errors="coerce").fillna(100).astype(int)
    df["unit_price"]       = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)

    # Parse dates
    df["last_restock_date"] = pd.to_datetime(df["last_restock_date"], errors="coerce")

    # Recompute stock status (may differ from generated value after cleaning)
    df["stock_status"] = np.where(
        df["quantity_on_hand"] <= 0, "Out of Stock",
        np.where(df["quantity_on_hand"] < df["reorder_point"], "Low Stock", "In Stock")
    )

    # Inventory value
    df["inventory_value"] = (df["quantity_on_hand"] * df["unit_price"]).round(2)

    # Days since last restock
    df["days_since_restock"] = (pd.Timestamp.now() - df["last_restock_date"]).dt.days

    logger.info(f"  → inventory cleaned: {len(df):,} rows")
    return df


# =============================================================================
# 3. Clean Orders
# =============================================================================
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning orders …")
    df = df.copy()

    # Numeric fields
    df["quantity"]     = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    df["unit_price"]   = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0.0)

    # Recalculate total if zero
    mask = df["total_amount"] == 0
    df.loc[mask, "total_amount"] = (df.loc[mask, "quantity"] * df.loc[mask, "unit_price"]).round(2)

    # Dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Temporal features
    df["order_year"]    = df["order_date"].dt.year
    df["order_month"]   = df["order_date"].dt.month
    df["order_quarter"] = df["order_date"].dt.quarter
    df["order_weekday"] = df["order_date"].dt.day_name()

    # Fill missing payment
    df["payment_method"] = df["payment_method"].fillna("Unknown")
    df["priority"]       = df["priority"].fillna("Medium")

    logger.info(f"  → orders cleaned: {len(df):,} rows")
    return df


# =============================================================================
# 4. Clean Shipments
# =============================================================================
def clean_shipments(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning shipments …")
    df = df.copy()

    # Dates
    for col in ["ship_date", "estimated_delivery", "actual_delivery"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Delivery delay (derived feature)
    df["delivery_delay_days"] = (df["actual_delivery"] - df["estimated_delivery"]).dt.days

    # Classify delay
    df["delay_category"] = pd.cut(
        df["delivery_delay_days"],
        bins=[-999, -1, 0, 3, 7, 999],
        labels=["Early", "On Time", "Slight Delay", "Moderate Delay", "Severe Delay"],
    )

    # Shipping cost
    df["shipping_cost"] = pd.to_numeric(df["shipping_cost"], errors="coerce").fillna(0.0)

    # Fill missing status
    df["delivery_status"] = df["delivery_status"].fillna("Unknown")
    df["carrier"]         = df["carrier"].fillna("Unknown")

    logger.info(f"  → shipments cleaned: {len(df):,} rows")
    return df


# =============================================================================
# 5. Create Joined / Enriched Datasets
# =============================================================================
def create_order_shipment_summary(orders: pd.DataFrame, shipments: pd.DataFrame) -> pd.DataFrame:
    """Join orders and shipments for a unified analytics view."""
    logger.info("Creating order-shipment summary …")

    merged = orders.merge(shipments, on="order_id", how="left", suffixes=("_order", "_shipment"))

    # Mark shipped / unshipped
    merged["is_shipped"] = merged["shipment_id"].notna().astype(int)

    logger.info(f"  → order-shipment summary: {len(merged):,} rows")
    return merged


# =============================================================================
# Main Transform Function
# =============================================================================
def transform_all(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Run all transformation steps and return cleaned DataFrames.

    Parameters
    ----------
    data : dict[str, pd.DataFrame]
        Raw DataFrames from the extract phase.

    Returns
    -------
    dict[str, pd.DataFrame]
        Cleaned DataFrames + enriched summary table.
    """
    logger.info("=" * 50)
    logger.info("TRANSFORM PHASE – cleaning & enriching data")
    logger.info("=" * 50)

    cleaned = {
        "suppliers":  clean_suppliers(data["suppliers"]),
        "inventory":  clean_inventory(data["inventory"]),
        "orders":     clean_orders(data["orders"]),
        "shipments":  clean_shipments(data["shipments"]),
    }

    # Enriched join
    cleaned["order_shipment_summary"] = create_order_shipment_summary(
        cleaned["orders"], cleaned["shipments"]
    )

    # Log summary statistics
    logger.info("─" * 50)
    logger.info("Transform Summary:")
    for name, df in cleaned.items():
        logger.info(f"  {name:30s}  →  {len(df):>6,} rows  ×  {len(df.columns):>3} cols")
    logger.info("─" * 50)

    return cleaned


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from extract import extract_all  # noqa: F401

    raw = extract_all()
    cleaned = transform_all(raw)

    for name, df in cleaned.items():
        print(f"\n{'='*60}\n{name.upper()}\n{'='*60}")
        print(df.dtypes)
        print(df.head(3))
