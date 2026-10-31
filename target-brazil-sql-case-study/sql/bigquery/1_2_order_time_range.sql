-- Q1.2 | Time range between which the orders were placed
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Get the time range between which the orders were placed.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  MIN(order_purchase_timestamp) AS first_order_at,
  MAX(order_purchase_timestamp) AS last_order_at,
  TIMESTAMP_DIFF(MAX(order_purchase_timestamp), MIN(order_purchase_timestamp), DAY) AS span_in_days,
  COUNT(*) AS total_orders
FROM target.orders;
