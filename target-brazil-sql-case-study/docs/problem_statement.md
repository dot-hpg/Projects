# Problem statement: Business Case "Target SQL" (Scaler)

**Context.** Target is a globally renowned brand and a prominent retailer in the United States. This business case focuses on Target's operations in Brazil and covers 100,000 orders placed between 2016 and 2018, with order status, price, payment and freight performance, customer location, product attributes and customer reviews.

**Task.** As a data analyst/scientist at Target, analyse the dataset to extract valuable insights and provide actionable recommendations.

## Questions

1. **Initial exploration** (15 pts)
   1. Data type of all columns in the `customers` table.
   2. Time range between which the orders were placed.
   3. Count the cities & states of customers who ordered during the given period.
2. **In-depth exploration** (15 pts)
   1. Is there a growing trend in the number of orders placed over the past years?
   2. Is there monthly seasonality in the number of orders?
   3. At what time of day do Brazilian customers mostly order? (0-6 Dawn, 7-12 Morning, 13-18 Afternoon, 19-23 Night)
3. **Evolution of e-commerce orders in the Brazil region** (10 pts)
   1. Month-on-month number of orders placed in each state.
   2. How are customers distributed across the states?
4. **Impact on economy** (20 pts)
   1. % increase in the cost of orders from 2017 to 2018 (Jan-Aug only), using `payment_value`.
   2. Total & average order price for each state.
   3. Total & average order freight for each state.
5. **Sales, freight and delivery time** (20 pts)
   1. Days taken to deliver each order (`time_to_deliver = order_delivered_customer_date - order_purchase_timestamp`) and the difference between estimated and actual delivery (`diff_estimated_delivery = order_delivered_customer_date - order_estimated_delivery_date`), in a single query.
   2. Top 5 states with the highest & lowest average freight value.
   3. Top 5 states with the highest & lowest average delivery time.
   4. Top 5 states where delivery is really fast compared to the estimated date.
6. **Payments** (10 pts)
   1. Month-on-month number of orders by payment type.
   2. Number of orders by number of payment installments.
7. **Actionable insights & recommendations** (10 pts)

**Submission.** A Word document with each SQL query and a screenshot of the first 10 rows of output, plus insights and recommendations, converted to a PDF of at most 50 pages.
