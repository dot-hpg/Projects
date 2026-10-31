-- Q2.4 | Time of day when Brazilian customers place orders
-- Section : 2. In-depth exploration
-- Question: During what time of the day do Brazilian customers mostly place their orders? (0-6 Dawn, 7-12 Morning, 13-18 Afternoon, 19-23 Night)
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  CASE
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 0  AND 6  THEN 'Dawn'
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 7  AND 12 THEN 'Morning'
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
    ELSE 'Night'
  END AS time_of_day,
  COUNT(*) AS total_orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders
FROM target.orders
GROUP BY time_of_day
ORDER BY total_orders DESC;
