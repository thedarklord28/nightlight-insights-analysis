"""
fetch_data.py
Mock data generator -- instant, no Earth Engine or internet needed.
Produces one brightness grid PER YEAR so the year-wise charts have something
to draw, plus a population grid.

For real data use fetch_city.py (any city) instead.

Usage:
    python src\fetch_data.py --mock
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_io

DATA_DIR = data_io.DATA_DIR


def make_mock_grid(shape=(40, 40), seed=0, hotspots=None):
    """Mostly-low background with a few bright hotspot clusters.
    hotspots: list of (row_start, row_end, col_start, col_end, boost)"""
    rng = np.random.default_rng(seed)
    grid = np.clip(rng.normal(5, 1.5, shape), 0, None)
    for r1, r2, c1, c2, boost in hotspots or []:
        grid[r1:r2, c1:c2] += boost
    return grid


def fetch_mock_data(first_year=2019, last_year=2024, shape=(40, 40)):
    print("Generating mock data (no internet or Earth Engine needed)...")
    os.makedirs(DATA_DIR, exist_ok=True)
    data_io.clear_brightness_files()

    years = list(range(first_year, last_year + 1))
    steps = max(len(years) - 1, 1)

    # (row_start, row_end, col_start, col_end, boost_in_first_year, boost_in_last_year)
    spec = [
        (8, 14, 6, 13, 10, 15),    # grew a lot
        (25, 32, 28, 35, 8, 9),    # roughly flat
        (15, 20, 20, 26, 6, 5),    # slightly down
        (2, 6, 30, 36, 0, 7),      # brand-new hotspot
    ]
    for i, year in enumerate(years):
        t = i / steps
        hotspots = [(r1, r2, c1, c2, b0 + (b1 - b0) * t) for r1, r2, c1, c2, b0, b1 in spec]
        grid = make_mock_grid(shape, seed=1, hotspots=hotspots)
        jitter = np.random.default_rng(100 + year).normal(0, 0.3, shape)
        np.save(data_io.brightness_path(year), np.clip(grid + jitter, 0, None))

    population = make_mock_grid(shape, seed=2, hotspots=[
        (8, 14, 6, 13, 6),
        (30, 36, 5, 12, 12),   # high population, not bright -> policing flag
        (18, 24, 24, 30, 5),
    ])
    np.save(os.path.join(DATA_DIR, "population.npy"), population)

    # Mock data is "Chennai", so write Chennai's bounds. This also overwrites any
    # grid_bounds.json left behind by a previous real fetch of another city.
    with open(os.path.join(DATA_DIR, "grid_bounds.json"), "w") as f:
        json.dump({"west": 80.00, "south": 12.80, "east": 80.35, "north": 13.20,
                   "height": shape[0], "width": shape[1]}, f, indent=2)

    data_io.save_meta("Chennai, India", years, "mock")
    print(f"Saved {len(years)} yearly brightness grids ({years[0]}-{years[-1]}) + population to {os.path.abspath(DATA_DIR)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use fake data (default)")
    parser.parse_args()
    fetch_mock_data()
