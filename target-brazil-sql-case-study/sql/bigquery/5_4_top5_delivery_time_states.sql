-- Q5.4 | Top 5 states with the highest & lowest average delivery time
-- Section : 5. Sales, freight & delivery time
-- Question: Find out the top 5 states with the highest & lowest average delivery time.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH state_delivery AS (
  SELECT
    c.customer_state,
    ROUND(AVG(TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)), 2)
      AS avg_delivery_days
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
  GROUP BY c.customer_state
),
ranked AS (
  SELECT
    customer_state,
    avg_delivery_days,
    ROW_NUMBER() OVER (ORDER BY avg_delivery_days DESC) AS rank_slow,
    ROW_NUMBER() OVER (ORDER BY avg_delivery_days ASC)  AS rank_fast
  FROM state_delivery
)
SELECT
  s.rank_slow          AS rank_no,
  s.customer_state     AS slowest_state,
  s.avg_delivery_days  AS slowest_avg_days,
  f.customer_state     AS fastest_state,
  f.avg_delivery_days  AS fastest_avg_days
FROM ranked AS s
JOIN ranked AS f
  ON s.rank_slow = f.rank_fast
WHERE s.rank_slow <= 5
ORDER BY rank_no;
