-- Q4.3 | Total & average order price for each state
-- Section : 4. Impact on economy: money movement
-- Question: Calculate the Total & Average value of order price for each state.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  c.customer_state,
  ROUND(SUM(oi.price), 2) AS total_order_price,
  ROUND(AVG(oi.price), 2) AS avg_price_per_item,
  ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id), 2) AS avg_price_per_order,
  COUNT(DISTINCT oi.order_id) AS orders
FROM target.orders AS o
JOIN target.customers   AS c  ON o.customer_id = c.customer_id
JOIN target.order_items AS oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_order_price DESC;
