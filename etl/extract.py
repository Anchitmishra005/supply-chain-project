"""
=============================================================================
 ETL – Extract Module
=============================================================================
 Reads raw CSV files from the data/ directory and returns DataFrames.
 Also includes an optional API simulator for demonstration purposes.
=============================================================================
"""

import os
import sys
import json
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.logger import get_logger

logger = get_logger("etl.extract")

# ---------------------------------------------------------------------------
# Data directory
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# ---------------------------------------------------------------------------
# CSV file map
# ---------------------------------------------------------------------------
CSV_FILES = {
    "suppliers":  "suppliers.csv",
    "inventory":  "inventory.csv",
    "orders":     "orders.csv",
    "shipments":  "shipments.csv",
}


def extract_csv(name: str) -> pd.DataFrame:
    """
    Load a single CSV file into a pandas DataFrame.

    Parameters
    ----------
    name : str
        Key from CSV_FILES (e.g. 'orders').

    Returns
    -------
    pd.DataFrame
    """
    filepath = os.path.join(DATA_DIR, CSV_FILES[name])
    logger.info(f"Extracting {name} from {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"CSV file missing: {filepath}")

    df = pd.read_csv(filepath)
    logger.info(f"  → {name}: {len(df):,} rows × {len(df.columns)} columns")
    return df


def extract_all() -> dict[str, pd.DataFrame]:
    """
    Extract all CSV datasets and return them in a dict.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keys: 'suppliers', 'inventory', 'orders', 'shipments'.
    """
    logger.info("=" * 50)
    logger.info("EXTRACT PHASE – loading all CSV files")
    logger.info("=" * 50)

    data = {}
    for name in CSV_FILES:
        data[name] = extract_csv(name)

    logger.info(f"Extraction complete  –  {len(data)} datasets loaded")
    return data


# =============================================================================
# Optional: Simple API Simulator
# =============================================================================
class SupplyChainAPIHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that serves CSV data as JSON for demo purposes."""

    data_cache: dict = {}

    def do_GET(self):  # noqa: N802
        path = self.path.strip("/")
        if path in self.data_cache:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = self.data_cache[path].to_dict(orient="records")
            self.wfile.write(json.dumps(payload[:100]).encode())  # limit to 100 rows
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        """Suppress default request logging."""
        pass


def start_api_server(port: int = 8765) -> HTTPServer:
    """
    Start a background API server that exposes datasets as JSON endpoints.

    Endpoints:
        GET /suppliers   → suppliers JSON
        GET /inventory   → inventory JSON
        GET /orders      → orders JSON
        GET /shipments   → shipments JSON

    Parameters
    ----------
    port : int
        Port to listen on.

    Returns
    -------
    HTTPServer
    """
    # Pre-load data
    SupplyChainAPIHandler.data_cache = extract_all()

    server = HTTPServer(("127.0.0.1", port), SupplyChainAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"API Simulator running at http://127.0.0.1:{port}")
    return server


def extract_from_api(endpoint: str, base_url: str = "http://127.0.0.1:8765") -> pd.DataFrame:
    """
    Fetch data from the API simulator.

    Parameters
    ----------
    endpoint : str
        One of: suppliers, inventory, orders, shipments.
    base_url : str
        Base URL of the API server.

    Returns
    -------
    pd.DataFrame
    """
    import urllib.request

    url = f"{base_url}/{endpoint}"
    logger.info(f"Fetching from API: {url}")

    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())

    df = pd.DataFrame(data)
    logger.info(f"  → {endpoint}: {len(df):,} rows from API")
    return df


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    datasets = extract_all()
    for name, df in datasets.items():
        print(f"\n{name}\n{'─' * 40}")
        print(df.head(3).to_string(index=False))
