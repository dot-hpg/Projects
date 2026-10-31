-- Q4.2 | Cost of orders by month, 2017 vs 2018 (Jan-Aug)
-- Section : 4. Impact on economy: money movement
-- Question: Supporting view for 4.1: where in the year did the growth come from?
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  EXTRACT(MONTH FROM o.order_purchase_timestamp) AS month_no,
  ROUND(SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END), 2) AS cost_2017,
  ROUND(SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2018 THEN p.payment_value END), 2) AS cost_2018,
  ROUND(100 * (SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2018 THEN p.payment_value END)
             - SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END))
        / SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END), 2) AS yoy_pct
FROM target.orders AS o
JOIN target.payments AS p
  ON o.order_id = p.order_id
WHERE EXTRACT(MONTH FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
GROUP BY month_no
ORDER BY month_no;
