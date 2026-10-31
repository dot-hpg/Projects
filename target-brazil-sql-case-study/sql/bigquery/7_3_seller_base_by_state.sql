-- Q7.3 | Where are the sellers? Seller vs customer concentration
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: share of sellers vs share of customers by state (supply-demand gap).
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH sellers_by_state AS (
  SELECT seller_state AS state, COUNT(*) AS sellers
  FROM target.sellers
  GROUP BY seller_state
),
customers_by_state AS (
  SELECT customer_state AS state, COUNT(DISTINCT customer_unique_id) AS customers
  FROM target.customers
  GROUP BY customer_state
)
SELECT
  c.state,
  c.customers,
  COALESCE(s.sellers, 0) AS sellers,
  ROUND(100 * c.customers / SUM(c.customers) OVER (), 2) AS pct_customers,
  ROUND(100 * COALESCE(s.sellers, 0) / SUM(COALESCE(s.sellers, 0)) OVER (), 2) AS pct_sellers,
  ROUND(c.customers / NULLIF(s.sellers, 0), 1) AS customers_per_seller
FROM customers_by_state AS c
LEFT JOIN sellers_by_state AS s ON c.state = s.state
ORDER BY c.customers DESC;
