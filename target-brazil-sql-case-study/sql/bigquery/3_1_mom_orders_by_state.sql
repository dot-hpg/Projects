-- Q3.1 | Month-on-month number of orders placed in each state
-- Section : 3. Evolution of e-commerce orders in the Brazil region
-- Question: Get the month on month no. of orders placed in each state.
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH state_month AS (
  SELECT
    c.customer_state,
    EXTRACT(YEAR  FROM o.order_purchase_timestamp) AS order_year,
    EXTRACT(MONTH FROM o.order_purchase_timestamp) AS order_month,
    COUNT(o.order_id) AS total_orders
  FROM target.orders AS o
  JOIN target.customers AS c
    ON o.customer_id = c.customer_id
  GROUP BY c.customer_state, order_year, order_month
)
SELECT
  customer_state,
  order_year,
  order_month,
  total_orders,
  total_orders - LAG(total_orders) OVER (
      PARTITION BY customer_state ORDER BY order_year, order_month) AS mom_change
FROM state_month
ORDER BY customer_state, order_year, order_month;
