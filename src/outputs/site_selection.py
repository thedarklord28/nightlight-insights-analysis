"""
outputs/site_selection.py
Splits the region into a grid of zones and ranks them by combined_score.
Answers: "where's the best place to open a new business?"

If data/grid_bounds.json exists, each zone also gets its real centre
latitude/longitude plus a Google Maps link.
"""

import os
import json
import numpy as np
import plotly.graph_objects as go

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_bounds():
    path = os.path.join(DATA_DIR, "grid_bounds.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def zone_center_latlon(bounds, row_frac, col_frac):
    lon = bounds["west"] + col_frac * (bounds["east"] - bounds["west"])
    lat = bounds["north"] - row_frac * (bounds["north"] - bounds["south"])
    return lat, lon


def split_into_zones(grid, bounds, zone_rows=4, zone_cols=4):
    h, w = grid.shape
    row_step = max(h // zone_rows, 1)
    col_step = max(w // zone_cols, 1)

    zones = {}
    letters = "ABCD"
    for i in range(zone_rows):
        for j in range(zone_cols):
            r1, r2 = i * row_step, (i + 1) * row_step
            c1, c2 = j * col_step, (j + 1) * col_step
            block = grid[r1:r2, c1:c2]
            if block.size == 0:
                continue
            name = f"Zone {letters[i]}{j + 1}"
            entry = {"score": block.mean()}
            if bounds is not None:
                lat, lon = zone_center_latlon(bounds, (r1 + r2) / 2 / h, (c1 + c2) / 2 / w)
                entry["lat"], entry["lon"] = lat, lon
                entry["maps_url"] = f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            zones[name] = entry
    return zones


def run(top_n=5):
    combined_score = np.load(os.path.join(DATA_DIR, "combined_score.npy"))
    bounds = load_bounds()
    zones = split_into_zones(combined_score, bounds)

    ranked = sorted(zones.items(), key=lambda x: x[1]["score"], reverse=True)[:top_n]
    names = [r[0] for r in ranked]
    scores = [r[1]["score"] for r in ranked]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=scores, y=names, orientation="h",
                         text=[f"{s:.3f}" for s in scores], textposition="outside"))
    fig.update_layout(title=f"Top {top_n} zones for business placement",
                      xaxis_title="Combined activity score",
                      yaxis=dict(autorange="reversed"), template="plotly_white")

    out_path = os.path.join(DATA_DIR, "site_selection.html")
    fig.write_html(out_path)
    print(f"Saved chart to {out_path}")
    print("Top zones:")
    for name, info in ranked:
        if "lat" in info:
            print(f"  {name}: score={info['score']:.3f}  location=({info['lat']:.4f}, {info['lon']:.4f})  {info['maps_url']}")
        else:
            print(f"  {name}: score={info['score']:.3f}")


if __name__ == "__main__":
    run()