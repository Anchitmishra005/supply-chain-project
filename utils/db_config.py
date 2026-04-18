"""
=============================================================================
 Database Configuration
=============================================================================
 Centralised MySQL connection settings used across the entire project.
 Update the values below to match your local MySQL installation.
=============================================================================
"""

import os

# ---------------------------------------------------------------------------
# MySQL Connection Parameters
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "user":     os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Anchit45"),   # ← updated based on user input
    "database": os.getenv("MYSQL_DATABASE", "supply_chain_db"),
    "charset":  "utf8mb4",
}

# ---------------------------------------------------------------------------
# SQLAlchemy connection URL  (used by pandas and the ETL loader)
# ---------------------------------------------------------------------------
def get_connection_url() -> str:
    """Build a mysql+pymysql:// connection string."""
    c = DB_CONFIG
    return (
        f"mysql+pymysql://{c['user']}:{c['password']}"
        f"@{c['host']}:{c['port']}/{c['database']}"
        f"?charset={c['charset']}"
    )

# ---------------------------------------------------------------------------
# Quick connectivity test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from sqlalchemy import create_engine, text
    engine = create_engine(get_connection_url())
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✔ Database connection successful!" if result else "✘ Connection failed!")
