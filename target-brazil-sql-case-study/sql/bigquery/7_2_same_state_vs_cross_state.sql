-- Q7.2 | Same-state vs cross-state fulfilment
-- Section : 7. Bonus deep-dives (beyond the brief)
-- Question: Bonus: how much faster and cheaper is an order when the seller is in the customer's state?
-- Dialect : BigQuery Standard SQL (dataset `target`)

WITH item_level AS (
  SELECT
    o.order_id,
    CASE WHEN s.seller_state = c.customer_state THEN 'Same state' ELSE 'Cross state' END AS route,
    oi.freight_value,
    oi.price,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) AS actual_days,
    CASE WHEN TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END AS is_late
  FROM target.orders AS o
  JOIN target.customers   AS c  ON o.customer_id = c.customer_id
  JOIN target.order_items AS oi ON o.order_id = oi.order_id
  JOIN target.sellers     AS s  ON oi.seller_id = s.seller_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
  route,
  COUNT(*) AS items,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_items,
  ROUND(AVG(actual_days), 2) AS avg_delivery_days,
  ROUND(AVG(freight_value), 2) AS avg_freight,
  ROUND(100 * SUM(freight_value) / SUM(price), 2) AS freight_pct_of_price,
  ROUND(100 * AVG(is_late), 2) AS pct_late
FROM item_level
GROUP BY route
ORDER BY items DESC;
