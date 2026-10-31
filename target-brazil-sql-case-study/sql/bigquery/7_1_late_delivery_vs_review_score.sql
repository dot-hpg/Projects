-- Q7.1 | Does late delivery hurt review scores?
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: average review score and share of 1-star reviews by how early or late the order arrived.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH d AS (
  SELECT
    o.order_id,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) AS days_vs_estimate
  FROM target.orders AS o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
),
r AS (
  SELECT order_id, AVG(review_score) AS review_score
  FROM target.order_reviews
  GROUP BY order_id
)
SELECT
  CASE
    WHEN d.days_vs_estimate <= -15 THEN '1. 15+ days early'
    WHEN d.days_vs_estimate <= -8  THEN '2. 8-14 days early'
    WHEN d.days_vs_estimate <= 0   THEN '3. 0-7 days early'
    WHEN d.days_vs_estimate <= 3   THEN '4. 1-3 days late'
    WHEN d.days_vs_estimate <= 7   THEN '5. 4-7 days late'
    ELSE                                '6. 8+ days late'
  END AS delivery_bucket,
  COUNT(*) AS orders,
  ROUND(AVG(r.review_score), 2) AS avg_review_score,
  ROUND(100 * AVG(CASE WHEN r.review_score <= 1 THEN 1 ELSE 0 END), 2) AS pct_1_star,
  ROUND(100 * AVG(CASE WHEN r.review_score >= 5 THEN 1 ELSE 0 END), 2) AS pct_5_star
FROM d
JOIN r ON d.order_id = r.order_id
GROUP BY delivery_bucket
ORDER BY delivery_bucket;
