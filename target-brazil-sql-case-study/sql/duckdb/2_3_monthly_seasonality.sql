-- Q2.3 | Monthly seasonality in the number of orders
-- Section : 2. In-depth exploration
-- Question: Can we see some kind of monthly seasonality in terms of the no. of orders being placed?
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

-- Calendar month on rows, year on columns, so the same month can be compared across years.
SELECT
  EXTRACT(MONTH FROM order_purchase_timestamp) AS month_no,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2016 THEN 1 ELSE 0 END) AS orders_2016,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2017 THEN 1 ELSE 0 END) AS orders_2017,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2018 THEN 1 ELSE 0 END) AS orders_2018,
  COUNT(*) AS total_orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_orders
FROM target.orders
GROUP BY month_no
ORDER BY month_no;
