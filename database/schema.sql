-- =============================================================================
--  Supply Chain Management – MySQL Database Schema
-- =============================================================================
--  This script creates all tables required for the supply chain data pipeline.
--  Run this ONCE before executing the ETL pipeline.
-- =============================================================================

-- Create the database (idempotent)
CREATE DATABASE IF NOT EXISTS supply_chain_db;
USE supply_chain_db;

-- =============================================================================
-- Drop existing tables (in correct dependency order)
-- =============================================================================
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS kpi_metrics;
DROP TABLE IF EXISTS demand_forecast;
DROP TABLE IF EXISTS stock_alerts;

-- =============================================================================
-- 1. Suppliers
-- =============================================================================
CREATE TABLE suppliers (
    supplier_id     VARCHAR(10)   PRIMARY KEY,
    supplier_name   VARCHAR(100)  NOT NULL,
    contact_email   VARCHAR(150),
    phone           VARCHAR(30),
    city            VARCHAR(50),
    country         VARCHAR(50),
    rating          DECIMAL(2,1)  CHECK (rating BETWEEN 1.0 AND 5.0),
    lead_time_days  INT           DEFAULT 0,
    active          TINYINT(1)    DEFAULT 1,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_supplier_country (country),
    INDEX idx_supplier_rating  (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 2. Inventory
-- =============================================================================
CREATE TABLE inventory (
    inventory_id      VARCHAR(12)   PRIMARY KEY,
    product_id        VARCHAR(100)  NOT NULL,
    product_name      VARCHAR(100)  NOT NULL,
    category          VARCHAR(50),
    warehouse_id      VARCHAR(20)   NOT NULL,
    supplier_id       VARCHAR(10),
    quantity_on_hand  INT           DEFAULT 0,
    reorder_point     INT           DEFAULT 100,
    unit_price        DECIMAL(10,2) DEFAULT 0.00,
    last_restock_date DATE,
    stock_status      VARCHAR(20)   DEFAULT 'In Stock',
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_inventory_product   (product_id),
    INDEX idx_inventory_warehouse (warehouse_id),
    INDEX idx_inventory_status    (stock_status),
    INDEX idx_inventory_supplier  (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 3. Orders
-- =============================================================================
CREATE TABLE orders (
    order_id        VARCHAR(12)    PRIMARY KEY,
    product_id      VARCHAR(100)   NOT NULL,
    customer_id     VARCHAR(12)    NOT NULL,
    quantity        INT            NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    total_amount    DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    order_date      DATE           NOT NULL,
    payment_method  VARCHAR(30),
    warehouse_id    VARCHAR(20),
    priority        VARCHAR(15)    DEFAULT 'Medium',
    created_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_order_product   (product_id),
    INDEX idx_order_customer  (customer_id),
    INDEX idx_order_date      (order_date),
    INDEX idx_order_warehouse (warehouse_id),
    INDEX idx_order_priority  (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 4. Shipments
-- =============================================================================
CREATE TABLE shipments (
    shipment_id          VARCHAR(12)   PRIMARY KEY,
    order_id             VARCHAR(12)   NOT NULL,
    supplier_id          VARCHAR(10),
    ship_date            DATE          NOT NULL,
    estimated_delivery   DATE,
    actual_delivery      DATE          NULL,
    delivery_status      VARCHAR(20)   DEFAULT 'Pending',
    delivery_delay_days  INT           NULL,
    carrier              VARCHAR(30),
    shipping_cost        DECIMAL(10,2) DEFAULT 0.00,
    created_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)    REFERENCES orders(order_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_shipment_order    (order_id),
    INDEX idx_shipment_status   (delivery_status),
    INDEX idx_shipment_date     (ship_date),
    INDEX idx_shipment_supplier (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 5. KPI Metrics  (populated by the ETL pipeline)
-- =============================================================================
CREATE TABLE kpi_metrics (
    metric_id          INT           AUTO_INCREMENT PRIMARY KEY,
    metric_name        VARCHAR(100)  NOT NULL,
    metric_value       DECIMAL(12,4),
    metric_date        DATE          NOT NULL,
    metric_category    VARCHAR(50),
    created_at         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_kpi_name (metric_name),
    INDEX idx_kpi_date (metric_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 6. Demand Forecast  (populated by the ML module)
-- =============================================================================
CREATE TABLE demand_forecast (
    forecast_id        INT           AUTO_INCREMENT PRIMARY KEY,
    product_id         VARCHAR(100)  NOT NULL,
    forecast_date      DATE          NOT NULL,
    predicted_demand   DECIMAL(10,2),
    model_used         VARCHAR(50)   DEFAULT 'LinearRegression',
    created_at         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_forecast_product (product_id),
    INDEX idx_forecast_date    (forecast_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- 7. Stock Alerts  (populated by the alert system)
-- =============================================================================
CREATE TABLE stock_alerts (
    alert_id           INT           AUTO_INCREMENT PRIMARY KEY,
    product_id         VARCHAR(100)  NOT NULL,
    warehouse_id       VARCHAR(20)   NOT NULL,
    current_stock      INT,
    reorder_point      INT,
    alert_type         VARCHAR(30)   DEFAULT 'Low Stock',
    alert_date         DATETIME      DEFAULT CURRENT_TIMESTAMP,
    resolved           TINYINT(1)    DEFAULT 0,

    INDEX idx_alert_product   (product_id),
    INDEX idx_alert_warehouse (warehouse_id),
    INDEX idx_alert_resolved  (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- Verification
-- =============================================================================
SELECT '✔ Schema created successfully!' AS status;
SHOW TABLES;
