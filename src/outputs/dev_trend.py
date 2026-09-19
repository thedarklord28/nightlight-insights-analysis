"""
outputs/dev_trend.py
Simplest output: plots average brightness over time for the whole region.
Answers: "is this area actually developing?"
"""

import os
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def run():
    brightness_2019 = np.load(os.path.join(DATA_DIR, "brightness_2019.npy"))
    brightness_2024 = np.load(os.path.join(DATA_DIR, "brightness_2024.npy"))

    # with only 2 years of mock data we just connect two points --
    # once you pull real data for more years, add them to this list
    years = [2019, 2024]
    avg_brightness = [brightness_2019.mean(), brightness_2024.mean()]

    pct_change = (avg_brightness[-1] - avg_brightness[0]) / avg_brightness[0] * 100

    plt.figure(figsize=(6, 4))
    plt.plot(years, avg_brightness, marker="o", linewidth=2)
    plt.fill_between(years, avg_brightness, min(avg_brightness) - 1, alpha=0.1)
    plt.ylabel("Average night-light brightness")
    plt.title(f"Development trend ({pct_change:+.1f}% change)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(DATA_DIR, "dev_trend.png")
    plt.savefig(out_path)
    print(f"Saved chart to {out_path}")
    print(f"Change: {pct_change:+.1f}% over the period")


if __name__ == "__main__":
    run()
