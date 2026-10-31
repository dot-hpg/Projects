"""Run every DuckDB query in the catalog against target_brazil.duckdb and save
full results to outputs/results/<id>_<slug>.csv."""
from pathlib import Path
import sys
import duckdb
sys.path.insert(0, str(Path(__file__).parent))
from query_catalog import Q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "results"


def run(verbose=True):
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ROOT / "target_brazil.duckdb"), read_only=True)
    results = {}
    for item in Q:
        df = con.execute(item["duckdb"]).df()
        for col in df.columns:  # SUM(CASE ...) comes back as float; restore integer counts
            if df[col].dtype.kind == "f" and df[col].dropna().apply(float.is_integer).all() \
                    and not col.startswith(("pct", "avg", "cost", "total_value", "yoy", "mom")):
                df[col] = df[col].astype("Int64")
        results[item["id"]] = df
        df.to_csv(OUT / f"{item['id'].replace('.', '_')}_{item['slug']}.csv", index=False)
        if verbose:
            print(f"\n=== Q{item['id']} {item['title']}  ({len(df)} rows)")
            print(df.head(30).to_string(max_colwidth=40))
    return results


if __name__ == "__main__":
    run()
