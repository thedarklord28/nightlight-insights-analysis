"""
outputs/site_selection.py
Splits the region into a grid of zones and ranks them by combined_score.
Answers: "where's the best place to open a new business?"
"""

import os
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def split_into_zones(grid: np.ndarray, zone_rows=4, zone_cols=4):
    """
    Splits a grid into zone_rows x zone_cols blocks and averages each block.
    Returns a dict like {"Zone A1": score, "Zone A2": score, ...}
    """
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
    combined_score = np.load(os.path.join(DATA_DIR, "combined_score.npy"))
    zones = split_into_zones(combined_score)

    ranked = sorted(zones.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names = [r[0] for r in ranked]
    scores = [r[1] for r in ranked]

    plt.figure(figsize=(6, 4))
    plt.barh(names, scores)
    plt.gca().invert_yaxis()
    plt.xlabel("Combined activity score")
    plt.title(f"Top {top_n} zones for business placement")
    plt.tight_layout()

    out_path = os.path.join(DATA_DIR, "site_selection.png")
    plt.savefig(out_path)
    print(f"Saved chart to {out_path}")
    print("Top zones:")
    for name, score in ranked:
        print(f"  {name}: {score:.3f}")


if __name__ == "__main__":
    run()
