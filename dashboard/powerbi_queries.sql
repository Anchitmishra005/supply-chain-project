-- =============================================================================
--  Power BI – SQL Queries for Dashboard Visuals
-- =============================================================================
--  Import these queries into Power BI using  Home → Get Data → MySQL
--  and choose "Advanced options" to enter custom SQL.
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────
-- 1. Monthly Revenue Trend
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    DATE_FORMAT(order_date, '%Y-%m')  AS order_month,
    COUNT(*)                          AS total_orders,
    SUM(quantity)                     AS total_units,
    ROUND(SUM(total_amount), 2)       AS total_revenue,
    ROUND(AVG(total_amount), 2)       AS avg_order_value
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;


-- ─────────────────────────────────────────────────────────────────────────
-- 2. Inventory Levels by Warehouse & Status
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    warehouse_id,
    stock_status,
    COUNT(*)                             AS item_count,
    SUM(quantity_on_hand)                AS total_stock,
    ROUND(SUM(quantity_on_hand * unit_price), 2) AS inventory_value
FROM inventory
GROUP BY warehouse_id, stock_status
ORDER BY warehouse_id, stock_status;


-- ─────────────────────────────────────────────────────────────────────────
-- 3. Delivery Delay Analysis
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    delivery_status,
    carrier,
    COUNT(*)                                      AS shipment_count,
    ROUND(AVG(DATEDIFF(actual_delivery, estimated_delivery)), 2) AS avg_delay_days,
    ROUND(AVG(shipping_cost), 2)                  AS avg_shipping_cost
FROM shipments
WHERE actual_delivery IS NOT NULL
GROUP BY delivery_status, carrier
ORDER BY avg_delay_days DESC;


-- ─────────────────────────────────────────────────────────────────────────
-- 4. Demand Trends (Daily Orders per Product)
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    product_id,
    order_date,
    SUM(quantity)      AS daily_demand,
    COUNT(*)           AS order_count,
    SUM(total_amount)  AS daily_revenue
FROM orders
GROUP BY product_id, order_date
ORDER BY product_id, order_date;


-- ─────────────────────────────────────────────────────────────────────────
-- 5. Low Stock Alerts
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    i.product_id,
    i.product_name,
    i.warehouse_id,
    i.quantity_on_hand,
    i.reorder_point,
    (i.reorder_point - i.quantity_on_hand)  AS deficit,
    s.supplier_name,
    s.lead_time_days
FROM inventory i
LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
WHERE i.quantity_on_hand < i.reorder_point
ORDER BY deficit DESC;


-- ─────────────────────────────────────────────────────────────────────────
-- 6. Supplier Performance Scorecard
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    s.supplier_id,
    s.supplier_name,
    s.city,
    s.country,
    s.rating,
    s.lead_time_days,
    COUNT(DISTINCT i.inventory_id)   AS products_supplied,
    COUNT(DISTINCT sh.shipment_id)   AS total_shipments,
    ROUND(AVG(DATEDIFF(sh.actual_delivery, sh.estimated_delivery)), 2) AS avg_delay
FROM suppliers s
LEFT JOIN inventory i  ON s.supplier_id = i.supplier_id
LEFT JOIN shipments sh ON s.supplier_id = sh.supplier_id
WHERE s.active = 1
GROUP BY s.supplier_id, s.supplier_name, s.city, s.country,
         s.rating, s.lead_time_days
ORDER BY s.rating DESC;


-- ─────────────────────────────────────────────────────────────────────────
-- 7. Order Fulfillment Summary
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    o.order_id,
    o.product_id,
    o.quantity                       AS ordered_qty,
    o.total_amount,
    o.priority,
    s.delivery_status,
    s.carrier,
    DATEDIFF(s.actual_delivery, o.order_date)  AS order_to_delivery_days
FROM orders o
LEFT JOIN shipments s ON o.order_id = s.order_id
ORDER BY o.order_date DESC;


-- ─────────────────────────────────────────────────────────────────────────
-- 8. KPI Summary (Latest Values)
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    metric_name,
    metric_value,
    metric_category,
    metric_date
FROM kpi_metrics
WHERE metric_date = (SELECT MAX(metric_date) FROM kpi_metrics)
ORDER BY metric_category, metric_name;


-- ─────────────────────────────────────────────────────────────────────────
-- 9. Demand Forecast Data
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    product_id,
    forecast_date,
    predicted_demand,
    model_used
FROM demand_forecast
ORDER BY product_id, forecast_date;


-- ─────────────────────────────────────────────────────────────────────────
-- 10. Revenue by Priority & Payment Method
-- ─────────────────────────────────────────────────────────────────────────
SELECT
    priority,
    payment_method,
    COUNT(*)                     AS order_count,
    ROUND(SUM(total_amount), 2)  AS total_revenue,
    ROUND(AVG(total_amount), 2)  AS avg_revenue
FROM orders
GROUP BY priority, payment_method
ORDER BY priority, total_revenue DESC;
