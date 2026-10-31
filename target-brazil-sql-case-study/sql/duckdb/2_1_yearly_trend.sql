-- Q2.1 | Is there a growing trend in orders over the years? (yearly view)
-- Section : 2. In-depth exploration
-- Question: Is there a growing trend in the no. of orders placed over the past years?
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

-- 2016 and 2018 are partial years, so the like-for-like comparison is Jan-Aug.
WITH yearly AS (
  SELECT
    EXTRACT(YEAR FROM order_purchase_timestamp) AS order_year,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_purchase_timestamp) BETWEEN 1 AND 8 THEN 1 ELSE 0 END)
      AS jan_aug_orders,
    COUNT(DISTINCT EXTRACT(MONTH FROM order_purchase_timestamp)) AS active_months
  FROM target.orders
  GROUP BY order_year
)
SELECT
  order_year,
  active_months,
  total_orders,
  ROUND(total_orders / active_months, 0) AS avg_orders_per_active_month,
  jan_aug_orders,
  ROUND(100 * (jan_aug_orders - LAG(jan_aug_orders) OVER (ORDER BY order_year))
        / NULLIF(LAG(jan_aug_orders) OVER (ORDER BY order_year), 0), 2) AS jan_aug_yoy_growth_pct
FROM yearly
ORDER BY order_year;
