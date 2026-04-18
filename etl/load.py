"""
=============================================================================
 ETL – Load Module
=============================================================================
 Loads cleaned DataFrames into MySQL using SQLAlchemy bulk insert.
 Handles table ordering to respect foreign key constraints.
=============================================================================
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.db_config import get_connection_url
from utils.logger import get_logger

logger = get_logger("etl.load")

# ---------------------------------------------------------------------------
# Table load order (respects FK dependencies)
# ---------------------------------------------------------------------------
TABLE_LOAD_ORDER = ["suppliers", "inventory", "orders", "shipments"]

# Columns to keep per table (must match schema.sql)
TABLE_COLUMNS = {
    "suppliers": [
        "supplier_id", "supplier_name", "contact_email", "phone",
        "city", "country", "rating", "lead_time_days", "active",
    ],
    "inventory": [
        "inventory_id", "product_id", "product_name", "category",
        "warehouse_id", "supplier_id", "quantity_on_hand", "reorder_point",
        "unit_price", "last_restock_date", "stock_status",
    ],
    "orders": [
        "order_id", "product_id", "customer_id", "quantity",
        "unit_price", "total_amount", "order_date", "payment_method",
        "warehouse_id", "priority",
    ],
    "shipments": [
        "shipment_id", "order_id", "supplier_id", "ship_date",
        "estimated_delivery", "actual_delivery", "delivery_status",
        "delivery_delay_days", "carrier", "shipping_cost",
    ],
}


def load_table(
    engine,
    table_name: str,
    df: pd.DataFrame,
    if_exists: str = "append",
    chunksize: int = 500,
) -> None:
    """
    Load a DataFrame into a MySQL table using pandas + SQLAlchemy.

    Parameters
    ----------
    engine : sqlalchemy.Engine
    table_name : str
    df : pd.DataFrame
    if_exists : str
        'replace' drops and recreates; 'append' inserts new rows.
    chunksize : int
        Number of rows per INSERT batch.
    """
    logger.info(f"Loading table: {table_name}  ({len(df):,} rows, chunksize={chunksize})")

    # Select only the columns that match the target schema
    if table_name in TABLE_COLUMNS:
        cols = [c for c in TABLE_COLUMNS[table_name] if c in df.columns]
        df = df[cols]

    # Convert NaT / NaN to None for MySQL compatibility
    df = df.where(df.notna(), None)

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        chunksize=chunksize,
        method="multi",
    )

    logger.info(f"  ✔ {table_name} loaded successfully")


def load_all(
    data: dict[str, pd.DataFrame],
    if_exists: str = "append",
) -> None:
    """
    Load all cleaned DataFrames into MySQL.

    Parameters
    ----------
    data : dict[str, pd.DataFrame]
        Keys should include 'suppliers', 'inventory', 'orders', 'shipments'.
    if_exists : str
        'replace' or 'append'.
    """
    logger.info("=" * 50)
    logger.info("LOAD PHASE – writing to MySQL")
    logger.info("=" * 50)

    url = get_connection_url()
    engine = create_engine(url, echo=False)

    # Disable FK checks for clean replace
    if if_exists == "replace":
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    try:
        for table in TABLE_LOAD_ORDER:
            if table in data:
                load_table(engine, table, data[table], if_exists=if_exists)
            else:
                logger.warning(f"  ⚠ Dataset '{table}' not found – skipping")
    finally:
        # Re-enable FK checks
        if if_exists == "replace":
            with engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    # Verification
    logger.info("─" * 50)
    logger.info("Verifying table row counts …")
    with engine.connect() as conn:
        for table in TABLE_LOAD_ORDER:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            logger.info(f"  {table:20s}  →  {count:>6,} rows")
    logger.info("─" * 50)
    logger.info("Load phase complete ✔")

    engine.dispose()


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from extract import extract_all
    from transform import transform_all

    raw     = extract_all()
    cleaned = transform_all(raw)
    load_all(cleaned)
