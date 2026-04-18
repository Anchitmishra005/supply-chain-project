"""
=============================================================================
 Advanced – Demand Forecasting
=============================================================================
 Uses scikit-learn Linear Regression to predict future product demand
 based on historical order data stored in MySQL.
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.db_config import get_connection_url
from utils.logger import get_logger

logger = get_logger("advanced.forecast")


def load_order_history() -> pd.DataFrame:
    """Load aggregated weekly order data from MySQL."""
    from sqlalchemy import create_engine

    engine = create_engine(get_connection_url())
    query = """
        SELECT
            product_id,
            DATE(order_date) AS order_day,
            SUM(quantity)    AS daily_demand
        FROM orders
        GROUP BY product_id, DATE(order_date)
        ORDER BY product_id, order_day
    """
    df = pd.read_sql(query, engine)
    engine.dispose()
    logger.info(f"Loaded {len(df):,} daily demand records")
    return df


def forecast_product(product_df: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
    """
    Fit a linear regression model for a single product and predict
    demand for the next `days_ahead` days.

    Parameters
    ----------
    product_df : pd.DataFrame
        Must have columns: order_day (datetime), daily_demand (int).
    days_ahead : int
        Number of future days to forecast.

    Returns
    -------
    pd.DataFrame
        Columns: forecast_date, predicted_demand.
    """
    from sklearn.linear_model import LinearRegression

    df = product_df.copy()
    df["order_day"] = pd.to_datetime(df["order_day"])
    df = df.sort_values("order_day")

    # Create numeric feature: days since first order
    reference = df["order_day"].min()
    df["day_num"] = (df["order_day"] - reference).dt.days

    X = df[["day_num"]].values
    y = df["daily_demand"].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict future days
    last_day = df["day_num"].max()
    future_days = np.arange(last_day + 1, last_day + 1 + days_ahead).reshape(-1, 1)
    predictions = model.predict(future_days)

    # Build result DataFrame
    future_dates = [
        reference + timedelta(days=int(d)) for d in future_days.flatten()
    ]

    return pd.DataFrame({
        "forecast_date":    future_dates,
        "predicted_demand": np.maximum(predictions, 0).round(2),  # no negative demand
    })


def run_forecasting(top_n: int = 10, days_ahead: int = 30) -> pd.DataFrame:
    """
    Run demand forecasting for the top N products by total demand.

    Parameters
    ----------
    top_n : int
        Number of top products to forecast.
    days_ahead : int
        Forecast horizon in days.

    Returns
    -------
    pd.DataFrame
        Combined forecast for all selected products.
    """
    logger.info(f"Running demand forecast for top {top_n} products, {days_ahead} days ahead")

    history = load_order_history()

    # Identify top products
    top_products = (
        history.groupby("product_id")["daily_demand"]
        .sum()
        .nlargest(top_n)
        .index
        .tolist()
    )
    logger.info(f"Top products: {top_products}")

    all_forecasts = []
    for pid in top_products:
        product_data = history[history["product_id"] == pid]
        if len(product_data) < 5:
            logger.warning(f"  Skipping {pid} – insufficient data ({len(product_data)} points)")
            continue

        forecast = forecast_product(product_data, days_ahead)
        forecast["product_id"] = pid
        forecast["model_used"] = "LinearRegression"
        all_forecasts.append(forecast)
        logger.info(f"  ✔ {pid}: forecasted {len(forecast)} days")

    if not all_forecasts:
        logger.warning("No forecasts generated!")
        return pd.DataFrame()

    result = pd.concat(all_forecasts, ignore_index=True)

    # Store in MySQL
    _store_forecast(result)

    return result


def _store_forecast(df: pd.DataFrame) -> None:
    """Write forecast results to the demand_forecast table."""
    from sqlalchemy import create_engine

    engine = create_engine(get_connection_url())
    df.to_sql("demand_forecast", engine, if_exists="replace", index=False, chunksize=500)
    engine.dispose()
    logger.info(f"Stored {len(df):,} forecast records in demand_forecast table")


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    result = run_forecasting(top_n=10, days_ahead=30)
    if not result.empty:
        print(result.head(20).to_string(index=False))
    else:
        print("No forecast data generated.")
