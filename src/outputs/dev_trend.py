"""
outputs/dev_trend.py
Year-by-year development trend: average night-light brightness for EVERY year
available, plus the year-on-year % change. Answers "is this area developing?"
"""

import os
import sys

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import data_io

DATA_DIR = data_io.DATA_DIR


def run():
    meta = data_io.load_meta()
    by_year = data_io.load_all_brightness()
    years = sorted(by_year)
    means = [float(np.mean(np.nan_to_num(by_year[y], nan=0.0))) for y in years]

    yoy = [None] + [
        ((means[i] - means[i - 1]) / means[i - 1] * 100) if means[i - 1] else None
        for i in range(1, len(means))
    ]
    total_pct = ((means[-1] - means[0]) / means[0] * 100) if means[0] else 0.0

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=[y for y, v in zip(years, yoy) if v is not None],
        y=[v for v in yoy if v is not None],
        name="Year-on-year change (%)",
        marker_color=["#10B981" if v >= 0 else "#EF4444" for v in yoy if v is not None],
        opacity=0.35,
    ), secondary_y=True)
    fig.add_trace(go.Scatter(
        x=years, y=means, name="Average brightness",
        mode="lines+markers", line=dict(width=3, color="#2563EB"), marker=dict(size=9),
    ), secondary_y=False)

    fig.update_layout(
        title=f"{data_io.city_short(meta['city'])}: development trend {years[0]}-{years[-1]} ({total_pct:+.1f}% overall)",
        template="plotly_white",
        xaxis=dict(tickmode="array", tickvals=years),
        legend=dict(orientation="h", y=-0.2),
    )
    fig.update_yaxes(title_text="Average night-light brightness", secondary_y=False)
    fig.update_yaxes(title_text="Year-on-year change (%)", secondary_y=True, showgrid=False)

    out_path = os.path.join(DATA_DIR, "dev_trend.html")
    fig.write_html(out_path)
    print(f"Saved chart to {out_path}")
    print("Year  | avg brightness | YoY change")
    for y, m, c in zip(years, means, yoy):
        print(f"{y}  | {m:14.2f} | {'-' if c is None else f'{c:+.1f}%'}")
    print(f"Overall change {years[0]} -> {years[-1]}: {total_pct:+.1f}%")


if __name__ == "__main__":
    run()
