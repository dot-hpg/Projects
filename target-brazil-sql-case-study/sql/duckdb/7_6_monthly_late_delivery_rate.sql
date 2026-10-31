-- Q7.6 | Do peaks break the delivery network?
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: monthly share of late deliveries and average delivery time (delivered orders, Jan 2017 - Aug 2018).
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  STRFTIME(order_purchase_timestamp, '%Y-%m') AS order_month,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(CAST(TRUNC(DATE_DIFF('second', order_purchase_timestamp, order_delivered_customer_date) / 86400.0) AS BIGINT)), 2) AS avg_delivery_days,
  ROUND(100 * AVG(CASE WHEN CAST(TRUNC(DATE_DIFF('second', order_estimated_delivery_date, order_delivered_customer_date) / 86400.0) AS BIGINT) > 0
                       THEN 1 ELSE 0 END), 2) AS pct_late
FROM target.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_purchase_timestamp >= '2017-01-01'
  AND order_purchase_timestamp <  '2018-09-01'
GROUP BY order_month
ORDER BY order_month;
