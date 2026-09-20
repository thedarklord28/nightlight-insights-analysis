"""
outputs/policing_priority.py
Generates dual analysis for policing priorities (Under-Lit Risk) 
and commercial/over-illuminated zones (Over-Lit / Low-Pop).
"""

import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def split_into_zones(grid: np.ndarray, zone_rows=4, zone_cols=4):
    h, w = grid.shape
    row_step = h // zone_rows
    col_step = w // zone_cols

    zones = {}
    letters = "ABCD"
    for i in range(zone_rows):
        for j in range(zone_cols):
            block = grid[i * row_step:(i + 1) * row_step, j * col_step:(j + 1) * col_step]
            name = f"Zone {letters[i]}{j + 1}"
            zones[name] = block.mean()
    return zones


def run(top_n=5):
    population = np.load(os.path.join(DATA_DIR, "population.npy"))
    brightness_2024 = np.load(os.path.join(DATA_DIR, "brightness_2024.npy"))

    pop_zones = split_into_zones(population)
    bright_zones = split_into_zones(brightness_2024)

    max_pop = max(pop_zones.values()) + 1e-9
    max_bright = max(bright_zones.values()) + 1e-9

    priority_zones = {}
    for name in pop_zones:
        pop_norm = pop_zones[name] / max_pop
        bright_norm = bright_zones[name] / max_bright
        priority_zones[name] = pop_norm - bright_norm

    # 1. Top High Risk (Positive Mismatch: High Pop, Low Light)
    pos_zones = sorted([item for item in priority_zones.items() if item[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]
    
    # 2. Top Over-Illuminated / Low Pop (Negative Mismatch: High Light, Low Pop)
    neg_zones = sorted([item for item in priority_zones.items() if item[1] < 0], key=lambda x: x[1])[:top_n]

    # Subplot setup: Side-by-side charts
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("Top Policing Priority (Under-Lit Zones)", "Top Over-Illuminated / Commercial Zones")
    )

    if pos_zones:
        pos_names = [r[0] for r in reversed(pos_zones)]
        pos_scores = [r[1] for r in reversed(pos_zones)]
        fig.add_trace(
            go.Bar(x=pos_scores, y=pos_names, orientation='h', marker_color='crimson', name="High Risk"),
            row=1, col=1
        )

    if neg_zones:
        neg_names = [r[0] for r in reversed(neg_zones)]
        neg_scores = [abs(r[1]) for r in reversed(neg_zones)]  # Convert to positive magnitude for clear charting
        fig.add_trace(
            go.Bar(x=neg_scores, y=neg_names, orientation='h', marker_color='royalblue', name="Over-Illuminated"),
            row=1, col=2
        )

    fig.update_layout(
        title_text="Dual-Aspect Spatial Mismatch Analysis",
        template="plotly_white",
        showlegend=False
    )

    out_path = os.path.join(DATA_DIR, "policing_priority.html")
    fig.write_html(out_path)
    print(f"Saved interactive dual-analysis chart to {out_path}")

    print("\n--- High Policing Priority (Under-Lit) ---")
    for name, score in pos_zones:
        print(f"  {name}: {score:+.3f}")

    print("\n--- High Commercial / Over-Illuminated Zones ---")
    for name, score in neg_zones:
        print(f"  {name}: {score:+.3f}")


if __name__ == "__main__":
    run()