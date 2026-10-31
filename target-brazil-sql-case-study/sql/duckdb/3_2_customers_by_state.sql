-- Q3.2 | How customers are distributed across states
-- Section : 3. Evolution of e-commerce orders in the Brazil region
-- Question: How are the customers distributed across all the states?
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

WITH by_state AS (
  SELECT
    customer_state,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    COUNT(DISTINCT customer_city)      AS cities_covered
  FROM target.customers
  GROUP BY customer_state
)
SELECT
  customer_state,
  unique_customers,
  ROUND(100 * unique_customers / SUM(unique_customers) OVER (), 2) AS pct_of_customers,
  ROUND(100 * SUM(unique_customers) OVER (ORDER BY unique_customers DESC, customer_state
                                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        / SUM(unique_customers) OVER (), 2) AS cumulative_pct,
  cities_covered
FROM by_state
ORDER BY unique_customers DESC;
