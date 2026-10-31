"""Written analysis for every query: insights, recommendations and the chart that
goes with it. Every number here comes from outputs/results/*.csv."""

TITLE = "Target Brazil: E-commerce Operations SQL Case Study"
AUTHOR = "Guntuku Hariprasad"

HEADLINE_KPIS = [
    ("99,441", "orders, Sep 2016 - Oct 2018"),
    ("96,096", "unique customers in 4,119 cities, 27 states"),
    ("+137%", "order value, Jan-Aug 2018 vs 2017"),
    ("12.1 days", "average delivery; 6.8% arrive late"),
    ("4.32 → 1.70", "review score, early vs 8+ days late"),
]

EXEC_SUMMARY = [
    "Growth is real and volume-driven. Orders in Jan-Aug 2018 were 135% higher than in Jan-Aug 2017 and "
    "payment value rose 137%, while the average order value barely moved (R$159.7 to R$161.0). Target "
    "Brazil won more customers; it did not sell them bigger baskets.",
    "Growth has plateaued. Monthly orders climbed from 800 (Jan 2017) to a Black Friday peak of 7,544 "
    "(Nov 2017; 1,176 orders on Black Friday, 24 Nov, alone) and then held at roughly 6,200-7,300 a month through 2018. "
    "Year-on-year value growth fell from +705% in January to +52% in August.",
    "Demand is concentrated in the South-East. SP, RJ and MG hold 66.5% of customers and SP alone 41.9%. "
    "59.7% of sellers are also in SP, so the network is effectively a single hub.",
    "Distance from the hub drives cost, speed and satisfaction. SP customers get orders in 8.3 days and pay "
    "R$15.15 freight per item; Roraima (RR) waits 29.0 days and pays R$42.98. Same-state orders arrive in "
    "7.5 days vs 14.6 cross-state, with 43% lower freight.",
    "Lateness, not slowness, destroys ratings. Orders delivered early average 4.2-4.3 stars; orders 8+ days "
    "late average 1.70 and 70% of them get 1 star. Late rates spike after demand peaks (12.4% in Nov 2017, "
    "19.0% in Mar 2018), so the problem is capacity, not geography alone.",
    "Credit card is the payment backbone (76.9% of orders, average 3.5 installments). Half of all orders are "
    "single-payment, but 10-installment plans carry the biggest tickets (R$415 average).",
    "Retention is the biggest untapped lever: 96.9% of customers ordered only once.",
]

# id -> dict(insights=[...], recs=[...], chart=optional filename)
ANALYSIS = {
    "1.1": dict(
        insights=[
            "The customers table has 5 columns. The two IDs, city and state are STRING; the zip code prefix is "
            "INT64 (stored as BIGINT locally).",
            "customer_id is unique per order, while customer_unique_id identifies the real person: 99,441 "
            "customer_ids map to 96,096 unique customers. Any customer count in this study uses "
            "customer_unique_id.",
            "Zip prefixes lose their leading zero as integers (01037 becomes 1037). They still join to "
            "geolocation correctly because both sides are integers.",
        ],
        recs=["Keep zip prefixes as zero-padded STRING in the warehouse so they match postal formats when "
              "shared with logistics partners."]),
    "1.2": dict(
        insights=[
            "Orders span 4 Sep 2016 21:15 to 17 Oct 2018 17:30, about 772 days (25 calendar months).",
            "The edges are thin: Sep-Dec 2016 has 329 orders (no orders at all in Nov 2016) and Sep-Oct 2018 "
            "has 20. Year-on-year comparisons should therefore use Jan-Aug, which the brief also asks for.",
        ],
        recs=["Report trends on complete months (Jan 2017 - Aug 2018) so the partial edges do not distort growth "
              "rates."]),
    "1.3": dict(
        insights=[
            "Customers who ordered in the period come from 4,119 cities across all 27 Brazilian states "
            "(26 states + the Federal District).",
            "Those 99,441 orders were placed by 96,096 unique customers, i.e. 1.03 orders per customer.",
        ],
        recs=["National reach already exists; the opportunity is deepening penetration outside the South-East, "
              "not opening new states."]),
    "1.4": dict(
        insights=[
            "Orders, customers and payments join almost 1:1 (99,441 orders, 99,440 with a payment). 775 orders "
            "have no items, mostly cancelled/unavailable ones.",
            "Geolocation has 1,000,163 rows for only 19,015 zip prefixes: many coordinates per prefix, so it must "
            "be aggregated to one row per prefix before joining.",
            "Reviews hold 99,224 rows for 98,673 orders, so a few orders have more than one review; review scores "
            "are averaged per order before joining.",
        ],
        recs=["Publish a deduplicated geolocation view (one centroid per zip prefix) so analysts do not "
              "accidentally multiply rows."]),
    "1.5": dict(
        insights=[
            "97.0% of orders were delivered; 1.1% shipped but not delivered, 0.6% cancelled and 0.6% unavailable.",
            "Only 8 delivered orders lack a delivery date, so delivery metrics cover 96,470 orders.",
        ],
        recs=["Investigate the 609 'unavailable' orders: each one is a sale lost to stock-outs and a likely "
              "unhappy customer."]),
    "2.1": dict(
        insights=[
            "Yes, there is a strong growth trend. Like-for-like (Jan-Aug), orders grew from 22,968 in 2017 to "
            "53,991 in 2018: +135%.",
            "Average orders per active month rose from 3,758 in 2017 to 5,401 in 2018 (+44%), even though 2018 "
            "lacks the Nov-Dec holiday season.",
        ],
        recs=["Use the 2018 run-rate (~6,700 orders a month) as the planning baseline for capacity and "
              "inventory, not the 2017 average."],
        chart="01_monthly_orders_trend.png"),
    "2.2": dict(
        insights=[
            "Orders rose almost every month in 2017, from 800 in January to 4,631 in October.",
            "November 2017 jumped 62.9% month-on-month to 7,544 orders, the all-time peak; 24 Nov 2017 (Black "
            "Friday) alone had 1,176 orders, over 5x the average day that month.",
            "From January 2018 volume plateaued between 6,167 and 7,269 a month: the growth phase is over and "
            "the business is now in a scale phase.",
        ],
        recs=["Re-ignite growth with acquisition campaigns in under-penetrated states, because organic "
              "momentum has flattened since Jan 2018.",
              "Treat Black Friday as the single largest operational event: pre-book carrier capacity and "
              "staff from October."]),
    "2.3": dict(
        insights=[
            "Seasonality exists but is masked by growth. In 2017 orders rose steadily to a November peak (Black "
            "Friday) and eased in December.",
            "In 2018, Jan-Mar were the strongest months (7,269, 6,728, 7,211) and Jun-Jul the weakest "
            "(6,167, 6,292): post-holiday and new-year demand are strong, mid-year is soft.",
            "May, July and August have the highest share of all orders (10.6-10.9%) because they are covered "
            "by two full years of data.",
        ],
        recs=["Run mid-year (June-July) promotions to fill the seasonal dip.",
              "Build inventory ahead of November and Q1, the two demand peaks."],
        chart="02_monthly_seasonality.png"),
    "2.4": dict(
        insights=[
            "Brazilian customers order mostly in the Afternoon (38.4%), then Night (28.5%) and Morning (27.9%). "
            "Dawn is quiet (5.3%).",
            "By hour, demand ramps from 10:00 and stays high until 22:00; the busiest hour is 16:00 "
            "(6,675 orders).",
        ],
        recs=["Schedule flash sales, push notifications and paid-media bids for 13:00-22:00.",
              "Use 0:00-6:00 for site deployments and maintenance, when only 5% of orders arrive."],
        chart="03_time_of_day.png"),
    "3.1": dict(
        insights=[
            "Every state grew between Jan-Aug 2017 and Jan-Aug 2018 except Acre (AC, 33 to 27 orders).",
            "The fastest growers were DF (+184%), MS (+172%) and SP (+166%). The North and North-East grew "
            "slowest: SE (+43%), RO (+35%), AM (+55%), PA (+66%).",
            "Each state's share of monthly orders is very stable: SP is ~40% every month.",
        ],
        recs=["Investigate why the North and North-East lag the national growth rate; delivery time and freight "
              "(sections 4-5) are the likely blockers."],
        chart="05_state_month_heatmap.png"),
    "3.2": dict(
        insights=[
            "Customers are highly concentrated: SP has 41.9%, RJ 12.9%, MG 11.7%. The top 5 states (SP, RJ, MG, "
            "RS, PR) hold 77.1% of all customers.",
            "The bottom 5 (RO, AM, AC, AP, RR) together hold only 0.6%. Roraima has just 45 customers.",
            "SP also covers the most cities in absolute terms after MG (629 vs 745).",
        ],
        recs=["Defend the core (SP, RJ, MG) with loyalty programmes; grow the long tail with regional marketing "
              "and cheaper shipping, because each new customer there has low competition."],
        chart="04_customers_by_state.png"),
    "4.1": dict(
        insights=[
            "The cost of orders (payment_value) grew from R$3.67M in Jan-Aug 2017 to R$8.69M in Jan-Aug 2018, an "
            "increase of 136.98%.",
            "Average order value was flat (R$159.7 vs R$161.0), so the increase comes from more orders, not "
            "higher prices.",
        ],
        recs=["Add basket-building levers (bundles, free-shipping thresholds, cross-sell) to grow order value "
              "now that volume growth has slowed."]),
    "4.2": dict(
        insights=[
            "Year-on-year growth decays month by month: +705% in January, +178% in April, +52% in August.",
            "2018 monthly value is flat at R$1.0-1.16M, confirming the plateau seen in order counts.",
        ],
        recs=["Set 2019 targets on a plateau-aware baseline; extrapolating early-2018 growth rates would "
              "overstate demand by a wide margin."],
        chart="06_cost_growth_2017_2018.png"),
    "4.3": dict(
        insights=[
            "SP generates the most revenue by far (R$5.20M, 38% of item value), followed by RJ (R$1.82M) and "
            "MG (R$1.59M).",
            "SP also has the lowest average order price (R$125.75 per order). Remote states buy fewer but pricier "
            "baskets: PB R$216.67, AP R$198.15, AC R$197.32 per order.",
        ],
        recs=["In remote states, customers only buy when the item is valuable enough to justify the shipping. "
              "Lower freight would unlock everyday, lower-priced purchases there."],
        chart="07_price_vs_freight_by_state.png"),
    "4.4": dict(
        insights=[
            "Total freight is largest in SP (R$718.7K) because of volume, but SP's average freight per item is the "
            "lowest (R$15.15).",
            "Freight is a much heavier burden in the North and North-East: 28.6% of the item price in RR, 26.4% "
            "in MA and 24.7% in RO, vs 13.8% in SP.",
        ],
        recs=["Introduce regional freight subsidies or free-shipping thresholds for states where freight exceeds "
              "20% of the price."]),
    "5.1": dict(
        insights=[
            "The query returns one row per delivered order (96,470 rows) with time_to_deliver and "
            "diff_estimated_delivery, computed exactly as the brief's formulas.",
            "A negative diff_estimated_delivery means the order arrived before the estimate; the first rows show "
            "typical values of -22 to -39 days in late 2016.",
        ],
        recs=["Store both metrics in a delivery fact table so operations can track them daily."]),
    "5.2": dict(
        insights=[
            "Average delivery time is 12.09 days (0 to 209 days).",
            "On average orders arrive 10.96 days before the estimate, yet 6,534 orders (6.77%) still arrive at "
            "least one day late.",
            "SP (1,820) and RJ (1,495) account for 50.7% of late orders.",
        ],
        recs=["Estimates are padded by ~11 days. Tightening them would make the site more competitive at checkout "
              "without changing logistics."]),
    "5.3": dict(
        insights=[
            "Highest average freight: RR (R$42.98), PB (R$42.72), RO (R$41.07), AC (R$40.07), PI (R$39.15), all "
            "North/North-East states far from the SP hub.",
            "Lowest: SP (R$15.15), PR (R$20.53), MG (R$20.63), RJ (R$20.96), DF (R$21.04), the states with the "
            "most orders and sellers.",
            "Freight in RR is 2.8x that in SP.",
        ],
        recs=["Negotiate consolidated (bulk) shipping contracts for the North and North-East, and open a "
              "regional cross-dock to shorten the line-haul."],
        chart="09_freight_vs_delivery_by_state.png"),
    "5.4": dict(
        insights=[
            "Slowest deliveries: RR (29.0 days), AP (26.7), AM (26.0), AL (24.0), PA (23.3).",
            "Fastest: SP (8.3 days), PR (11.5), MG (11.5), DF (12.5), SC (14.5).",
            "A customer in Roraima waits 3.5x longer than one in São Paulo.",
        ],
        recs=["Recruit sellers or place inventory in the North and North-East; same-state orders arrive in half "
              "the time (see 7.2)."],
        chart="08_delivery_actual_vs_estimate.png"),
    "5.5": dict(
        insights=[
            "Deliveries beat the estimate by the widest margin in AC (20.1 days early), RO (19.5), AP (19.1), "
            "AM (18.9) and RR (16.7).",
            "These are the slowest states. They look 'fast' only because their estimates are padded to 38-46 "
            "days.",
            "By contrast, AL (23.9% late) and MA (19.7% late) have the least reliable estimates.",
        ],
        recs=["Recalibrate estimates per state. Over-promising by 20 days loses sales at checkout; "
              "under-promising in AL and MA damages reviews."]),
    "5.6": dict(
        insights=[
            "Delivery time, freight and lateness move together: the North and North-East are slow, expensive and "
            "(in AL, MA, CE, SE, PI) often late.",
            "Among large states, RJ stands out with 13.5% late deliveries despite average speed, 2.3x SP's rate.",
        ],
        recs=["Make RJ the first fix: it is the second-biggest market and has a lateness problem, not a "
              "distance problem."],
        chart="14_delivery_time_map.png"),
    "6.1": dict(
        insights=[
            "Credit card is the dominant method every month and grew fastest, from 582 orders (Jan 2017) to "
            "~5,000 a month in 2018.",
            "UPI is a steady second at ~1,100-1,500 orders a month. Voucher and debit card are small; debit card "
            "picked up in mid-2018.",
            "All methods peak together in November 2017.",
        ],
        recs=["Partner with card issuers for interest-free installment campaigns around Black Friday, when card "
              "volume peaks."],
        chart="11_payment_type_trend.png"),
    "6.2": dict(
        insights=[
            "Credit card is used in 76.9% of orders and carries R$12.5M of value (average R$163, 3.5 "
            "installments).",
            "UPI covers 19.9% of orders; vouchers 3.9% with the smallest average ticket (R$65.7).",
        ],
        recs=["Offer a small UPI discount to shift volume from card (lower fees) on low-value baskets."]),
    "6.3": dict(
        insights=[
            "48.9% of orders are paid in a single installment, 12.4% in 2 and 10.4% in 3.",
            "The average payment rises with installments: R$112 for 1, R$308 for 8, R$415 for 10. Installments "
            "are what make expensive items affordable.",
            "10 installments (5.3% of orders) is a clear spike, the usual 'interest-free 10x' offer in Brazil.",
        ],
        recs=["Promote interest-free installments on high-ticket categories (watches, electronics, furniture) "
              "to grow basket size."],
        chart="12_installments.png"),
    "7.1": dict(
        insights=[
            "Customers barely reward early delivery (4.32 stars at 15+ days early vs 4.20 at 0-7 days early), but "
            "they punish lateness hard: 3.29 at 1-3 days late, 2.11 at 4-7, 1.70 at 8+.",
            "70% of orders delivered 8+ days late receive a 1-star review, vs 6-7% of on-time orders.",
        ],
        recs=["Optimise for reliability (on-time %) rather than raw speed; it is the strongest single driver "
              "of ratings in the data.",
              "Proactively notify and compensate customers (voucher) when an order is predicted to be late."],
        chart="10_review_score_vs_delivery_delay.png"),
    "7.2": dict(
        insights=[
            "36.2% of items ship from a seller in the customer's own state.",
            "Those items arrive in 7.5 days vs 14.6 cross-state, pay R$13.45 vs R$23.63 freight (-43%), and are "
            "late 4.5% vs 7.8% of the time.",
        ],
        recs=["Raising the same-state share is the single biggest logistics lever: recruit local sellers and "
              "prioritise local stock in search ranking."],
        chart="13_same_vs_cross_state.png"),
    "7.3": dict(
        insights=[
            "59.7% of sellers are in SP, which has 41.9% of customers.",
            "BA (172 customers per seller), PE (179) and RJ (72) are badly under-supplied, compared with 22 in SP.",
        ],
        recs=["Run seller-acquisition drives in BA, PE, CE and RJ to localise supply for large, under-served "
              "markets."]),
    "7.4": dict(
        insights=[
            "Health & beauty (9.3% of revenue), watches & gifts (8.9%) and bed/table/bath (7.6%) lead revenue.",
            "Bed/table/bath, furniture/decor and computer accessories have the lowest ratings in the top 15 "
            "(3.90-3.93), pointing to quality or expectation gaps.",
        ],
        recs=["Audit sellers and listings in low-rated, high-revenue categories (photos, size guides, "
              "packaging)."]),
    "7.5": dict(
        insights=[
            "96.9% of customers ordered only once; 2.9% ordered twice and just 0.26% three or more times.",
        ],
        recs=["Launch a retention programme (post-delivery coupons, loyalty points, personalised "
              "recommendations). Even a few points of repeat rate is worth thousands of orders."]),
    "7.6": dict(
        insights=[
            "Late deliveries are usually 3-5% of orders but jump after demand peaks: 12.4% in Nov 2017 and 14.1% / "
            "19.0% in Feb / Mar 2018.",
            "Average delivery time improved to 7.7 days by Aug 2018, so the network can perform when it is not "
            "overloaded.",
        ],
        recs=["Plan peak capacity (carriers, warehouse staff) 4-6 weeks ahead of Black Friday and the "
              "post-holiday surge, and widen estimates temporarily during peaks."],
        chart="15_late_delivery_rate_trend.png"),
}

RECOMMENDATIONS = [
    ("Fix reliability before speed",
     "A late order loses 0.9-2.6 review stars; an early one gains almost nothing. Track on-time % as the "
     "headline logistics KPI, predict late orders and notify/compensate proactively. Start with RJ (13.5% late, "
     "second-largest market)."),
    ("Recalibrate delivery estimates per state",
     "Estimates are padded by 11 days on average and by up to 20 days in the North. Showing realistic dates "
     "at checkout improves conversion; adding buffer in AL and MA (20-24% late) protects reviews."),
    ("Localise supply: regional sellers and a North/North-East cross-dock",
     "Same-state items arrive 2x faster with 43% lower freight. 60% of sellers sit in SP while BA, PE and RJ have "
     "70-180 customers per seller. Recruit sellers there and pilot a cross-dock in the North-East."),
    ("Make freight affordable in remote states",
     "Freight is 22-29% of the item price in the North/North-East vs 14% in SP. Bulk carrier contracts, "
     "subsidised shipping and free-shipping thresholds would unlock everyday purchases in markets that grew "
     "slowest."),
    ("Plan peak capacity ahead of Black Friday and Q1",
     "Black Friday 2017 brought 5x a normal day's orders; late deliveries jumped to 12.4% that month and to 14-19% after the Q1 2018 surge. Pre-book "
     "carrier capacity and staff from October and temporarily widen estimates during peaks."),
    ("Grow basket size with installments and bundles",
     "Average order value has been flat at ~R$160 for two years. 10x interest-free plans already carry R$415 "
     "tickets; promote them on high-ticket categories and add bundles and free-shipping thresholds."),
    ("Build retention",
     "97% of customers buy once. A loyalty programme, post-delivery coupons and personalised recommendations "
     "target the cheapest growth available, especially now that acquisition-led growth has plateaued."),
    ("Time marketing to the afternoon and evening",
     "38% of orders arrive 13:00-18:00 and 28% at night. Concentrate flash sales, push and paid-media budget "
     "in 13:00-22:00, and run maintenance at dawn."),
]

ASSUMPTIONS = [
    "SQL is written for BigQuery (dataset `target`) and mirrored for DuckDB; both produce identical results.",
    "Delivery metrics use orders with status 'delivered' and a non-null delivery date (96,470 orders).",
    "Days are whole 24-hour periods (BigQuery TIMESTAMP_DIFF ... DAY). An order is late when "
    "diff_estimated_delivery > 0, i.e. it arrived at least one day after the estimated date.",
    "'Average freight value' and 'average delivery time' by state are averaged per item and per order "
    "respectively; per-order price and freight are also reported in 4.3-4.4.",
    "Customer counts use customer_unique_id (one person), not customer_id (one per order).",
    "Payment type 'UPI' is the label used in this version of the dataset.",
]
