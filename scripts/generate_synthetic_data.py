from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(99)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/metrics.db"))
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    days = pd.date_range("2024-01-01", periods=90, freq="D")
    rows = []
    for d in days:
        for region in ["East", "West", "Central"]:
            rows.append(
                {
                    "metric_date": d.date().isoformat(),
                    "region": region,
                    "revenue_usd": round(float(RNG.uniform(8000, 42000)), 2),
                    "orders": int(RNG.integers(120, 900)),
                }
            )
    df = pd.DataFrame(rows)
    import sqlite3

    conn = sqlite3.connect(args.out)
    df.to_sql("daily_region_metrics", conn, if_exists="replace", index=False)
    conn.close()
    df.to_csv(args.out.with_suffix(".csv"), index=False)
    print(f"Wrote SQLite {args.out} and CSV")


if __name__ == "__main__":
    main()
