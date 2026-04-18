# ============================================================================
#  Power BI Dashboard – Setup & Configuration Guide
# ============================================================================
#
#  This document provides step-by-step instructions for building the
#  Supply Chain Analytics dashboard in Power BI Desktop.
#
# ============================================================================


# ────────────────────────────────────────────────────────────────────────────
# STEP 1: Connect Power BI to MySQL
# ────────────────────────────────────────────────────────────────────────────
#
#  1. Open Power BI Desktop
#  2. Click  Home → Get Data → MySQL database
#     (If you don't see MySQL, install the MySQL ODBC Connector first:
#      https://dev.mysql.com/downloads/connector/odbc/)
#  3. Enter connection details:
#        Server   :  localhost  (or your MySQL host IP)
#        Database :  supply_chain_db
#  4. Choose  Database  authentication and enter your MySQL credentials:
#        User     :  root
#        Password :  root   (change to match your setup)
#  5. Click  Connect
#  6. In the Navigator pane, select ALL tables:
#        ☑ suppliers
#        ☑ inventory
#        ☑ orders
#        ☑ shipments
#        ☑ kpi_metrics
#        ☑ demand_forecast
#        ☑ stock_alerts
#  7. Click  Load
#
# ────────────────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────────────────
# STEP 2: Define Relationships (Model View)
# ────────────────────────────────────────────────────────────────────────────
#
#  Go to  Model view  (left sidebar) and verify / create these relationships:
#
#  ┌──────────────┐      ┌──────────────┐
#  │  suppliers   │──1:M─│  inventory   │   (supplier_id)
#  └──────────────┘      └──────────────┘
#
#  ┌──────────────┐      ┌──────────────┐
#  │   orders     │──1:M─│  shipments   │   (order_id)
#  └──────────────┘      └──────────────┘
#
#  ┌──────────────┐      ┌──────────────┐
#  │  suppliers   │──1:M─│  shipments   │   (supplier_id)
#  └──────────────┘      └──────────────┘
#
# ────────────────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────────────────
# STEP 3: Recommended Visuals
# ────────────────────────────────────────────────────────────────────────────
#
#  PAGE 1:  Executive Overview
#  ─────────────────────────────
#   • KPI Cards (top row):
#       - Total Revenue           → SUM(orders[total_amount])
#       - Avg Delivery Time       → kpi_metrics filtered on metric_name
#       - On-Time Delivery Rate   → kpi_metrics filtered on metric_name
#       - Order Fulfillment Rate  → kpi_metrics filtered on metric_name
#
#   • Line Chart: Monthly Revenue
#       Axis  : orders[order_date] (Month)
#       Values: SUM(orders[total_amount])
#
#   • Pie Chart: Orders by Priority
#       Legend: orders[priority]
#       Values: COUNT(orders[order_id])
#
#
#  PAGE 2:  Inventory & Stock
#  ─────────────────────────────
#   • Stacked Bar Chart: Inventory by Warehouse
#       Axis  : inventory[warehouse_id]
#       Values: SUM(inventory[quantity_on_hand])
#       Legend: inventory[stock_status]
#
#   • Table: Low Stock Alerts
#       Columns: product_id, warehouse_id, current_stock,
#                reorder_point, alert_type
#       Filter : stock_alerts[resolved] = 0
#
#   • Gauge: Stockout Rate
#       Value  : Stockout Rate from kpi_metrics
#       Target : 5%
#
#
#  PAGE 3:  Delivery Performance
#  ──────────────────────────────
#   • Bar Chart: Delivery Status Distribution
#       Axis  : shipments[delivery_status]
#       Values: COUNT(shipments[shipment_id])
#
#   • Histogram: Delivery Delay Distribution
#       Axis  : shipments[delivery_delay_days] (bins)
#       Values: COUNT
#
#   • Scatter Plot: Shipping Cost vs Delay
#       X: shipments[shipping_cost]
#       Y: shipments[delivery_delay_days]
#
#
#  PAGE 4:  Demand Forecast
#  ──────────────────────────
#   • Line Chart: Predicted Demand
#       Axis  : demand_forecast[forecast_date]
#       Values: demand_forecast[predicted_demand]
#       Legend: demand_forecast[product_id]
#
#   • Clustered Bar: Historical vs Forecast Demand
#
#
#  PAGE 5:  Supplier Scorecard
#  ────────────────────────────
#   • Table: Supplier ratings with conditional formatting
#       Columns: supplier_id, supplier_name, country, rating,
#                lead_time_days, active
#
#   • Map: Supplier locations
#       Location: suppliers[city]
#       Size    : COUNT of inventory items supplied
#
# ────────────────────────────────────────────────────────────────────────────
