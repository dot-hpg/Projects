-- Q5.2 | Delivery performance summary (supporting 5.1)
-- Section : 5. Sales, freight & delivery time
-- Question: Supporting view: overall distribution of delivery time and lateness.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH d AS (
  SELECT
    CAST(TRUNC(DATE_DIFF('second', order_purchase_timestamp, order_delivered_customer_date) / 86400.0) AS BIGINT)      AS time_to_deliver,
    CAST(TRUNC(DATE_DIFF('second', order_estimated_delivery_date, order_delivered_customer_date) / 86400.0) AS BIGINT) AS diff_estimated_delivery
  FROM target.orders
  WHERE order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL
)
SELECT
  COUNT(*) AS delivered_orders,
  ROUND(AVG(time_to_deliver), 2) AS avg_days_to_deliver,
  MIN(time_to_deliver) AS min_days,
  MAX(time_to_deliver) AS max_days,
  ROUND(AVG(diff_estimated_delivery), 2) AS avg_days_vs_estimate,
  SUM(CASE WHEN diff_estimated_delivery > 0 THEN 1 ELSE 0 END) AS late_orders,
  ROUND(100 * SUM(CASE WHEN diff_estimated_delivery > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_late
FROM d;
