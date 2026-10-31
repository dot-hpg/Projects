-- Q7.4 | Top product categories by revenue
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: which categories drive revenue, and how satisfied are their buyers?
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH r AS (
  SELECT order_id, AVG(review_score) AS review_score
  FROM target.order_reviews
  GROUP BY order_id
)
SELECT
  COALESCE(p.product_category_name, 'unknown') AS category,
  COUNT(DISTINCT oi.order_id) AS orders,
  ROUND(SUM(oi.price), 2) AS revenue,
  ROUND(100 * SUM(oi.price) / SUM(SUM(oi.price)) OVER (), 2) AS pct_revenue,
  ROUND(AVG(oi.price), 2) AS avg_item_price,
  ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM target.order_items AS oi
LEFT JOIN target.products AS p ON oi.product_id = p.product_id
LEFT JOIN r ON oi.order_id = r.order_id
GROUP BY category
ORDER BY revenue DESC
LIMIT 15;
