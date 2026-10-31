-- Q7.6 | Do peaks break the delivery network?
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: monthly share of late deliveries and average delivery time (delivered orders, Jan 2017 - Aug 2018).
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  FORMAT_TIMESTAMP('%Y-%m', order_purchase_timestamp) AS order_month,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(TIMESTAMP_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY)), 2) AS avg_delivery_days,
  ROUND(100 * AVG(CASE WHEN TIMESTAMP_DIFF(order_delivered_customer_date, order_estimated_delivery_date, DAY) > 0
                       THEN 1 ELSE 0 END), 2) AS pct_late
FROM target.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_purchase_timestamp >= '2017-01-01'
  AND order_purchase_timestamp <  '2018-09-01'
GROUP BY order_month
ORDER BY order_month;
