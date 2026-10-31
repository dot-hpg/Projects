-- Q5.3 | Top 5 states with the highest & lowest average freight value
-- Section : 5. Sales, freight & delivery time
-- Question: Find out the top 5 states with the highest & lowest average freight value.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH state_freight AS (
  SELECT
    c.customer_state,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_value
  FROM target.orders AS o
  JOIN target.customers   AS c  ON o.customer_id = c.customer_id
  JOIN target.order_items AS oi ON o.order_id = oi.order_id
  GROUP BY c.customer_state
),
ranked AS (
  SELECT
    customer_state,
    avg_freight_value,
    ROW_NUMBER() OVER (ORDER BY avg_freight_value DESC) AS rank_high,
    ROW_NUMBER() OVER (ORDER BY avg_freight_value ASC)  AS rank_low
  FROM state_freight
)
SELECT
  h.rank_high          AS rank_no,
  h.customer_state     AS highest_freight_state,
  h.avg_freight_value  AS highest_avg_freight,
  l.customer_state     AS lowest_freight_state,
  l.avg_freight_value  AS lowest_avg_freight
FROM ranked AS h
JOIN ranked AS l
  ON h.rank_high = l.rank_low
WHERE h.rank_high <= 5
ORDER BY rank_no;
