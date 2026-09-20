"""
diagnose_tifs.py
Checks the raw, unprocessed contents of your three GeoTIFFs so we can see
exactly where the NaN/zero problem is coming from -- before any
reprojection or alignment touches the data.

Usage:
    python src\\diagnose_tifs.py
"""

import os
import numpy as np
import rasterio

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

files = ["brightness_2019.tif", "brightness_2024.tif", "population.tif"]

for fname in files:
    path = os.path.join(DATA_DIR, fname)
    print(f"\n--- {fname} ---")
    if not os.path.exists(path):
        print("FILE NOT FOUND at this path.")
        continue

    with rasterio.open(path) as src:
        print(f"CRS: {src.crs}")
        print(f"Shape: {src.height} x {src.width}")
        print(f"Bounds: {src.bounds}")
        print(f"Nodata value: {src.nodata}")

        band = src.read(1).astype("float64")
        total = band.size
        nan_count = np.isnan(band).sum()
        zero_count = (band == 0).sum()

        print(f"Total pixels: {total}")
        print(f"NaN pixels: {nan_count} ({100*nan_count/total:.1f}%)")
        print(f"Zero pixels: {zero_count} ({100*zero_count/total:.1f}%)")

        valid = band[~np.isnan(band)]
        if len(valid) > 0:
            print(f"Min (excluding NaN): {valid.min():.4f}")
            print(f"Max (excluding NaN): {valid.max():.4f}")
            print(f"Mean (excluding NaN): {valid.mean():.4f}")
        else:
            print("Every single pixel is NaN -- the file has no valid data at all.")