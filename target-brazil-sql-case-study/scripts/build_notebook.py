"""Generate and execute notebooks/Target_Brazil_SQL_Case_Study.ipynb from the
query catalog and the written analysis."""
from pathlib import Path
import sys
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

sys.path.insert(0, str(Path(__file__).parent))
from query_catalog import Q  # noqa: E402
from insights import ANALYSIS, ASSUMPTIONS, EXEC_SUMMARY, RECOMMENDATIONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "Target_Brazil_SQL_Case_Study.ipynb"

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [md(
    "# Target Brazil: E-commerce Operations SQL Case Study\n"
    "**Author:** Guntuku Hariprasad &nbsp;·&nbsp; **Data:** 99,441 orders, Sep 2016 - Oct 2018 "
    "&nbsp;·&nbsp; **Stack:** SQL (BigQuery dialect, executed here on DuckDB), pandas, matplotlib\n\n"
    "This notebook answers every question in the Scaler *Target SQL* business case with a SQL query, shows "
    "the result, and explains what it means for the business. Every query is written in BigQuery Standard SQL "
    "(the `bigquery` text printed above each result) and runs locally through an automatic DuckDB translation, "
    "so the notebook reproduces end to end with no cloud account.\n\n"
    "## Executive summary\n" + "\n".join(f"- {s}" for s in EXEC_SUMMARY) +
    "\n\n## Assumptions\n" + "\n".join(f"- {s}" for s in ASSUMPTIONS)),
    code(
        "import sys, subprocess\n"
        "from pathlib import Path\n"
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
        "sys.path.insert(0, str(ROOT / 'scripts'))\n"
        "import duckdb, pandas as pd\n"
        "from IPython.display import Image, Markdown, display\n"
        "from query_catalog import Q\n"
        "pd.set_option('display.max_columns', 20); pd.set_option('display.width', 200)\n"
        "DB = ROOT / 'target_brazil.duckdb'\n"
        "if not DB.exists():  # first run: load the 8 CSVs from data/ into DuckDB\n"
        "    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_db.py')], check=True)\n"
        "con = duckdb.connect(str(DB), read_only=True)\n"
        "QUERIES = {q['id']: q for q in Q}\n\n"
        "def run(qid, show_sql=True, rows=10):\n"
        "    q = QUERIES[qid]\n"
        "    if show_sql:\n"
        "        print(q['bigquery'])\n"
        "    df = con.execute(q['duckdb']).df()\n"
        "    print(f'{len(df):,} rows')\n"
        "    return df.head(rows)\n\n"
        "def chart(name):\n"
        "    display(Image(filename=str(ROOT / 'charts' / name), width=900))"),
    code("con.sql(\"SELECT table_name, estimated_size AS approx_rows FROM duckdb_tables() "
         "WHERE schema_name = 'target' ORDER BY 2 DESC\").df()"),
]
current = None
for item in Q:
    if item["section"] != current:
        current = item["section"]
        cells.append(md(f"## {current}"))
    cells.append(md(f"### Q{item['id']} {item['title']}\n> {item['question']}"))
    cells.append(code(f"run('{item['id']}')"))
    a = ANALYSIS[item["id"]]
    if a.get("chart"):
        cells.append(code(f"chart('{a['chart']}')"))
    cells.append(md("**Insights**\n" + "\n".join(f"- {s}" for s in a["insights"]) +
                    "\n\n**Recommendations**\n" + "\n".join(f"- {s}" for s in a["recs"])))
cells.append(md("## 8. Actionable insights & recommendations\n" +
                "\n".join(f"{i}. **{h}.** {b}" for i, (h, b) in enumerate(RECOMMENDATIONS, 1))))

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3",
                                                               "language": "python"}})
ExecutePreprocessor(timeout=600, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(NB.parent)}})
NB.write_text(nbf.writes(nb))
print("wrote", NB)

import subprocess  # noqa: E402
subprocess.run([sys.executable, "-m", "nbconvert", "--to", "html", str(NB), "--output-dir", str(NB.parent)],
               check=True, capture_output=True)
print("wrote", NB.with_suffix(".html"))
