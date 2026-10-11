"""
overlay_engine.py
Turns the raw grids into the two scores every output module builds on:

- growth_score:   brightness in the LAST year minus the FIRST year
- combined_score: weighted mix of latest brightness + population ("activity")

Works with however many years fetch produced (2 or 10).
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align import align_grids
import data_io

DATA_DIR = data_io.DATA_DIR


def compute_growth_score(brightness_old, brightness_new):
    old_aligned, new_aligned = align_grids(brightness_old, brightness_new)
    return new_aligned - old_aligned


def compute_combined_score(brightness, population, light_weight=0.6, pop_weight=0.4):
    brightness_aligned, population_aligned = align_grids(brightness, population)

    # normalise both to 0-1 so one metric doesn't dominate just because its numbers are bigger
    b_norm = brightness_aligned / (brightness_aligned.max() + 1e-9)
    p_norm = population_aligned / (population_aligned.max() + 1e-9)
    return light_weight * b_norm + pop_weight * p_norm


def run():
    meta = data_io.load_meta()
    years = meta["years"]
    if len(years) < 2:
        raise RuntimeError("Need at least two years of brightness data. Run the pipeline with --mock or --city.")
    first, last = years[0], years[-1]

    brightness_first = np.nan_to_num(data_io.load_brightness(first), nan=0.0)
    brightness_last = np.nan_to_num(data_io.load_brightness(last), nan=0.0)
    population = np.nan_to_num(np.load(os.path.join(DATA_DIR, "population.npy")), nan=0.0)

    growth_score = compute_growth_score(brightness_first, brightness_last)
    combined_score = compute_combined_score(brightness_last, population)

    np.save(os.path.join(DATA_DIR, "growth_score.npy"), growth_score)
    np.save(os.path.join(DATA_DIR, "combined_score.npy"), combined_score)

    print(f"City: {meta['city']}  |  years used: {first} -> {last} ({len(years)} years available)")
    print(f"Growth score range: {growth_score.min():.2f} to {growth_score.max():.2f}")
    print(f"Combined score range: {combined_score.min():.2f} to {combined_score.max():.2f}")


if __name__ == "__main__":
    run()
