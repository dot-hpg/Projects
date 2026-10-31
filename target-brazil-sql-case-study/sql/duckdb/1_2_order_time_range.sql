-- Q1.2 | Time range between which the orders were placed
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Get the time range between which the orders were placed.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  MIN(order_purchase_timestamp) AS first_order_at,
  MAX(order_purchase_timestamp) AS last_order_at,
  CAST(TRUNC(DATE_DIFF('second', MIN(order_purchase_timestamp), MAX(order_purchase_timestamp)) / 86400.0) AS BIGINT) AS span_in_days,
  COUNT(*) AS total_orders
FROM target.orders;
