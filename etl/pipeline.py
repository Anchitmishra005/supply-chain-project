"""
=============================================================================
 ETL Pipeline Runner
=============================================================================
 Orchestrates the full Extract → Transform → Load pipeline.
 Can be run standalone or imported by Airflow tasks.
=============================================================================
"""

import os
import sys
import time

# Ensure project root is in the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.logger import get_logger
from etl.extract import extract_all
from etl.transform import transform_all
from etl.load import load_all

logger = get_logger("etl.pipeline")


def run_pipeline() -> None:
    """Execute the full ETL pipeline: Extract → Transform → Load."""
    start = time.time()

    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║   SUPPLY CHAIN ETL PIPELINE – Starting                  ║")
    logger.info("╚" + "═" * 58 + "╝")

    # ── STEP 1: Extract ─────────────────────────────────────────
    raw_data = extract_all()

    # ── STEP 2: Transform ───────────────────────────────────────
    cleaned_data = transform_all(raw_data)

    # ── STEP 3: Load ────────────────────────────────────────────
    load_all(cleaned_data)

    elapsed = time.time() - start
    logger.info("╔" + "═" * 58 + "╗")
    logger.info(f"║   Pipeline completed in {elapsed:.2f}s                          ║")
    logger.info("╚" + "═" * 58 + "╝")


if __name__ == "__main__":
    run_pipeline()
