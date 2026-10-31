"""Load the 8 Target Brazil CSVs into a local DuckDB database (schema `target`),
mirroring the BigQuery dataset used in the Scaler case study, so every query in
sql/duckdb/ runs unchanged against `target.<table>`.

Usage:  python scripts/build_db.py            -> creates target_brazil.duckdb in repo root
"""
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB = ROOT / "target_brazil.duckdb"

TABLES = {
    "customers": """
        SELECT customer_id, customer_unique_id,
               CAST(customer_zip_code_prefix AS BIGINT) AS customer_zip_code_prefix,
               customer_city, customer_state
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    "sellers": """
        SELECT seller_id, CAST(seller_zip_code_prefix AS BIGINT) AS seller_zip_code_prefix,
               seller_city, seller_state
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    "geolocation": """
        SELECT CAST(geolocation_zip_code_prefix AS BIGINT) AS geolocation_zip_code_prefix,
               CAST(geolocation_lat AS DOUBLE) AS geolocation_lat,
               CAST(geolocation_lng AS DOUBLE) AS geolocation_lng,
               geolocation_city, geolocation_state
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    "orders": """
        SELECT order_id, customer_id, order_status,
               CAST(order_purchase_timestamp AS TIMESTAMP)       AS order_purchase_timestamp,
               CAST(order_approved_at AS TIMESTAMP)              AS order_approved_at,
               CAST(order_delivered_carrier_date AS TIMESTAMP)   AS order_delivered_carrier_date,
               CAST(order_delivered_customer_date AS TIMESTAMP)  AS order_delivered_customer_date,
               CAST(order_estimated_delivery_date AS TIMESTAMP)  AS order_estimated_delivery_date
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    "order_items": """
        SELECT order_id, CAST(order_item_id AS BIGINT) AS order_item_id, product_id, seller_id,
               CAST(shipping_limit_date AS TIMESTAMP) AS shipping_limit_date,
               CAST(price AS DOUBLE) AS price, CAST(freight_value AS DOUBLE) AS freight_value
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    "payments": """
        SELECT order_id, CAST(payment_sequential AS BIGINT) AS payment_sequential, payment_type,
               CAST(payment_installments AS BIGINT) AS payment_installments,
               CAST(payment_value AS DOUBLE) AS payment_value
        FROM read_csv('{p}', header=true, all_varchar=true)""",
    # review dates are stored as dd/mm/yy H:MM; the file is latin-1 encoded (not UTF-8)
    "order_reviews": """
        SELECT review_id, order_id, CAST(review_score AS BIGINT) AS review_score,
               review_comment_title,
               strptime(review_creation_date, '%d/%m/%y %-H:%M')    AS review_creation_date,
               strptime(review_answer_timestamp, '%d/%m/%y %-H:%M') AS review_answer_timestamp
        FROM reviews_raw""",
    # source header says `product category`; renamed to the documented column name
    "products": """
        SELECT product_id, "product category" AS product_category_name,
               CAST(product_name_length AS BIGINT)        AS product_name_length,
               CAST(product_description_length AS BIGINT) AS product_description_length,
               CAST(product_photos_qty AS BIGINT)  AS product_photos_qty,
               CAST(product_weight_g AS BIGINT)    AS product_weight_g,
               CAST(product_length_cm AS BIGINT)   AS product_length_cm,
               CAST(product_height_cm AS BIGINT)   AS product_height_cm,
               CAST(product_width_cm AS BIGINT)    AS product_width_cm
        FROM read_csv('{p}', header=true, all_varchar=true)""",
}


def build(db_path: Path = DB) -> duckdb.DuckDBPyConnection:
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA target")
    # order_reviews.csv is not valid UTF-8 (some titles carry truncated byte
    # sequences), so it is decoded leniently with pandas and handed to DuckDB.
    reviews_raw = pd.read_csv(DATA / "order_reviews.csv", dtype=str, encoding="latin-1",
                              keep_default_na=False, na_values=[""])
    con.register("reviews_raw", reviews_raw)
    for name, sql in TABLES.items():
        con.execute(f"CREATE TABLE target.{name} AS " + sql.format(p=(DATA / f"{name}.csv").as_posix()))
        n = con.execute(f"SELECT COUNT(*) FROM target.{name}").fetchone()[0]
        print(f"target.{name:<12} {n:>9,} rows")
    return con


if __name__ == "__main__":
    build()
