-- Q5.5 | Top 5 states where delivery is fastest compared to the estimate
-- Section : 5. Sales, freight & delivery time
-- Question: Find out the top 5 states where the order delivery is really fast as compared to the estimated date of delivery (difference between the averages of actual & estimated delivery time).
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH d AS (
  SELECT
    c.customer_state,
    CAST(TRUNC(DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_customer_date) / 86400.0) AS BIGINT)     AS actual_days,
    CAST(TRUNC(DATE_DIFF('second', o.order_purchase_timestamp, o.order_estimated_delivery_date) / 86400.0) AS BIGINT)     AS estimated_days,
    CASE WHEN CAST(TRUNC(DATE_DIFF('second', o.order_estimated_delivery_date, o.order_delivered_customer_date) / 86400.0) AS BIGINT) > 0 THEN 1 ELSE 0 END AS is_late
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
  customer_state,
  ROUND(AVG(actual_days), 2)    AS avg_actual_days,
  ROUND(AVG(estimated_days), 2) AS avg_estimated_days,
  ROUND(AVG(estimated_days) - AVG(actual_days), 2) AS days_faster_than_estimate,
  ROUND(100 * AVG(is_late), 2)  AS pct_late
FROM d
GROUP BY customer_state
ORDER BY days_faster_than_estimate DESC
LIMIT 5;
