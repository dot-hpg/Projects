-- Q4.1 | % increase in cost of orders, 2017 vs 2018 (Jan-Aug)
-- Section : 4. Impact on economy: money movement
-- Question: Get the % increase in the cost of orders from year 2017 to 2018 (include months between Jan to Aug only), using payment_value.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH yearly_cost AS (
  SELECT
    EXTRACT(YEAR FROM o.order_purchase_timestamp) AS order_year,
    SUM(p.payment_value) AS total_cost
  FROM target.orders AS o
  JOIN target.payments AS p
    ON o.order_id = p.order_id
  WHERE EXTRACT(YEAR  FROM o.order_purchase_timestamp) IN (2017, 2018)
    AND EXTRACT(MONTH FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
  GROUP BY order_year
)
SELECT
  ROUND(MAX(CASE WHEN order_year = 2017 THEN total_cost END), 2) AS cost_2017_jan_aug,
  ROUND(MAX(CASE WHEN order_year = 2018 THEN total_cost END), 2) AS cost_2018_jan_aug,
  ROUND(100 * (MAX(CASE WHEN order_year = 2018 THEN total_cost END)
             - MAX(CASE WHEN order_year = 2017 THEN total_cost END))
        / MAX(CASE WHEN order_year = 2017 THEN total_cost END), 2) AS pct_increase
FROM yearly_cost;
