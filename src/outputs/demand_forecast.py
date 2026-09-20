"""
outputs/demand_forecast.py
Ranks zones by growth_score to forecast where delivery demand is likely
rising fastest. Follows the same pattern as site_selection.py and
policing_priority.py so it plugs into run_pipeline.py the same way.
"""

import os
import numpy as np
import plotly.graph_objects as go

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def split_into_zones(grid: np.ndarray, zone_rows=4, zone_cols=4):
    h, w = grid.shape
    row_step = max(h // zone_rows, 1)
    col_step = max(w // zone_cols, 1)

    zones = {}
    letters = "ABCD"
    for i in range(zone_rows):
        for j in range(zone_cols):
            block = grid[i * row_step:(i + 1) * row_step, j * col_step:(j + 1) * col_step]
            if block.size == 0:
                continue
            zones[f"Zone {letters[i]}{j + 1}"] = float(block.mean())
    return zones


def run(top_n=5):
    growth_score = np.load(os.path.join(DATA_DIR, "growth_score.npy"))
    clean = np.nan_to_num(growth_score, nan=0.0)

    zones = split_into_zones(clean)
    ranked = sorted(zones.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names = [r[0] for r in ranked]
    scores = [r[1] for r in ranked]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scores, y=names,
        orientation="h",
        marker=dict(color=scores, colorscale=[[0.0, "#D1FAE5"], [1.0, "#10B981"]]),
        text=[f"{s:+.2f}" for s in scores],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Top {top_n} zones by forecasted demand growth",
        xaxis_title="Growth score (2019 to 2024)",
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
    )

    out_path = os.path.join(DATA_DIR, "demand_forecast.html")
    fig.write_html(out_path)
    print(f"Saved chart to {out_path}")
    print("Top rising-demand zones:")
    for name, score in ranked:
        print(f"  {name}: {score:+.3f}")


if __name__ == "__main__":
    run()