# 📊 Supply Chain Data Pipeline

> An end-to-end **Data Engineering** project that simulates a real-world supply chain system using **Python**, **MySQL**, **Apache Airflow**, and **Power BI**.

---

## 📐 Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Data Sources   │────▶│  Python ETL  │────▶│   Apache    │────▶│   MySQL     │────▶│  Power BI    │
│  (CSV / API)    │     │  Extract     │     │   Airflow   │     │  Database   │     │  Dashboard   │
│                 │     │  Transform   │     │  (Scheduler)│     │             │     │              │
│                 │     │  Load        │     │             │     │             │     │              │
└─────────────────┘     └──────────────┘     └─────────────┘     └─────────────┘     └──────────────┘
```

**Data Flow:**
1. **Generate** → Synthetic CSV datasets (suppliers, inventory, orders, shipments)
2. **Extract**  → Load CSVs into pandas DataFrames
3. **Transform** → Clean, validate, and enrich data (derived features, joins)
4. **Load**     → Bulk insert into MySQL with FK-aware ordering
5. **Schedule** → Airflow DAG automates the pipeline daily
6. **Visualize** → Power BI dashboards consume MySQL data

---

## 🛠 Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.11+                      |
| Database         | MySQL 8.0                         |
| ETL Framework    | pandas, SQLAlchemy, PyMySQL       |
| Scheduling       | Apache Airflow 2.7+               |
| ML/Forecasting   | scikit-learn (Linear Regression)  |
| Visualization    | Power BI Desktop                  |
| Containerization | Docker & Docker Compose           |
| Version Control  | Git                               |

---

## 📁 Project Structure

```
Supply chain management/
├── data/                          # Raw & generated datasets
│   └── generate_data.py           # Synthetic data generator (1000+ rows)
│
├── database/                      # Database layer
│   └── schema.sql                 # MySQL schema (7 tables, FKs, indexes)
│
├── etl/                           # ETL pipeline modules
│   ├── __init__.py
│   ├── extract.py                 # Extract – CSV loading + API simulator
│   ├── transform.py               # Transform – cleaning & feature engineering
│   ├── load.py                    # Load – bulk insert into MySQL
│   └── pipeline.py                # Pipeline orchestrator
│
├── airflow_dags/                  # Airflow DAGs
│   └── supply_chain_dag.py        # Daily scheduled DAG
│
├── advanced/                      # Advanced analytics
│   ├── __init__.py
│   ├── demand_forecast.py         # ML demand forecasting
│   ├── alert_system.py            # Low-stock alert system
│   └── kpi_metrics.py             # KPI computation engine
│
├── dashboard/                     # Power BI resources
│   ├── powerbi_setup_guide.py     # Step-by-step setup instructions
│   └── powerbi_queries.sql        # 10 production SQL queries
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   ├── db_config.py               # MySQL connection config
│   └── logger.py                  # Rotating file + console logger
│
├── logs/                          # Log files (auto-created)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image
├── docker-compose.yml             # Multi-service orchestration
├── .gitignore
└── README.md                      # ← You are here
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.11+**
- **MySQL 8.0** (local or Docker)
- **pip** (Python package manager)

### 1. Clone & Install Dependencies

```bash
cd "Supply chain management"
pip install -r requirements.txt
```

### 2. Set Up MySQL Database

**Option A – Local MySQL:**
```bash
mysql -u root -p < database/schema.sql
```

**Option B – Docker:**
```bash
docker-compose up -d mysql
# Schema is auto-initialized from database/schema.sql
```

### 3. Configure Database Connection

Edit `utils/db_config.py` or set environment variables:

```bash
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=root
set MYSQL_DATABASE=supply_chain_db
```

### 4. Generate Synthetic Data

```bash
python data/generate_data.py
```

This creates 4 CSV files in the `data/` directory:
- `suppliers.csv` (200 rows)
- `inventory.csv` (1,000 rows)
- `orders.csv` (1,500 rows)
- `shipments.csv` (1,500 rows)

### 5. Run the ETL Pipeline

```bash
python -m etl.pipeline
```

This executes: **Extract → Transform → Load** and populates all MySQL tables.

### 6. Run Advanced Analytics

```bash
# Compute KPI metrics
python -m advanced.kpi_metrics

# Check stock alerts
python -m advanced.alert_system

# Run demand forecasting
python -m advanced.demand_forecast
```

---

## ⏰ Apache Airflow Setup

### Local Setup

```bash
# Initialize Airflow (first time only)
airflow db init
airflow users create --username admin --password admin \
    --firstname Admin --lastname User --role Admin --email admin@example.com

# Copy the DAG file
cp airflow_dags/supply_chain_dag.py ~/airflow/dags/

# Start Airflow
airflow webserver --port 8080 &
airflow scheduler &
```

### Docker Setup

```bash
docker-compose up -d
# Access Airflow UI at http://localhost:8080
# Default credentials: admin / admin (check console output)
```

### DAG Details

| Property       | Value                              |
|---------------|-------------------------------------|
| DAG ID        | `supply_chain_etl_pipeline`         |
| Schedule      | Daily at 02:00 UTC (`0 2 * * *`)   |
| Tasks         | generate → extract → transform → load → [kpis, alerts] |
| Retries       | 2 per task, 5-minute delay          |
| Timeout       | 30 minutes per task                 |

---

## 📊 Power BI Dashboard

### Connecting to MySQL

1. Open **Power BI Desktop**
2. **Home → Get Data → MySQL Database**
3. Enter: `Server: localhost`, `Database: supply_chain_db`
4. Authenticate with your MySQL credentials
5. Select all 7 tables → **Load**

### Dashboard Pages

| Page | Visuals |
|------|---------|
| **Executive Overview** | KPI cards, monthly revenue line chart, orders by priority pie chart |
| **Inventory & Stock** | Warehouse bar chart, low-stock alerts table, stockout gauge |
| **Delivery Performance** | Status distribution, delay histogram, cost vs delay scatter |
| **Demand Forecast** | Predicted demand line chart, historical vs forecast comparison |
| **Supplier Scorecard** | Ratings table with conditional formatting, supplier map |

### Pre-built SQL Queries

See `dashboard/powerbi_queries.sql` for 10 ready-to-use queries optimized for Power BI.

---

## 📈 Advanced Features

### 1. Demand Forecasting
- **Model:** scikit-learn Linear Regression
- **Input:** Historical daily order quantities
- **Output:** 30-day demand predictions per product
- **Storage:** `demand_forecast` table in MySQL

### 2. Alert System
- **Monitors:** Inventory levels vs. reorder points
- **Severity Levels:** Out of Stock → Critical → Low Stock → Warning
- **Storage:** `stock_alerts` table in MySQL
- **Trigger:** Automated via Airflow DAG

### 3. KPI Metrics
10 key metrics computed and stored daily:

| # | KPI | Category |
|---|-----|----------|
| 1 | Average Delivery Time | Delivery |
| 2 | On-Time Delivery Rate | Delivery |
| 3 | Order Fulfillment Rate | Orders |
| 4 | Average Order Value | Orders |
| 5 | Inventory Turnover Ratio | Inventory |
| 6 | Stockout Rate | Inventory |
| 7 | Total Revenue | Financial |
| 8 | Average Shipping Cost | Financial |
| 9 | Avg Supplier Rating | Suppliers |
| 10 | Critical Stock Percentage | Inventory |

---

## 🗄 Database Schema

```
┌──────────────┐       ┌──────────────┐
│  suppliers   │──1:M──│  inventory   │
│              │       │              │
│  supplier_id │       │  inventory_id│
│  name, city  │       │  product_id  │
│  rating      │       │  quantity    │
└──────┬───────┘       └──────────────┘
       │
       │ 1:M
       ▼
┌──────────────┐       ┌──────────────┐
│  shipments   │──M:1──│   orders     │
│              │       │              │
│  shipment_id │       │  order_id    │
│  delay_days  │       │  total_amount│
│  carrier     │       │  priority    │
└──────────────┘       └──────────────┘

       ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
       │  kpi_metrics  │  │demand_forecast│  │ stock_alerts  │
       └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🐳 Docker Usage

```bash
# Start everything (MySQL + Airflow)
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f mysql
docker-compose logs -f airflow

# Stop services
docker-compose down

# Stop & remove all data
docker-compose down -v
```

---

### Key Talking Points:
- **ETL Design:** Modular extract/transform/load with clear separation of concerns
- **Data Quality:** Null handling, type validation, referential integrity
- **Feature Engineering:** delivery_delay, stock_status, delay_category, supplier_tier
- **Scheduling:** Airflow DAG with dependency chain, retries, XCom metadata
- **Analytics:** Linear regression forecasting, automated alerting, 10 KPIs
- **Infrastructure:** Docker Compose, environment-based config, rotating logs

---

## 📄 License

This project is for educational and portfolio purposes.

---

