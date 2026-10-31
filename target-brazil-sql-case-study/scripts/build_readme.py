"""Write README.md (question index is generated from the query catalog)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from query_catalog import Q  # noqa: E402
from insights import RECOMMENDATIONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPORT = "report/Target_SQL_Case_Study_Guntuku_Hariprasad"

rows = []
for q in Q:
    stem = f"{q['id'].replace('.', '_')}_{q['slug']}"
    rows.append(f"| {q['id']} | {q['title']} | [BigQuery](sql/bigquery/{stem}.sql) · [DuckDB](sql/duckdb/{stem}.sql) "
                f"| [CSV](outputs/results/{stem}.csv) · [Top 10](outputs/screenshots/{stem}.png) |")
index = "\n".join(rows)
recs = "\n".join(f"{i}. **{h}.** {b}" for i, (h, b) in enumerate(RECOMMENDATIONS, 1))

README = f"""# Target Brazil: E-commerce Operations SQL Case Study

![SQL](https://img.shields.io/badge/SQL-BigQuery%20%7C%20DuckDB-1c5cab)
![Python](https://img.shields.io/badge/Python-pandas%20%7C%20matplotlib-2a78d6)
![Orders](https://img.shields.io/badge/orders-99%2C441-eb6834)
![Queries](https://img.shields.io/badge/queries-{len(Q)}-1baf7a)

An end-to-end SQL analysis of **99,441 orders** placed with Target in Brazil between September 2016 and
October 2018, built for the Scaler *Target SQL* business case. It answers every question in the brief with a
BigQuery query, goes further with six deep-dives (reviews vs. lateness, local vs. cross-state fulfilment,
seller coverage, categories, retention, peak-season lateness), and ends with eight ranked, evidence-backed
recommendations.

**[Read the report (PDF)]({REPORT}.pdf)** · [Word version]({REPORT}.docx) ·
[Notebook](notebooks/Target_Brazil_SQL_Case_Study.ipynb) ·
[Notebook as HTML](notebooks/Target_Brazil_SQL_Case_Study.html) · [All queries](sql/bigquery/00_all_queries.sql) ·
[Problem statement](docs/problem_statement.md)

---

## Key findings

| | |
|---|---|
| **+137%** | Order value, Jan-Aug 2018 vs Jan-Aug 2017 (R$3.67M → R$8.69M). Orders grew 135%, average order value stayed flat at ~R$160: growth is entirely volume. |
| **Plateau** | Orders rose from 800 (Jan 2017) to a Black Friday peak of 7,544 (Nov 2017), then held at ~6.2-7.3k a month through 2018. |
| **66.5%** | Share of customers in just three states (SP, RJ, MG). 59.7% of sellers are in SP. |
| **3.5x** | Delivery gap between São Paulo (8.3 days) and Roraima (29.0 days). Freight is 2.8x higher in RR (R$42.98 vs R$15.15). |
| **4.32 → 1.70** | Average review score for orders delivered 15+ days early vs 8+ days late; 70% of very late orders get 1 star. |
| **2x faster** | Same-state orders arrive in 7.5 days vs 14.6 cross-state, with 43% lower freight. |
| **96.9%** | Customers who ordered only once. |

![Monthly orders](charts/01_monthly_orders_trend.png)

<table>
<tr>
<td><img src="charts/10_review_score_vs_delivery_delay.png" alt="Review score vs delivery delay"></td>
<td><img src="charts/08_delivery_actual_vs_estimate.png" alt="Actual vs estimated delivery"></td>
</tr>
<tr>
<td><img src="charts/14_delivery_time_map.png" alt="Delivery time map"></td>
<td><img src="charts/13_same_vs_cross_state.png" alt="Same vs cross state"><br><img src="charts/15_late_delivery_rate_trend.png" alt="Late rate trend"></td>
</tr>
</table>

## Recommendations

{recs}

## Questions answered

Every query is written in **BigQuery Standard SQL** (dataset `target`) and auto-translated to **DuckDB** so
it runs locally. Full results are saved as CSV; the "Top 10" link is the result screenshot used in the report.

| # | Question | SQL | Output |
|---|---|---|---|
{index}

## Charts

| | | |
|---|---|---|
| ![](charts/02_monthly_seasonality.png) | ![](charts/03_time_of_day.png) | ![](charts/04_customers_by_state.png) |
| ![](charts/05_state_month_heatmap.png) | ![](charts/06_cost_growth_2017_2018.png) | ![](charts/07_price_vs_freight_by_state.png) |
| ![](charts/09_freight_vs_delivery_by_state.png) | ![](charts/11_payment_type_trend.png) | ![](charts/12_installments.png) |

## Repository structure

```
.
├── data/                  8 raw CSVs, schema image, data dictionary
├── sql/
│   ├── bigquery/          one .sql file per question + 00_all_queries.sql (BigQuery dialect)
│   └── duckdb/            the same queries translated for DuckDB
├── notebooks/             executed Jupyter notebook (+ HTML export)
├── report/                submission document: Word (.docx) and PDF ({len(Q)} queries, < 50 pages)
├── charts/                15 charts (PNG)
├── outputs/
│   ├── results/           full result of every query (CSV)
│   └── screenshots/       first 10 rows of every result (PNG)
├── scripts/               pipeline: load data → export SQL → run → chart → screenshots → report → notebook
├── docs/                  problem statement
└── run_all.py             rebuilds everything from the raw CSVs
```

## Reproduce

```bash
git clone https://github.com/dot-hpg/Projects.git
cd Projects/target-brazil-sql-case-study
pip install -r requirements.txt
python run_all.py                    # ~1 minute: builds target_brazil.duckdb and every output
```

To run on **BigQuery** instead: upload the CSVs in `data/` as tables in a dataset named `target`, then run the
files in `sql/bigquery/`.

## Method notes

- **One source of truth.** Queries live once in [`scripts/query_catalog.py`](scripts/query_catalog.py) in
  BigQuery SQL; a small translator rewrites the dialect-specific functions (`TIMESTAMP_DIFF`,
  `FORMAT_TIMESTAMP`, `INFORMATION_SCHEMA`) for DuckDB, and every BigQuery query is parsed with `sqlglot` as a
  syntax check.
- **Delivery maths** follows the brief: `time_to_deliver = delivered - purchased`,
  `diff_estimated_delivery = delivered - estimated`, in whole days. An order is *late* when
  `diff_estimated_delivery > 0`.
- **Customers** are counted with `customer_unique_id` (a person), not `customer_id` (one per order).
- **Data cleaning** (encoding of the reviews file, renamed category column, duplicate geolocation rows) is
  documented in [`data/README.md`](data/README.md).

## Author

**Guntuku Hariprasad** · GitHub [@dot-hpg](https://github.com/dot-hpg)

Code is MIT-licensed. The datasets were provided for the Scaler *Target SQL* business case and are included for
reproducibility and educational use.
"""
(ROOT / "README.md").write_text(README)
print("wrote README.md")
