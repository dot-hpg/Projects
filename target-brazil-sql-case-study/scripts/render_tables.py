"""Render the first 10 rows of every query result as a PNG 'screenshot'
(outputs/screenshots/<id>_<slug>.png), as the submission guidelines require."""
from pathlib import Path
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from query_catalog import Q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "outputs" / "results", ROOT / "outputs" / "screenshots"
HEADER_BG, BORDER, INK, MUTED, ZEBRA = "#eef3fb", "#d9dde3", "#1f1f1f", "#6b6b6b", "#fafbfc"


def fmt(v, col):
    if pd.isna(v):
        return "null"
    if isinstance(v, float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v}" if col.endswith(("year", "month", "month_no", "installments", "rank_no")) else f"{v:,}"
    return str(v)


def render(item):
    stem = f"{item['id'].replace('.', '_')}_{item['slug']}"
    df = pd.read_csv(RES / f"{stem}.csv")
    total = len(df)
    head = df.head(10)
    cells = [[fmt(v, c) for v, c in zip(row, head.columns)] for row in head.itertuples(index=False)]
    cols = ["Row"] + list(head.columns)
    cells = [[str(i + 1)] + r for i, r in enumerate(cells)]
    fig, ax = plt.subplots(figsize=(6, 0.3 * (len(cells) + 1)))
    ax.axis("off")
    t = ax.table(cellText=cells, colLabels=cols, loc="upper left", cellLoc="left")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.auto_set_column_width(list(range(len(cols))))
    t.scale(1, 1.35)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(BORDER)
        cell.set_linewidth(0.5)
        if r == 0:
            cell.set_facecolor(HEADER_BG)
            cell.set_text_props(weight="bold", color=INK)
        else:
            cell.set_facecolor(ZEBRA if r % 2 == 0 else "white")
            cell.set_text_props(color=MUTED if c == 0 else INK)
    note = f"Showing {len(cells)} of {total:,} rows" if total > 10 else f"{total} row{'s' if total != 1 else ''}"
    ax.text(0, -0.04, f"Q{item['id']} result  ·  {note}", transform=ax.transAxes, fontsize=7.5, color=MUTED, va="top")
    fig.savefig(OUT / f"{stem}.png", dpi=200, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for item in Q:
        render(item)
    print(f"rendered {len(Q)} result screenshots")
