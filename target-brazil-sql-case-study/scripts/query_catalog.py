"""Single source of truth for every SQL query in the case study.

Each query is written once in **BigQuery Standard SQL** (the dialect used on the
Scaler platform, dataset `target`).  `to_duckdb()` rewrites the handful of
dialect-specific functions so the identical logic runs locally on DuckDB.

`python scripts/export_sql.py` writes the catalog to sql/bigquery/ and sql/duckdb/.
"""

# ----------------------------------------------------------------------------
# Dialect bridge (BigQuery -> DuckDB)
# ----------------------------------------------------------------------------

def _split_call(sql: str, fname: str):
    """Yield (start, end, [args]) for each top-level call of `fname(...)`."""
    i = 0
    while True:
        i = sql.find(fname + "(", i)
        if i < 0:
            return
        j, depth, args, cur = i + len(fname) + 1, 1, [], ""
        while depth:
            ch = sql[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            if ch == "," and depth == 1:
                args.append(cur.strip()); cur = ""
            else:
                cur += ch
            j += 1
        args.append(cur.strip())
        yield i, j + 1, args
        i = j + 1


def _rewrite(sql: str, fname: str, fn) -> str:
    for start, end, args in reversed(list(_split_call(sql, fname))):
        sql = sql[:start] + fn(args) + sql[end:]
    return sql


def to_duckdb(sql: str) -> str:
    # BigQuery TIMESTAMP_DIFF(end, start, DAY) counts whole 24h periods (truncated toward 0)
    sql = _rewrite(sql, "TIMESTAMP_DIFF", lambda a: (
        f"CAST(TRUNC(DATE_DIFF('second', {a[1]}, {a[0]}) / 86400.0) AS BIGINT)"))
    # BigQuery FORMAT_TIMESTAMP(fmt, ts) -> DuckDB STRFTIME(ts, fmt)
    sql = _rewrite(sql, "FORMAT_TIMESTAMP", lambda a: f"STRFTIME({a[1]}, {a[0]})")
    sql = sql.replace("target.INFORMATION_SCHEMA.COLUMNS", "information_schema.columns")
    sql = sql.replace("WHERE table_name = 'customers'",
                      "WHERE table_schema = 'target' AND table_name = 'customers'")
    return sql


# ----------------------------------------------------------------------------
# Query catalog
# ----------------------------------------------------------------------------
Q = []


def q(qid, slug, section, title, question, sql):
    Q.append(dict(id=qid, slug=slug, section=section, title=title,
                  question=question, bigquery=sql.strip() + "\n",
                  duckdb=to_duckdb(sql.strip()) + "\n"))


S1 = "1. Initial exploration: structure & characteristics"
S2 = "2. In-depth exploration"
S3 = "3. Evolution of e-commerce orders in the Brazil region"
S4 = "4. Impact on economy: money movement"
S5 = "5. Sales, freight & delivery time"
S6 = "6. Payments"
S7 = "7. Bonus deep-dives (beyond the brief)"

# ---------------------------------------------------------------- Section 1 --
q("1.1", "customers_column_types", S1,
  "Data type of all columns in the customers table",
  "Data type of all columns in the \"customers\" table.",
  """
SELECT
  column_name,
  data_type
FROM target.INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'customers'
ORDER BY ordinal_position;
""")

q("1.2", "order_time_range", S1,
  "Time range between which the orders were placed",
  "Get the time range between which the orders were placed.",
  """
SELECT
  MIN(order_purchase_timestamp) AS first_order_at,
  MAX(order_purchase_timestamp) AS last_order_at,
  TIMESTAMP_DIFF(MAX(order_purchase_timestamp), MIN(order_purchase_timestamp), DAY) AS span_in_days,
  COUNT(*) AS total_orders
FROM target.orders;
""")

q("1.3", "cities_states_of_customers", S1,
  "Count of cities & states of customers who ordered",
  "Count the Cities & States of customers who ordered during the given period.",
  """
SELECT
  COUNT(DISTINCT c.customer_city)  AS num_cities,
  COUNT(DISTINCT c.customer_state) AS num_states,
  COUNT(DISTINCT c.customer_unique_id) AS num_unique_customers,
  COUNT(DISTINCT o.order_id) AS num_orders
FROM target.orders AS o
JOIN target.customers AS c
  ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp BETWEEN
      (SELECT MIN(order_purchase_timestamp) FROM target.orders)
  AND (SELECT MAX(order_purchase_timestamp) FROM target.orders);
""")

q("1.4", "table_profile", S1,
  "Data profile: row counts and key coverage for every table",
  "Supporting check: size of every table and how cleanly they join.",
  """
SELECT 'orders'        AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT order_id)    AS distinct_keys FROM target.orders
UNION ALL SELECT 'customers',     COUNT(*), COUNT(DISTINCT customer_id)  FROM target.customers
UNION ALL SELECT 'order_items',   COUNT(*), COUNT(DISTINCT order_id)     FROM target.order_items
UNION ALL SELECT 'payments',      COUNT(*), COUNT(DISTINCT order_id)     FROM target.payments
UNION ALL SELECT 'order_reviews', COUNT(*), COUNT(DISTINCT order_id)     FROM target.order_reviews
UNION ALL SELECT 'products',      COUNT(*), COUNT(DISTINCT product_id)   FROM target.products
UNION ALL SELECT 'sellers',       COUNT(*), COUNT(DISTINCT seller_id)    FROM target.sellers
UNION ALL SELECT 'geolocation',   COUNT(*), COUNT(DISTINCT geolocation_zip_code_prefix) FROM target.geolocation
ORDER BY row_count DESC;
""")

q("1.5", "order_status_and_nulls", S1,
  "Order status mix and missing delivery timestamps",
  "Supporting check: which order statuses exist and how many orders lack delivery dates.",
  """
SELECT
  order_status,
  COUNT(*) AS orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders,
  SUM(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END)             AS missing_approved_at,
  SUM(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 ELSE 0 END)  AS missing_carrier_date,
  SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS missing_customer_date
FROM target.orders
GROUP BY order_status
ORDER BY orders DESC;
""")

# ---------------------------------------------------------------- Section 2 --
q("2.1", "yearly_trend", S2,
  "Is there a growing trend in orders over the years? (yearly view)",
  "Is there a growing trend in the no. of orders placed over the past years?",
  """
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
""")

q("2.2", "monthly_trend", S2,
  "Is there a growing trend in orders? (month-by-month series)",
  "Is there a growing trend in the no. of orders placed over the past years? (monthly series with MoM change and 3-month rolling average)",
  """
WITH monthly AS (
  SELECT
    FORMAT_TIMESTAMP('%Y-%m', order_purchase_timestamp) AS order_month,
    COUNT(*) AS total_orders
  FROM target.orders
  GROUP BY order_month
)
SELECT
  order_month,
  total_orders,
  total_orders - LAG(total_orders) OVER (ORDER BY order_month) AS mom_change,
  ROUND(100 * (total_orders - LAG(total_orders) OVER (ORDER BY order_month))
        / NULLIF(LAG(total_orders) OVER (ORDER BY order_month), 0), 2) AS mom_change_pct,
  ROUND(AVG(total_orders) OVER (ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0) AS rolling_3m_avg
FROM monthly
ORDER BY order_month;
""")

q("2.3", "monthly_seasonality", S2,
  "Monthly seasonality in the number of orders",
  "Can we see some kind of monthly seasonality in terms of the no. of orders being placed?",
  """
-- Calendar month on rows, year on columns, so the same month can be compared across years.
SELECT
  EXTRACT(MONTH FROM order_purchase_timestamp) AS month_no,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2016 THEN 1 ELSE 0 END) AS orders_2016,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2017 THEN 1 ELSE 0 END) AS orders_2017,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_purchase_timestamp) = 2018 THEN 1 ELSE 0 END) AS orders_2018,
  COUNT(*) AS total_orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_orders
FROM target.orders
GROUP BY month_no
ORDER BY month_no;
""")

q("2.4", "time_of_day", S2,
  "Time of day when Brazilian customers place orders",
  "During what time of the day do Brazilian customers mostly place their orders? "
  "(0-6 Dawn, 7-12 Morning, 13-18 Afternoon, 19-23 Night)",
  """
SELECT
  CASE
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 0  AND 6  THEN 'Dawn'
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 7  AND 12 THEN 'Morning'
    WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
    ELSE 'Night'
  END AS time_of_day,
  COUNT(*) AS total_orders,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders
FROM target.orders
GROUP BY time_of_day
ORDER BY total_orders DESC;
""")

# ---------------------------------------------------------------- Section 3 --
q("3.1", "mom_orders_by_state", S3,
  "Month-on-month number of orders placed in each state",
  "Get the month on month no. of orders placed in each state.",
  """
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
""")

q("3.2", "customers_by_state", S3,
  "How customers are distributed across states",
  "How are the customers distributed across all the states?",
  """
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
""")

# ---------------------------------------------------------------- Section 4 --
q("4.1", "cost_increase_2017_2018", S4,
  "% increase in cost of orders, 2017 vs 2018 (Jan-Aug)",
  "Get the % increase in the cost of orders from year 2017 to 2018 (include months between Jan to Aug only), using payment_value.",
  """
WITH yearly_cost AS (
  SELECT
    EXTRACT(YEAR FROM o.order_purchase_timestamp) AS order_year,
    SUM(p.payment_value) AS total_cost
  FROM target.orders AS o
  JOIN target.payments AS p
    ON o.order_id = p.order_id
  WHERE EXTRACT(YEAR  FROM o.order_purchase_timestamp) IN (2017, 2018)
    AND EXTRACT(MONTH FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
  GROUP BY order_year
)
SELECT
  ROUND(MAX(CASE WHEN order_year = 2017 THEN total_cost END), 2) AS cost_2017_jan_aug,
  ROUND(MAX(CASE WHEN order_year = 2018 THEN total_cost END), 2) AS cost_2018_jan_aug,
  ROUND(100 * (MAX(CASE WHEN order_year = 2018 THEN total_cost END)
             - MAX(CASE WHEN order_year = 2017 THEN total_cost END))
        / MAX(CASE WHEN order_year = 2017 THEN total_cost END), 2) AS pct_increase
FROM yearly_cost;
""")

q("4.2", "cost_by_month_2017_vs_2018", S4,
  "Cost of orders by month, 2017 vs 2018 (Jan-Aug)",
  "Supporting view for 4.1: where in the year did the growth come from?",
  """
SELECT
  EXTRACT(MONTH FROM o.order_purchase_timestamp) AS month_no,
  ROUND(SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END), 2) AS cost_2017,
  ROUND(SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2018 THEN p.payment_value END), 2) AS cost_2018,
  ROUND(100 * (SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2018 THEN p.payment_value END)
             - SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END))
        / SUM(CASE WHEN EXTRACT(YEAR FROM o.order_purchase_timestamp) = 2017 THEN p.payment_value END), 2) AS yoy_pct
FROM target.orders AS o
JOIN target.payments AS p
  ON o.order_id = p.order_id
WHERE EXTRACT(MONTH FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
GROUP BY month_no
ORDER BY month_no;
""")

q("4.3", "order_price_by_state", S4,
  "Total & average order price for each state",
  "Calculate the Total & Average value of order price for each state.",
  """
SELECT
  c.customer_state,
  ROUND(SUM(oi.price), 2) AS total_order_price,
  ROUND(AVG(oi.price), 2) AS avg_price_per_item,
  ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id), 2) AS avg_price_per_order,
  COUNT(DISTINCT oi.order_id) AS orders
FROM target.orders AS o
JOIN target.customers   AS c  ON o.customer_id = c.customer_id
JOIN target.order_items AS oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_order_price DESC;
""")

q("4.4", "order_freight_by_state", S4,
  "Total & average freight value for each state",
  "Calculate the Total & Average value of order freight for each state.",
  """
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
""")

# ---------------------------------------------------------------- Section 5 --
q("5.1", "delivery_time_per_order", S5,
  "Delivery time and estimated-vs-actual gap per order (single query)",
  "Find the no. of days taken to deliver each order from the purchase date (time_to_deliver) and the "
  "difference in days between the actual & estimated delivery date (diff_estimated_delivery), in a single query.",
  """
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
""")

q("5.2", "delivery_summary", S5,
  "Delivery performance summary (supporting 5.1)",
  "Supporting view: overall distribution of delivery time and lateness.",
  """
WITH d AS (
  SELECT
    TIMESTAMP_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY)      AS time_to_deliver,
    TIMESTAMP_DIFF(order_delivered_customer_date, order_estimated_delivery_date, DAY) AS diff_estimated_delivery
  FROM target.orders
  WHERE order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL
)
SELECT
  COUNT(*) AS delivered_orders,
  ROUND(AVG(time_to_deliver), 2) AS avg_days_to_deliver,
  MIN(time_to_deliver) AS min_days,
  MAX(time_to_deliver) AS max_days,
  ROUND(AVG(diff_estimated_delivery), 2) AS avg_days_vs_estimate,
  SUM(CASE WHEN diff_estimated_delivery > 0 THEN 1 ELSE 0 END) AS late_orders,
  ROUND(100 * SUM(CASE WHEN diff_estimated_delivery > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_late
FROM d;
""")

q("5.3", "top5_freight_states", S5,
  "Top 5 states with the highest & lowest average freight value",
  "Find out the top 5 states with the highest & lowest average freight value.",
  """
WITH state_freight AS (
  SELECT
    c.customer_state,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_value
  FROM target.orders AS o
  JOIN target.customers   AS c  ON o.customer_id = c.customer_id
  JOIN target.order_items AS oi ON o.order_id = oi.order_id
  GROUP BY c.customer_state
),
ranked AS (
  SELECT
    customer_state,
    avg_freight_value,
    ROW_NUMBER() OVER (ORDER BY avg_freight_value DESC) AS rank_high,
    ROW_NUMBER() OVER (ORDER BY avg_freight_value ASC)  AS rank_low
  FROM state_freight
)
SELECT
  h.rank_high          AS rank_no,
  h.customer_state     AS highest_freight_state,
  h.avg_freight_value  AS highest_avg_freight,
  l.customer_state     AS lowest_freight_state,
  l.avg_freight_value  AS lowest_avg_freight
FROM ranked AS h
JOIN ranked AS l
  ON h.rank_high = l.rank_low
WHERE h.rank_high <= 5
ORDER BY rank_no;
""")

q("5.4", "top5_delivery_time_states", S5,
  "Top 5 states with the highest & lowest average delivery time",
  "Find out the top 5 states with the highest & lowest average delivery time.",
  """
WITH state_delivery AS (
  SELECT
    c.customer_state,
    ROUND(AVG(TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)), 2)
      AS avg_delivery_days
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
  GROUP BY c.customer_state
),
ranked AS (
  SELECT
    customer_state,
    avg_delivery_days,
    ROW_NUMBER() OVER (ORDER BY avg_delivery_days DESC) AS rank_slow,
    ROW_NUMBER() OVER (ORDER BY avg_delivery_days ASC)  AS rank_fast
  FROM state_delivery
)
SELECT
  s.rank_slow          AS rank_no,
  s.customer_state     AS slowest_state,
  s.avg_delivery_days  AS slowest_avg_days,
  f.customer_state     AS fastest_state,
  f.avg_delivery_days  AS fastest_avg_days
FROM ranked AS s
JOIN ranked AS f
  ON s.rank_slow = f.rank_fast
WHERE s.rank_slow <= 5
ORDER BY rank_no;
""")

q("5.5", "top5_fast_vs_estimate", S5,
  "Top 5 states where delivery is fastest compared to the estimate",
  "Find out the top 5 states where the order delivery is really fast as compared to the estimated date of delivery "
  "(difference between the averages of actual & estimated delivery time).",
  """
WITH d AS (
  SELECT
    c.customer_state,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)     AS actual_days,
    TIMESTAMP_DIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp, DAY)     AS estimated_days,
    CASE WHEN TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END AS is_late
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
  customer_state,
  ROUND(AVG(actual_days), 2)    AS avg_actual_days,
  ROUND(AVG(estimated_days), 2) AS avg_estimated_days,
  ROUND(AVG(estimated_days) - AVG(actual_days), 2) AS days_faster_than_estimate,
  ROUND(100 * AVG(is_late), 2)  AS pct_late
FROM d
GROUP BY customer_state
ORDER BY days_faster_than_estimate DESC
LIMIT 5;
""")

q("5.6", "delivery_scorecard_by_state", S5,
  "State delivery scorecard (all 27 states)",
  "Supporting view: delivery speed, buffer vs estimate, lateness and freight side by side for every state.",
  """
WITH d AS (
  SELECT
    c.customer_state,
    o.order_id,
    TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) AS actual_days,
    TIMESTAMP_DIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp, DAY) AS estimated_days,
    CASE WHEN TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END AS is_late
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
),
f AS (
  SELECT c.customer_state, AVG(oi.freight_value) AS avg_freight
  FROM target.orders AS o
  JOIN target.customers   AS c  ON o.customer_id = c.customer_id
  JOIN target.order_items AS oi ON o.order_id = oi.order_id
  GROUP BY c.customer_state
)
SELECT
  d.customer_state,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(d.actual_days), 2) AS avg_actual_days,
  ROUND(AVG(d.estimated_days) - AVG(d.actual_days), 2) AS days_faster_than_estimate,
  ROUND(100 * AVG(d.is_late), 2) AS pct_late,
  ROUND(MAX(f.avg_freight), 2) AS avg_freight_per_item
FROM d
JOIN f ON d.customer_state = f.customer_state
GROUP BY d.customer_state
ORDER BY avg_actual_days DESC;
""")

# ---------------------------------------------------------------- Section 6 --
q("6.1", "mom_orders_by_payment_type", S6,
  "Month-on-month orders by payment type",
  "Find the month on month no. of orders placed using different payment types.",
  """
SELECT
  FORMAT_TIMESTAMP('%Y-%m', o.order_purchase_timestamp) AS order_month,
  p.payment_type,
  COUNT(DISTINCT o.order_id) AS total_orders
FROM target.orders AS o
JOIN target.payments AS p
  ON o.order_id = p.order_id
GROUP BY order_month, p.payment_type
ORDER BY order_month, total_orders DESC;
""")

q("6.2", "payment_type_share", S6,
  "Payment type share, value and installments (supporting 6.1)",
  "Supporting view: share of orders and value by payment type.",
  """
SELECT
  payment_type,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(100 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM target.payments), 2)
    AS pct_of_orders,
  ROUND(SUM(payment_value), 2) AS total_value,
  ROUND(AVG(payment_value), 2) AS avg_payment_value,
  ROUND(AVG(payment_installments), 2) AS avg_installments
FROM target.payments
GROUP BY payment_type
ORDER BY orders DESC;
""")

q("6.3", "orders_by_installments", S6,
  "Number of orders by payment installments",
  "Find the no. of orders placed on the basis of the payment installments that have been paid.",
  """
SELECT
  payment_installments,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(100 * COUNT(DISTINCT order_id)
        / SUM(COUNT(DISTINCT order_id)) OVER (), 2) AS pct_of_orders,
  ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM target.payments
GROUP BY payment_installments
ORDER BY payment_installments;
""")

# ---------------------------------------------------------------- Section 7 --
q("7.1", "late_delivery_vs_review_score", S7,
  "Does late delivery hurt review scores?",
  "Bonus: average review score and share of 1-star reviews by how early or late the order arrived.",
  """
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
""")

q("7.2", "same_state_vs_cross_state", S7,
  "Same-state vs cross-state fulfilment",
  "Bonus: how much faster and cheaper is an order when the seller is in the customer's state?",
  """
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
""")

q("7.3", "seller_base_by_state", S7,
  "Where are the sellers? Seller vs customer concentration",
  "Bonus: share of sellers vs share of customers by state (supply-demand gap).",
  """
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
""")

q("7.4", "top_categories", S7,
  "Top product categories by revenue",
  "Bonus: which categories drive revenue, and how satisfied are their buyers?",
  """
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
""")

q("7.5", "repeat_customers", S7,
  "How many customers come back?",
  "Bonus: distribution of customers by number of orders placed (uses customer_unique_id).",
  """
WITH per_customer AS (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS orders
  FROM target.orders AS o
  JOIN target.customers AS c ON o.customer_id = c.customer_id
  GROUP BY c.customer_unique_id
)
SELECT
  CASE WHEN orders >= 4 THEN '4+' ELSE CAST(orders AS STRING) END AS orders_per_customer,
  COUNT(*) AS customers,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers
FROM per_customer
GROUP BY orders_per_customer
ORDER BY orders_per_customer;
""")

q("7.6", "monthly_late_delivery_rate", S7,
  "Do peaks break the delivery network?",
  "Bonus: monthly share of late deliveries and average delivery time (delivered orders, Jan 2017 - Aug 2018).",
  """
SELECT
  FORMAT_TIMESTAMP('%Y-%m', order_purchase_timestamp) AS order_month,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(TIMESTAMP_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY)), 2) AS avg_delivery_days,
  ROUND(100 * AVG(CASE WHEN TIMESTAMP_DIFF(order_delivered_customer_date, order_estimated_delivery_date, DAY) > 0
                       THEN 1 ELSE 0 END), 2) AS pct_late
FROM target.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_purchase_timestamp >= '2017-01-01'
  AND order_purchase_timestamp <  '2018-09-01'
GROUP BY order_month
ORDER BY order_month;
""")
