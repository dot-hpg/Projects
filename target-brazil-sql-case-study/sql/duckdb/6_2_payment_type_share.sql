-- Q6.2 | Payment type share, value and installments (supporting 6.1)
-- Section : 6. Payments
-- Question: Supporting view: share of orders and value by payment type.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  payment_type,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(100 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM target.payments), 2)
    AS pct_of_orders,
  ROUND(SUM(payment_value), 2) AS total_value,
  ROUND(AVG(payment_value), 2) AS avg_payment_value,
  ROUND(AVG(payment_installments), 2) AS avg_installments
FROM target.payments
GROUP BY payment_type
ORDER BY orders DESC;
