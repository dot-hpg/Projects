-- Q6.3 | Number of orders by payment installments
-- Section : 6. Payments
-- Question: Find the no. of orders placed on the basis of the payment installments that have been paid.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  payment_installments,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(100 * COUNT(DISTINCT order_id)
        / SUM(COUNT(DISTINCT order_id)) OVER (), 2) AS pct_of_orders,
  ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM target.payments
GROUP BY payment_installments
ORDER BY payment_installments;
