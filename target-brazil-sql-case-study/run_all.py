"""Rebuild everything from the raw CSVs in data/:
DuckDB database -> SQL files -> query results -> charts -> result screenshots
-> notebook -> Word/PDF report.

    pip install -r requirements.txt
    python run_all.py
"""
import subprocess
import sys
from pathlib import Path

STEPS = ["build_db.py", "export_sql.py", "run_queries.py", "make_charts.py", "build_readme.py",
         "render_tables.py", "build_report.py", "build_notebook.py"]

for step in STEPS:
    print(f"\n>>> {step}")
    subprocess.run([sys.executable, str(Path(__file__).parent / "scripts" / step)], check=True,
                   stdout=subprocess.DEVNULL if step == "run_queries.py" else None)
print("\nDone. See outputs/, charts/, report/ and notebooks/.")
