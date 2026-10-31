-- Q1.5 | Order status mix and missing delivery timestamps
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Supporting check: which order statuses exist and how many orders lack delivery dates.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  order_status,
  COUNT(*) AS orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders,
  SUM(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END)             AS missing_approved_at,
  SUM(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 ELSE 0 END)  AS missing_carrier_date,
  SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS missing_customer_date
FROM target.orders
GROUP BY order_status
ORDER BY orders DESC;
