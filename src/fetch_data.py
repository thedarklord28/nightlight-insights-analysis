"""
fetch_data.py
Pulls (or fakes) two grids: night-light brightness and daytime population density.
Saves them as .npy files in data/ so the rest of the pipeline can use them
without caring where they came from.

Usage:
    python src\\fetch_data.py --mock          # instant, no sign-up needed
    python src\\fetch_data.py --real          # needs Earth Engine auth done first
"""

import argparse
import os
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def make_mock_grid(shape=(40, 40), seed=0, hotspots=None):
    """
    Builds a fake grid that looks like real night-light / density data:
    mostly low background values with a few bright 'hotspot' clusters.
    hotspots: list of (row_start, row_end, col_start, col_end, boost)
    """
    rng = np.random.default_rng(seed)
    grid = rng.normal(5, 1.5, shape)
    grid = np.clip(grid, 0, None)

    if hotspots is None:
        hotspots = [
            (8, 14, 6, 13, 10),
            (25, 32, 28, 35, 8),
            (15, 20, 20, 26, 6),
        ]
    for r1, r2, c1, c2, boost in hotspots:
        grid[r1:r2, c1:c2] += boost
    return grid


def fetch_mock_data():
    print("Generating mock data (no internet or Earth Engine needed)...")

    # night-light brightness for two years, so we can compute growth later
    brightness_2019 = make_mock_grid(seed=1)
    brightness_2024 = make_mock_grid(
        seed=1,
        hotspots=[
            (8, 14, 6, 13, 15),   # this hotspot grew brighter since 2019
            (25, 32, 28, 35, 9),
            (15, 20, 20, 26, 5),  # this one barely changed
            (2, 6, 30, 36, 7),    # a brand-new hotspot that appeared
        ],
    )

    # daytime population density (independent pattern, some overlap with light)
    population = make_mock_grid(seed=2, hotspots=[
        (8, 14, 6, 13, 6),
        (30, 36, 5, 12, 12),   # high population, but NOT bright at night -> policing flag later
        (18, 24, 24, 30, 5),
    ])

    np.save(os.path.join(DATA_DIR, "brightness_2019.npy"), brightness_2019)
    np.save(os.path.join(DATA_DIR, "brightness_2024.npy"), brightness_2024)
    np.save(os.path.join(DATA_DIR, "population.npy"), population)
    print(f"Saved 3 grids to {os.path.abspath(DATA_DIR)}")


def fetch_real_data():
    """
    Pulls real VIIRS night-light data from Google Earth Engine.
    Requires: pip install earthengine-api, then `earthengine authenticate` once.
    NOTE: population density here still needs a real source swapped in
    (e.g. WorldPop download) -- this function only pulls night-lights for now.
    """
    import ee
    ee.Initialize()

    # TODO: replace with your actual region of interest
    region = ee.Geometry.Rectangle([80.15, 12.85, 80.25, 12.95])

    def get_year_image(year):
        collection = (
            ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .filterBounds(region)
        )
        return collection.median().clip(region)

    img_2019 = get_year_image(2019)
    img_2024 = get_year_image(2024)

    print("Pulled Earth Engine images for 2019 and 2024.")
    print("Next step: export these to Drive or download as GeoTIFF using")
    print("ee.batch.Export.image.toDrive(...) -- see Earth Engine docs.")
    print("Once downloaded, load them with rasterio in align.py instead of .npy files.")

    return img_2019, img_2024


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use fake data (no sign-up needed)")
    parser.add_argument("--real", action="store_true", help="Pull real data from Earth Engine")
    args = parser.parse_args()

    if args.real:
        fetch_real_data()
    else:
        fetch_mock_data()
