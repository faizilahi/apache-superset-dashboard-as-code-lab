"""Render Superset-style dashboard-as-code to static HTML + PNG tiles."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]


def run_sql(db_path: Path, sql: str) -> pd.DataFrame:
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    return pd.read_sql_query(sql, engine)


def render_chart(df: pd.DataFrame, viz_type: str, title: str, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    if viz_type == "line" and "metric_date" in df.columns:
        for region, g in df.groupby("region"):
            ax.plot(g["metric_date"], g["revenue_usd"], label=region)
        ax.legend()
        ax.set_ylabel("Revenue USD")
    elif viz_type == "bar" and "region" in df.columns:
        ax.bar(df["region"], df["orders"], color=["#20A7C9", "#454E7C", "#5AC189"])
        ax.set_ylabel("Orders")
    ax.set_title(title)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


def render_dashboard(yaml_path: Path, db_path: Path, out_dir: Path) -> Path:
    spec = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    tiles = []
    for i, chart in enumerate(spec.get("charts", [])):
        sql = chart["query"]["sql"]
        df = run_sql(db_path, sql)
        png = out_dir / f"tile_{i+1}.png"
        render_chart(df, chart["viz_type"], chart["slice_name"], png)
        tiles.append({"title": chart["slice_name"], "image": png.name, "rows": len(df)})
    html_parts = [
        "<html><head><title>Superset-as-code export</title></head><body>",
        f"<h1>{spec.get('dashboard_title')}</h1>",
        f"<p>{spec.get('description')}</p>",
    ]
    for t in tiles:
        html_parts.append(f"<h2>{t['title']}</h2><img src='{t['image']}' width='700'/>")
    html_parts.append("</body></html>")
    html_path = out_dir / "dashboard.html"
    html_path.write_text("\n".join(html_parts), encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(tiles, indent=2), encoding="utf-8")
    return html_path


def main() -> None:
    yaml_path = ROOT / "dashboards" / "executive_kpi.yaml"
    db = ROOT / "data" / "metrics.db"
    out = ROOT / "output"
    path = render_dashboard(yaml_path, db, out)
    print(f"Rendered {path}")


if __name__ == "__main__":
    main()
