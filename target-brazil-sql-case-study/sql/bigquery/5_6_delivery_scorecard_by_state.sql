-- Q5.6 | State delivery scorecard (all 27 states)
-- Section : 5. Sales, freight & delivery time
-- Question: Supporting view: delivery speed, buffer vs estimate, lateness and freight side by side for every state.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH d AS (
  SELECT
    c.customer_state,
    o.order_id,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) AS actual_days,
    TIMESTAMP_DIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp, DAY) AS estimated_days,
    CASE WHEN TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END AS is_late
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
),
f AS (
  SELECT c.customer_state, AVG(oi.freight_value) AS avg_freight
  FROM target.orders AS o
  JOIN target.customers   AS c  ON o.customer_id = c.customer_id
  JOIN target.order_items AS oi ON o.order_id = oi.order_id
  GROUP BY c.customer_state
)
SELECT
  d.customer_state,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(d.actual_days), 2) AS avg_actual_days,
  ROUND(AVG(d.estimated_days) - AVG(d.actual_days), 2) AS days_faster_than_estimate,
  ROUND(100 * AVG(d.is_late), 2) AS pct_late,
  ROUND(MAX(f.avg_freight), 2) AS avg_freight_per_item
FROM d
JOIN f ON d.customer_state = f.customer_state
GROUP BY d.customer_state
ORDER BY avg_actual_days DESC;
