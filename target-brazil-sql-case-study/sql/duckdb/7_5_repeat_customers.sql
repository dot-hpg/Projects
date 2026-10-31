-- Q7.5 | How many customers come back?
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: distribution of customers by number of orders placed (uses customer_unique_id).
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH per_customer AS (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS orders
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  GROUP BY c.customer_unique_id
)
SELECT
  CASE WHEN orders >= 4 THEN '4+' ELSE CAST(orders AS STRING) END AS orders_per_customer,
  COUNT(*) AS customers,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers
FROM per_customer
GROUP BY orders_per_customer
ORDER BY orders_per_customer;
