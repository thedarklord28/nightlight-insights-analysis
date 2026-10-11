"""
data_io.py
Shared helpers so every script finds the same files the same way.

After a fetch, the data folder contains:
    brightness_<year>.npy   one night-light grid per year
    population.npy          population density grid (same shape)
    grid_bounds.json        real lat/lon edges of the grid
    meta.json               city name, years, how the data was produced
"""

import glob
import json
import os
import re

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
META_PATH = os.path.join(DATA_DIR, "meta.json")
DEFAULT_CITY = "Chennai, India"


def _years_on_disk():
    years = []
    for path in glob.glob(os.path.join(DATA_DIR, "brightness_*.npy")):
        m = re.search(r"brightness_(\d{4})\.npy$", path)
        if m:
            years.append(int(m.group(1)))
    return sorted(years)


def load_meta():
    """City + list of years. Falls back to whatever brightness_<year>.npy files
    exist, so data from older versions of the pipeline still works."""
    meta = {}
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            meta = json.load(f)

    on_disk = _years_on_disk()
    years = [y for y in meta.get("years", []) if y in on_disk] or on_disk
    meta["years"] = sorted(years)
    meta.setdefault("city", DEFAULT_CITY)
    meta.setdefault("mode", "unknown")
    meta["first_year"] = meta["years"][0] if meta["years"] else None
    meta["last_year"] = meta["years"][-1] if meta["years"] else None
    return meta


def save_meta(city, years, mode, **extra):
    os.makedirs(DATA_DIR, exist_ok=True)
    meta = {"city": city, "years": sorted(years), "mode": mode}
    meta.update(extra)
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)


def brightness_path(year):
    return os.path.join(DATA_DIR, f"brightness_{year}.npy")


def load_brightness(year):
    return np.load(brightness_path(year))


def load_all_brightness():
    """{year: 2D array} for every year available."""
    years = load_meta()["years"]
    if not years:
        raise FileNotFoundError(
            "No brightness_<year>.npy files found in data\\. "
            "Run the pipeline with --mock or --city first."
        )
    return {y: load_brightness(y) for y in years}


def clear_brightness_files():
    """Remove old per-year grids so a new city never mixes with the previous one."""
    for path in glob.glob(os.path.join(DATA_DIR, "brightness_*.npy")):
        os.remove(path)


def city_short(city):
    return city.split(",")[0].strip() or city


def city_slug(city):
    slug = re.sub(r"[^a-z0-9]+", "", city_short(city).lower())
    return slug or "city"


def is_chennai(city):
    return "chennai" in city.lower()
