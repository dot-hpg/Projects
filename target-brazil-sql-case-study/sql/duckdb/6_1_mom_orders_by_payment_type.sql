-- Q6.1 | Month-on-month orders by payment type
-- Section : 6. Payments
-- Question: Find the month on month no. of orders placed using different payment types.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  STRFTIME(o.order_purchase_timestamp, '%Y-%m') AS order_month,
  p.payment_type,
  COUNT(DISTINCT o.order_id) AS total_orders
FROM target.orders AS o
JOIN target.payments AS p
  ON o.order_id = p.order_id
GROUP BY order_month, p.payment_type
ORDER BY order_month, total_orders DESC;
