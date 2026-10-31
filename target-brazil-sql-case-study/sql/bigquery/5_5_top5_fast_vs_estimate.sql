-- Q5.5 | Top 5 states where delivery is fastest compared to the estimate
-- Section : 5. Sales, freight & delivery time
-- Question: Find out the top 5 states where the order delivery is really fast as compared to the estimated date of delivery (difference between the averages of actual & estimated delivery time).
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH d AS (
  SELECT
    c.customer_state,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)     AS actual_days,
    TIMESTAMP_DIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp, DAY)     AS estimated_days,
    CASE WHEN TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END AS is_late
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
