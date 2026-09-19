"""
overlay_engine.py
The core of the pipeline: takes the night-light and population grids and
produces two derived grids that every output module builds on:

- growth_score:   how much brighter an area got over time
- combined_score: a weighted mix of current brightness + population,
                   representing overall "activity" in an area
"""

import os
import numpy as np
from align import align_grids

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def compute_growth_score(brightness_old: np.ndarray, brightness_new: np.ndarray) -> np.ndarray:
    old_aligned, new_aligned = align_grids(brightness_old, brightness_new)
    return new_aligned - old_aligned


def compute_combined_score(brightness: np.ndarray, population: np.ndarray,
                            light_weight: float = 0.6, pop_weight: float = 0.4) -> np.ndarray:
    brightness_aligned, population_aligned = align_grids(brightness, population)

    # normalize both to 0-1 so one metric doesn't dominate just because
    # its raw numbers are bigger
    b_norm = brightness_aligned / (brightness_aligned.max() + 1e-9)
    p_norm = population_aligned / (population_aligned.max() + 1e-9)

    return light_weight * b_norm + pop_weight * p_norm


def run():
    brightness_2019 = np.load(os.path.join(DATA_DIR, "brightness_2019.npy"))
    brightness_2024 = np.load(os.path.join(DATA_DIR, "brightness_2024.npy"))
    population = np.load(os.path.join(DATA_DIR, "population.npy"))

    growth_score = compute_growth_score(brightness_2019, brightness_2024)
    combined_score = compute_combined_score(brightness_2024, population)

    np.save(os.path.join(DATA_DIR, "growth_score.npy"), growth_score)
    np.save(os.path.join(DATA_DIR, "combined_score.npy"), combined_score)

    print("Saved growth_score.npy and combined_score.npy to data/")
    print(f"Growth score range: {growth_score.min():.2f} to {growth_score.max():.2f}")
    print(f"Combined score range: {combined_score.min():.2f} to {combined_score.max():.2f}")


if __name__ == "__main__":
    run()
