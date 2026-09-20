"""
load_real_data.py
Reads the three real GeoTIFFs you downloaded (brightness_2019.tif,
brightness_2024.tif, population.tif), reprojects them all onto the SAME
pixel grid (real satellite/population data almost never share a grid by
default), and saves them as .npy files.

After running this once, overlay_engine.py and everything in outputs/
work exactly as they did with mock data -- they don't know or care that
the numbers are real now.

Usage:
    python src\\load_real_data.py
"""

import os
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.errors import RasterioIOError

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

BRIGHTNESS_2019_TIF = os.path.join(DATA_DIR, "brightness_2019.tif")
BRIGHTNESS_2024_TIF = os.path.join(DATA_DIR, "brightness_2024.tif")
POPULATION_TIF = os.path.join(DATA_DIR, "population.tif")


def load_band(path):
    """Opens a GeoTIFF and returns (array, profile). profile has the
    georeferencing info (crs, transform) we need to align other rasters to it."""
    with rasterio.open(path) as src:
        array = src.read(1).astype("float64")
        array = np.where(array < 0, 0, array)   # some rasters use negative = no-data
        profile = src.profile
    return array, profile


def reproject_to_match(source_path, reference_profile):
    """Reprojects source_path onto the reference raster's exact grid
    (same shape, same CRS, same resolution) so it lines up pixel-for-pixel."""
    with rasterio.open(source_path) as src:
        destination = np.zeros(
            (reference_profile["height"], reference_profile["width"]),
            dtype="float64",
        )
        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=reference_profile["transform"],
            dst_crs=reference_profile["crs"],
            resampling=Resampling.bilinear,
        )
    destination = np.where(destination < 0, 0, destination)
    return destination


def run():
    for path in [BRIGHTNESS_2019_TIF, BRIGHTNESS_2024_TIF, POPULATION_TIF]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing {path}\n"
                f"Make sure brightness_2019.tif, brightness_2024.tif, and "
                f"population.tif are all in the data\\ folder."
            )

    print("Loading brightness_2019.tif as the reference grid...")
    brightness_2019, ref_profile = load_band(BRIGHTNESS_2019_TIF)

    print("Reprojecting brightness_2024.tif onto the same grid...")
    brightness_2024 = reproject_to_match(BRIGHTNESS_2024_TIF, ref_profile)

    print("Reprojecting population.tif onto the same grid...")
    population = reproject_to_match(POPULATION_TIF, ref_profile)

    np.save(os.path.join(DATA_DIR, "brightness_2019.npy"), brightness_2019)
    np.save(os.path.join(DATA_DIR, "brightness_2024.npy"), brightness_2024)
    np.save(os.path.join(DATA_DIR, "population.npy"), population)

    print(f"Saved aligned .npy files to {os.path.abspath(DATA_DIR)}")
    print(f"Grid shape: {brightness_2019.shape}")
    print(f"Brightness 2019 range: {brightness_2019.min():.2f} to {brightness_2019.max():.2f}")
    print(f"Brightness 2024 range: {brightness_2024.min():.2f} to {brightness_2024.max():.2f}")
    print(f"Population range: {population.min():.2f} to {population.max():.2f}")
    print("\nDone. You can now run: python src\\overlay_engine.py")


if __name__ == "__main__":
    try:
        run()
    except RasterioIOError as e:
        print("Error opening one of the GeoTIFF files. Common causes:")
        print("- File is still an .html redirect page, not the actual .tif")
        print("  (this happens if a Drive download link expired/failed)")
        print("- File path is wrong -- double check the exact filename in data\\")
        raise e