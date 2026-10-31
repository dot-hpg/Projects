-- Q5.1 | Delivery time and estimated-vs-actual gap per order (single query)
-- Section : 5. Sales, freight & delivery time
-- Question: Find the no. of days taken to deliver each order from the purchase date (time_to_deliver) and the difference in days between the actual & estimated delivery date (diff_estimated_delivery), in a single query.
-- Dialect : BigQuery Standard SQL (dataset `target`)

-- time_to_deliver         = order_delivered_customer_date - order_purchase_timestamp
-- diff_estimated_delivery = order_delivered_customer_date - order_estimated_delivery_date
--   (negative = delivered BEFORE the estimate, positive = days late;
--    an order counts as late throughout this study when diff_estimated_delivery > 0)
SELECT
  order_id,
  order_purchase_timestamp,
  order_delivered_customer_date,
  order_estimated_delivery_date,
  TIMESTAMP_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY)      AS time_to_deliver,
  TIMESTAMP_DIFF(order_delivered_customer_date, order_estimated_delivery_date, DAY) AS diff_estimated_delivery
FROM target.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
ORDER BY order_purchase_timestamp;
