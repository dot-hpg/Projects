-- Q2.2 | Is there a growing trend in orders? (month-by-month series)
-- Section : 2. In-depth exploration
-- Question: Is there a growing trend in the no. of orders placed over the past years? (monthly series with MoM change and 3-month rolling average)
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH monthly AS (
  SELECT
    STRFTIME(order_purchase_timestamp, '%Y-%m') AS order_month,
    COUNT(*) AS total_orders
  FROM target.orders
  GROUP BY order_month
)
SELECT
  order_month,
  total_orders,
  total_orders - LAG(total_orders) OVER (ORDER BY order_month) AS mom_change,
  ROUND(100 * (total_orders - LAG(total_orders) OVER (ORDER BY order_month))
        / NULLIF(LAG(total_orders) OVER (ORDER BY order_month), 0), 2) AS mom_change_pct,
  ROUND(AVG(total_orders) OVER (ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0) AS rolling_3m_avg
FROM monthly
ORDER BY order_month;
