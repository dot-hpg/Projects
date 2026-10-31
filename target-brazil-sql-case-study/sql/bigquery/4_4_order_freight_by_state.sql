-- Q4.4 | Total & average freight value for each state
-- Section : 4. Impact on economy: money movement
-- Question: Calculate the Total & Average value of order freight for each state.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  c.customer_state,
  ROUND(SUM(oi.freight_value), 2) AS total_freight_value,
  ROUND(AVG(oi.freight_value), 2) AS avg_freight_per_item,
  ROUND(SUM(oi.freight_value) / COUNT(DISTINCT oi.order_id), 2) AS avg_freight_per_order,
  ROUND(100 * SUM(oi.freight_value) / SUM(oi.price), 2) AS freight_as_pct_of_price
FROM target.orders AS o
JOIN target.customers   AS c  ON o.customer_id = c.customer_id
JOIN target.order_items AS oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_freight_value DESC;
