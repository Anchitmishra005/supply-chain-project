"""
=============================================================================
 Apache Airflow DAG – Supply Chain ETL Pipeline
=============================================================================
 Schedule : Daily at 02:00 UTC
 Tasks    : generate_data → extract → transform → load → compute_kpis
 Retries  : 2 per task with 5-minute delay
=============================================================================
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# ---------------------------------------------------------------------------
# Default arguments
# ---------------------------------------------------------------------------
default_args = {
    "owner":            "data_engineering",
    "depends_on_past":  False,
    "email":            ["alerts@supplychain.example.com"],
    "email_on_failure": True,
    "email_on_retry":   False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
dag = DAG(
    dag_id="supply_chain_etl_pipeline",
    default_args=default_args,
    description="Daily ETL pipeline for supply chain data processing",
    schedule_interval="0 2 * * *",      # Every day at 2:00 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["supply_chain", "etl", "data_engineering"],
)


# =============================================================================
# Task callables  (thin wrappers that import & invoke project modules)
# =============================================================================

def task_generate_data(**kwargs):
    """Generate synthetic CSV datasets."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from data.generate_data import main as generate
    generate()
    kwargs["ti"].xcom_push(key="status", value="data_generated")


def task_extract(**kwargs):
    """Extract raw CSV files into DataFrames."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from etl.extract import extract_all
    data = extract_all()
    # Store row counts in XCom for downstream monitoring
    counts = {name: len(df) for name, df in data.items()}
    kwargs["ti"].xcom_push(key="row_counts", value=counts)
    return counts


def task_transform(**kwargs):
    """Transform and clean all datasets."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from etl.extract import extract_all
    from etl.transform import transform_all

    raw     = extract_all()
    cleaned = transform_all(raw)
    counts  = {name: len(df) for name, df in cleaned.items()}
    kwargs["ti"].xcom_push(key="transformed_counts", value=counts)
    return counts


def task_load(**kwargs):
    """Load cleaned data into MySQL."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from etl.extract import extract_all
    from etl.transform import transform_all
    from etl.load import load_all

    raw     = extract_all()
    cleaned = transform_all(raw)
    load_all(cleaned)
    kwargs["ti"].xcom_push(key="load_status", value="success")


def task_compute_kpis(**kwargs):
    """Compute and store KPI metrics after load."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from advanced.kpi_metrics import compute_and_store_kpis
    compute_and_store_kpis()
    kwargs["ti"].xcom_push(key="kpi_status", value="computed")


def task_check_alerts(**kwargs):
    """Check stock levels and raise alerts."""
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("AIRFLOW_HOME", "."), "project"))

    from advanced.alert_system import check_stock_alerts
    check_stock_alerts()
    kwargs["ti"].xcom_push(key="alert_status", value="checked")


# =============================================================================
# Task instantiation
# =============================================================================
with dag:

    t_generate = PythonOperator(
        task_id="generate_data",
        python_callable=task_generate_data,
        provide_context=True,
    )

    t_extract = PythonOperator(
        task_id="extract_data",
        python_callable=task_extract,
        provide_context=True,
    )

    t_transform = PythonOperator(
        task_id="transform_data",
        python_callable=task_transform,
        provide_context=True,
    )

    t_load = PythonOperator(
        task_id="load_to_mysql",
        python_callable=task_load,
        provide_context=True,
    )

    t_kpis = PythonOperator(
        task_id="compute_kpis",
        python_callable=task_compute_kpis,
        provide_context=True,
    )

    t_alerts = PythonOperator(
        task_id="check_stock_alerts",
        python_callable=task_check_alerts,
        provide_context=True,
    )

    # ── DAG dependency chain ────────────────────────────────────
    t_generate >> t_extract >> t_transform >> t_load >> [t_kpis, t_alerts]
