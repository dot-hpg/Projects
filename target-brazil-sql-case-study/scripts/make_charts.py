"""Build every chart used in the README, notebook and report.
Reads the query results in outputs/results/ (run scripts/run_queries.py first)
plus two small extra aggregations for the hourly view and the delivery map.
Charts are written to charts/*.png."""
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "outputs" / "results"
OUT = ROOT / "charts"
OUT.mkdir(exist_ok=True)

# ---- palette (validated reference palette, light mode) ----------------------
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
BLUE_LIGHT, BLUE_DARK = "#9ec5f4", "#184f95"
CRITICAL = "#d03b3b"
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.titlepad": 22, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "axes.axisbelow": True,
    "legend.frameon": False, "legend.fontsize": 9,
})


def r(name):
    return pd.read_csv(next(RES.glob(f"{name}_*.csv")))


def subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK2, fontsize=9.5, va="bottom")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=170)
    plt.close(fig)
    print("chart:", name)


def fmt_thousands(ax, axis="y"):
    f = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:,.0f}k" if abs(v) >= 1000 else f"{v:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def monthly_trend():
    df = r("2_2")
    df = df[(df.order_month >= "2017-01") & (df.order_month <= "2018-08")].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = range(len(df))
    ax.plot(x, df.total_orders, color=BLUE, lw=2, marker="o", ms=4, label="Monthly orders")
    ax.plot(x, df.rolling_3m_avg, color=MUTED, lw=1.5, ls="--", label="3-month rolling avg")
    pk = df.total_orders.idxmax()
    ax.annotate(f"Nov 2017: {df.total_orders[pk]:,} orders\n(Black Friday)", (pk, df.total_orders[pk]),
                xytext=(pk - 7, df.total_orders[pk] - 300), color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    labels = [f"{MONTHS[int(m[5:]) - 1]}\n{m[:4]}" if m.endswith("-01") or i == 0 else MONTHS[int(m[5:]) - 1]
              for i, m in enumerate(df.order_month)]
    ax.set_xticks(list(x), labels, fontsize=8)
    ax.set_ylim(0, 8500)
    fmt_thousands(ax)
    ax.set_ylabel("Orders")
    ax.legend(loc="lower right")
    ax.set_title("Orders grew ~9x from Jan 2017 to a plateau of ~6.5-7k a month in 2018")
    subtitle(ax, "Monthly orders, Jan 2017 - Aug 2018 (2016 and Sep-Oct 2018 have too few orders to plot)")
    save(fig, "01_monthly_orders_trend")


def seasonality():
    df = r("2_3")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    w = 0.38
    xs = range(12)
    ax.bar([i - w / 2 - 0.01 for i in xs], df.orders_2017, w, color=BLUE, label="2017")
    m8 = df.month_no <= 8
    ax.bar([i + w / 2 + 0.01 for i in xs if i < 8], df.orders_2018[m8], w, color=ORANGE, label="2018")
    ax.set_xticks(list(xs), MONTHS)
    fmt_thousands(ax)
    ax.set_ylabel("Orders")
    ax.legend(loc="upper left", ncols=2)
    ax.text(10, 7544 + 150, "Black Friday", ha="center", color=INK2, fontsize=8.5)
    ax.set_title("2017 climbs steadily to a November peak; 2018 runs flat at a higher level")
    subtitle(ax, "Orders by calendar month and year (2018 data ends in August)")
    save(fig, "02_monthly_seasonality")


def time_of_day(con):
    hourly = con.execute("""
        SELECT EXTRACT(HOUR FROM order_purchase_timestamp) AS hr, COUNT(*) AS orders
        FROM target.orders GROUP BY hr ORDER BY hr""").df()
    bucket = {**{h: "Dawn" for h in range(0, 7)}, **{h: "Morning" for h in range(7, 13)},
              **{h: "Afternoon" for h in range(13, 19)}, **{h: "Night" for h in range(19, 24)}}
    shade = {"Dawn": BLUE_LIGHT, "Morning": "#5598e7", "Afternoon": BLUE_DARK, "Night": "#2a78d6"}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 2]})
    tod = r("2_4").set_index("time_of_day").loc[["Dawn", "Morning", "Afternoon", "Night"]]
    a1.barh(tod.index[::-1], tod.total_orders[::-1], color=[shade[k] for k in tod.index[::-1]], height=0.6)
    for i, (k, v) in enumerate(tod.total_orders[::-1].items()):
        a1.text(v + 600, i, f"{tod.pct_of_orders[k]:.1f}%", va="center", color=INK, fontsize=9)
    a1.set_xlim(0, 46000)
    fmt_thousands(a1, "x")
    a1.grid(axis="y", visible=False)
    a1.set_title("Afternoon is the busiest window")
    subtitle(a1, "Orders by time of day")
    a2.bar(hourly.hr, hourly.orders, color=[shade[bucket[h]] for h in hourly.hr], width=0.8)
    a2.set_xticks(range(0, 24, 2))
    a2.set_xlabel("Hour of purchase (local time)")
    fmt_thousands(a2)
    a2.grid(axis="x", visible=False)
    a2.set_title("Demand ramps at 10:00 and holds until 22:00")
    subtitle(a2, "Orders by hour of day; shading matches the four time-of-day buckets")
    save(fig, "03_time_of_day")


def customers_by_state():
    df = r("3_2")
    fig, ax = plt.subplots(figsize=(10, 6.4))
    top = df.customer_state.isin(["SP", "RJ", "MG"])
    ax.barh(df.customer_state[::-1], df.unique_customers[::-1],
            color=[BLUE_DARK if t else BLUE_LIGHT for t in top[::-1]], height=0.7)
    for i, (_, row) in enumerate(df[::-1].iterrows()):
        if row.pct_of_customers >= 2:
            ax.text(row.unique_customers + 400, i, f"{row.pct_of_customers:.1f}%", va="center", fontsize=8, color=INK2)
    fmt_thousands(ax, "x")
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Unique customers")
    ax.set_title("SP, RJ and MG hold two-thirds of all customers")
    subtitle(ax, "Unique customers by state (darker = top 3, 66.5% combined)")
    save(fig, "04_customers_by_state")


def state_month_heatmap():
    df = r("3_1")
    df["ym"] = df.order_year.astype(str) + "-" + df.order_month.astype(str).str.zfill(2)
    df = df[(df.ym >= "2017-01") & (df.ym <= "2018-08")]
    pv = df.pivot_table(index="customer_state", columns="ym", values="total_orders", fill_value=0)
    order = pv.sum(axis=1).sort_values(ascending=False).index
    pv = pv.loc[order]
    # share of each month's national orders, so small states stay visible
    share = pv.div(pv.sum(axis=0), axis=1) * 100
    fig, ax = plt.subplots(figsize=(11, 7.2))
    im = ax.imshow(share.values, aspect="auto", cmap=SEQ, vmin=0, vmax=12)
    ax.set_yticks(range(len(share)), share.index, fontsize=8)
    ax.set_xticks(range(share.shape[1]), [c[2:] for c in share.columns], fontsize=7.5, rotation=90)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.01)
    cb.set_label("% of that month's orders (SP capped at 12%)", color=INK2)
    cb.outline.set_visible(False)
    ax.set_title("State mix is stable month to month; SP alone is ~40% every month")
    subtitle(ax, "Each state's share of national orders per month, Jan 2017 - Aug 2018 (states sorted by volume)")
    save(fig, "05_state_month_heatmap")


def cost_growth():
    df = r("4_2")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    w = 0.38
    xs = range(8)
    ax.bar([i - w / 2 - 0.01 for i in xs], df.cost_2017 / 1e6, w, color=BLUE, label="2017")
    ax.bar([i + w / 2 + 0.01 for i in xs], df.cost_2018 / 1e6, w, color=ORANGE, label="2018")
    for i, v in enumerate(df.yoy_pct):
        ax.text(i, df.cost_2018[i] / 1e6 + 0.03, f"+{v:.0f}%", ha="center", fontsize=8.5, color=INK2)
    ax.set_xticks(list(xs), MONTHS[:8])
    ax.set_ylabel("Payment value (R$ millions)")
    ax.set_ylim(0, 1.35)
    ax.legend(loc="upper left", ncols=2)
    ax.set_title("Order value up 137% (Jan-Aug 2018 vs 2017), but growth is slowing")
    subtitle(ax, "Monthly payment value, R$ millions; labels show year-on-year growth")
    save(fig, "06_cost_growth_2017_2018")


def price_freight_by_state():
    price, freight = r("4_3"), r("4_4")
    df = price.merge(freight, on="customer_state").sort_values("freight_as_pct_of_price")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 6.6), sharey=True)
    a1.barh(df.customer_state, df.avg_price_per_order, color=BLUE, height=0.7)
    a1.set_title("Average order price (R$)")
    subtitle(a1, "Remote states buy fewer, pricier baskets")
    a2.barh(df.customer_state, df.freight_as_pct_of_price,
            color=[ORANGE if v >= 22 else "#f4b08f" for v in df.freight_as_pct_of_price], height=0.7)
    a2.set_title("Freight as % of item price")
    subtitle(a2, "Darker = freight is 22%+ of the price")
    for a in (a1, a2):
        a.grid(axis="y", visible=False)
        a.tick_params(axis="y", labelsize=8.5)
    fig.suptitle("North & Northeast customers pay the most freight relative to what they buy",
                 x=0.01, ha="left", fontweight="bold", fontsize=13)
    save(fig, "07_price_vs_freight_by_state")


def delivery_vs_estimate():
    df = r("5_6").sort_values("avg_actual_days")
    est = df.avg_actual_days + df.days_faster_than_estimate
    fig, ax = plt.subplots(figsize=(10, 7))
    y = range(len(df))
    ax.hlines(y, df.avg_actual_days, est, color=AXIS, lw=2)
    ax.scatter(df.avg_actual_days, y, color=BLUE, s=36, zorder=3, label="Actual delivery days", edgecolor=SURFACE)
    ax.scatter(est, y, color=ORANGE, s=36, zorder=3, label="Estimated delivery days", edgecolor=SURFACE)
    ax.set_yticks(list(y), df.customer_state, fontsize=8.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Days from purchase")
    ax.legend(loc="lower right")
    ax.set_title("Estimates are padded by 8-20 days everywhere, hiding a 3.5x speed gap")
    subtitle(ax, "Average actual vs promised delivery time by customer state (delivered orders)")
    save(fig, "08_delivery_actual_vs_estimate")


def freight_vs_delivery_scatter():
    df = r("5_6")
    fig, ax = plt.subplots(figsize=(10, 6))
    sizes = df.delivered_orders / df.delivered_orders.max() * 1400 + 25
    ax.scatter(df.avg_actual_days, df.avg_freight_per_item, s=sizes, color=BLUE, alpha=0.55,
               edgecolor=SURFACE, linewidth=1.5)
    for _, row in df.iterrows():
        dx, dy = {"PR": (-0.6, -1.6), "MG": (0.6, 0.9), "RJ": (0, -1.8), "RS": (0, 0.9),
                  "SC": (-0.5, 0.9), "GO": (0, 0.9), "MS": (0, 1.8), "ES": (0.5, 0.2)}.get(row.customer_state, (0, 0.9))
        ax.text(row.avg_actual_days + dx, row.avg_freight_per_item + dy, row.customer_state,
                ha="center", fontsize=8, color=INK)
    ax.set_xlabel("Average delivery time (days)")
    ax.set_ylabel("Average freight per item (R$)")
    ax.set_title("The slowest states also pay the highest freight")
    subtitle(ax, "Each bubble is a state; bubble size = delivered orders")
    save(fig, "09_freight_vs_delivery_by_state")


def review_vs_delay():
    df = r("7_1")
    labels = [b[3:] for b in df.delivery_bucket]
    colors = [BLUE] * 3 + [CRITICAL] * 3
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
    a1.bar(labels, df.avg_review_score, color=colors, width=0.62)
    for i, v in enumerate(df.avg_review_score):
        a1.text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=9)
    a1.set_ylim(0, 5)
    a1.set_title("Average review score")
    subtitle(a1, "Blue = on time/early, red = late")
    a2.bar(labels, df.pct_1_star, color=colors, width=0.62)
    for i, v in enumerate(df.pct_1_star):
        a2.text(i, v + 1.2, f"{v:.0f}%", ha="center", fontsize=9)
    a2.set_ylim(0, 80)
    a2.set_title("Share of 1-star reviews")
    subtitle(a2, "% of orders in each bucket")
    for a in (a1, a2):
        a.tick_params(axis="x", labelsize=8, rotation=25)
        a.grid(axis="x", visible=False)
    fig.suptitle("A late delivery drops the review score from 4.3 to as low as 1.7",
                 x=0.01, ha="left", fontweight="bold", fontsize=13)
    save(fig, "10_review_score_vs_delivery_delay")


def payments_trend():
    df = r("6_1")
    df = df[(df.order_month >= "2017-01") & (df.order_month <= "2018-08")]
    pv = df.pivot_table(index="order_month", columns="payment_type", values="total_orders", fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = range(len(pv))
    series = [("credit_card", BLUE, "Credit card"), ("UPI", ORANGE, "UPI"),
              ("voucher", AQUA, "Voucher"), ("debit_card", YELLOW, "Debit card")]
    nudge = {"voucher": -180, "debit_card": 180}
    for col, c, lab in series:
        ax.plot(x, pv[col], color=c, lw=2, label=lab)
        ax.text(len(pv) - 0.6, pv[col].iloc[-1] + nudge.get(col, 0), lab, color=INK2, fontsize=8.5, va="center")
    ax.set_xticks(list(x), [m[2:] for m in pv.index], fontsize=8, rotation=90)
    ax.set_xlim(-0.5, len(pv) + 2)
    fmt_thousands(ax)
    ax.set_ylabel("Orders")
    ax.legend(loc="upper left")
    ax.set_title("Credit card carries ~3 of every 4 orders, and the gap keeps widening")
    subtitle(ax, "Monthly orders by payment type, Jan 2017 - Aug 2018 (an order can use more than one type)")
    save(fig, "11_payment_type_trend")


def installments():
    df = r("6_3")
    df = df[df.payment_installments.between(1, 12)]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.bar(df.payment_installments, df.total_orders, color=BLUE, width=0.62)
    ax.set_xticks(range(1, 13))
    for _, row in df.iterrows():
        if row.pct_of_orders >= 1:
            ax.text(int(row.payment_installments), row.total_orders + 600, f"{row.pct_of_orders:.0f}%",
                    ha="center", fontsize=8.5, color=INK2)
    fmt_thousands(ax)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Number of installments")
    ax.set_ylabel("Orders")
    ax.set_title("Half of orders are paid in one go; 10x is the go-to for big baskets")
    subtitle(ax, "Orders by number of payment installments (1-12 shown; 13-24 add 0.2%)")
    save(fig, "12_installments")


def same_vs_cross_state():
    df = r("7_2").set_index("route").loc[["Same state", "Cross state"]]
    metrics = [("avg_delivery_days", "Avg delivery days"), ("avg_freight", "Avg freight (R$)"),
               ("pct_late", "% delivered late")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    for a, (col, title) in zip(axes, metrics):
        a.bar(df.index, df[col], color=[AQUA, ORANGE], width=0.55)
        for i, v in enumerate(df[col]):
            a.text(i, v * 1.03, f"{v:.1f}", ha="center", fontsize=9.5)
        a.set_title(title, fontsize=11, pad=8)
        a.set_ylim(0, df[col].max() * 1.22)
        a.grid(axis="x", visible=False)
    fig.suptitle("Shipping within the same state halves delivery time and cuts freight by 43%",
                 x=0.01, ha="left", fontweight="bold", fontsize=13)
    save(fig, "13_same_vs_cross_state")


def delivery_map(con):
    """Uses the geolocation table: zip-prefix centroids, coloured by average delivery days."""
    df = con.execute("""
        WITH geo AS (
          SELECT geolocation_zip_code_prefix AS zip, AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng
          FROM target.geolocation
          WHERE geolocation_lat BETWEEN -34 AND 5.5 AND geolocation_lng BETWEEN -74 AND -34
          GROUP BY 1)
        SELECT g.lat, g.lng, COUNT(*) AS orders,
               AVG(DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_customer_date) / 86400.0) AS days
        FROM target.orders o
        JOIN target.customers c ON o.customer_id = c.customer_id
        JOIN geo g ON c.customer_zip_code_prefix = g.zip
        WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY 1, 2""").df()
    fig, ax = plt.subplots(figsize=(8, 8))
    df = df.sort_values("days", ascending=False)  # fast zips drawn on top
    sc = ax.scatter(df.lng, df.lat, c=df.days.clip(upper=30), cmap=SEQ, vmin=4, vmax=30,
                    s=6, alpha=0.85, linewidths=0)
    ax.set_aspect("equal")
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    cb = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.01)
    cb.set_label("Average delivery days (capped at 30)", color=INK2)
    cb.outline.set_visible(False)
    for name, lng, lat in [("São Paulo", -46.6, -23.5), ("Rio de Janeiro", -42.0, -21.6),
                           ("Manaus", -60.0, -3.1), ("Fortaleza", -38.5, -3.7), ("Porto Alegre", -51.2, -30.0)]:
        ax.annotate(name, (lng, lat), xytext=(6, 4), textcoords="offset points", fontsize=8.5, color=INK)
    ax.set_title("Delivery time grows with distance from the São Paulo hub")
    subtitle(ax, "Each dot is a customer zip-code prefix (geolocation table), coloured by average delivery days")
    save(fig, "14_delivery_time_map")


def main():
    con = duckdb.connect(str(ROOT / "target_brazil.duckdb"), read_only=True)
    monthly_trend(); seasonality(); time_of_day(con); customers_by_state(); state_month_heatmap()
    cost_growth(); price_freight_by_state(); delivery_vs_estimate(); freight_vs_delivery_scatter()
    review_vs_delay(); payments_trend(); installments(); same_vs_cross_state(); delivery_map(con)
    late_rate_trend()




def late_rate_trend():
    df = r("7_6")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    x = range(len(df))
    ax.plot(x, df.pct_late, color=CRITICAL, lw=2, marker="o", ms=4)
    for i in (df.index[df.order_month == "2017-11"][0], df.pct_late.idxmax()):
        ax.annotate(f"{df.order_month[i]}: {df.pct_late[i]:.1f}% late", (i, df.pct_late[i]),
                    xytext=(-60, 8), textcoords="offset points", fontsize=9, color=INK)
    ax.set_xticks(list(x), [m[2:] for m in df.order_month], fontsize=8, rotation=90)
    ax.set_ylabel("% of delivered orders that were late")
    ax.set_ylim(0, 22)
    ax.set_title("Late deliveries spike after demand peaks (Black Friday, Feb-Mar 2018)")
    subtitle(ax, "Share of delivered orders arriving at least one day after the estimated date, by purchase month")
    save(fig, "15_late_delivery_rate_trend")


if __name__ == "__main__":
    main()
