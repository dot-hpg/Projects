-- Q1.4 | Data profile: row counts and key coverage for every table
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Supporting check: size of every table and how cleanly they join.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT 'orders'        AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT order_id)    AS distinct_keys FROM target.orders
UNION ALL SELECT 'customers',     COUNT(*), COUNT(DISTINCT customer_id)  FROM target.customers
UNION ALL SELECT 'order_items',   COUNT(*), COUNT(DISTINCT order_id)     FROM target.order_items
UNION ALL SELECT 'payments',      COUNT(*), COUNT(DISTINCT order_id)     FROM target.payments
UNION ALL SELECT 'order_reviews', COUNT(*), COUNT(DISTINCT order_id)     FROM target.order_reviews
UNION ALL SELECT 'products',      COUNT(*), COUNT(DISTINCT product_id)   FROM target.products
UNION ALL SELECT 'sellers',       COUNT(*), COUNT(DISTINCT seller_id)    FROM target.sellers
UNION ALL SELECT 'geolocation',   COUNT(*), COUNT(DISTINCT geolocation_zip_code_prefix) FROM target.geolocation
ORDER BY row_count DESC;
