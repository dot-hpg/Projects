-- Q1.3 | Count of cities & states of customers who ordered
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Count the Cities & States of customers who ordered during the given period.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  COUNT(DISTINCT c.customer_city)  AS num_cities,
  COUNT(DISTINCT c.customer_state) AS num_states,
  COUNT(DISTINCT c.customer_unique_id) AS num_unique_customers,
  COUNT(DISTINCT o.order_id) AS num_orders
FROM target.orders AS o
JOIN target.customers AS c
  ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp BETWEEN
      (SELECT MIN(order_purchase_timestamp) FROM target.orders)
  AND (SELECT MAX(order_purchase_timestamp) FROM target.orders);
