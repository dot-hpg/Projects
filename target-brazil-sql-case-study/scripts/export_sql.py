"""Write every query in the catalog to sql/bigquery/ and sql/duckdb/ (one file
per question plus one combined script per dialect), and syntax-check the
BigQuery versions with sqlglot."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from query_catalog import Q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def header(item, dialect):
    return (f"-- Q{item['id']} | {item['title']}\n"
            f"-- Section : {item['section']}\n"
            f"-- Question: {item['question']}\n"
            f"-- Dialect : {dialect}\n\n")


def main():
    try:
        import sqlglot
    except ImportError:
        sqlglot = None
    for dialect, key, label in [("bigquery", "bigquery", "BigQuery Standard SQL (dataset `target`)"),
                                ("duckdb", "duckdb", "DuckDB (schema `target`, see scripts/build_db.py)")]:
        out = ROOT / "sql" / dialect
        out.mkdir(parents=True, exist_ok=True)
        for f in out.glob("*.sql"):
            f.unlink()
        combined = [f"-- Target Brazil SQL case study: all queries ({label})\n"]
        for item in Q:
            text = header(item, label) + item[key]
            name = f"{item['id'].replace('.', '_')}_{item['slug']}.sql"
            (out / name).write_text(text)
            combined.append("\n" + text)
            if sqlglot and dialect == "bigquery":
                sqlglot.parse(item[key], read="bigquery")  # raises on syntax errors
        (out / "00_all_queries.sql").write_text("".join(combined))
    print(f"exported {len(Q)} queries per dialect")


if __name__ == "__main__":
    main()
