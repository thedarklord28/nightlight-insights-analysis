"""
fetch_city.py
Pulls real data for ANY city straight from Google Earth Engine -- no Drive
export, no manual downloads. One call gets every year of night-light data
plus a population layer, all on the same pixel grid.

Usage (run from the project root, venv active):
    python src\\fetch_city.py --city "Mumbai, India"
    python src\\fetch_city.py --city "Chennai, India" --start 2016 --end 2024
    python src\\fetch_city.py --city "Chennai, India" --lat 13.0827 --lon 80.2707

--lat/--lon skip the geocoding step (use them if the geocoder is down or
returns the wrong place).
"""

import argparse
import io
import json
import math
import os
import sys
import urllib.request
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_io
from align import align_grids

DATA_DIR = data_io.DATA_DIR

VIIRS_ID = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG"        # monthly night-light radiance, 2014 onward
GPW_ID = "CIESIN/GPWv411/GPW_Population_Density"      # people per km2, years 2000/05/10/15/20
GPW_YEAR = 2020
SCALE_M = 500
MIN_YEAR = 2014
MAX_RADIUS_KM = 40


# ---------------------------------------------------------------- location
def geocode_city(query):
    """City name -> (lat, lon, address) using OpenStreetMap's free Nominatim service."""
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="nightlight-insights-student-project")
        loc = geolocator.geocode(query, exactly_one=True, timeout=15)
    except Exception as e:
        raise RuntimeError(
            f"Could not geocode '{query}' ({e}).\n"
            "Pass the coordinates yourself instead, e.g.  --lat 13.0827 --lon 80.2707"
        )
    if loc is None:
        raise RuntimeError(
            f"No place found for '{query}'. Try 'City, Country' or pass --lat/--lon."
        )
    return loc.latitude, loc.longitude, loc.address


def bbox_from_center(lat, lon, radius_km):
    """Square box around a point -> (west, south, east, north) in degrees."""
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.1))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


# ----------------------------------------------------------- Earth Engine
PROJECT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ee_project.txt")


def _saved_project():
    """Project id from the EE_PROJECT environment variable or ee_project.txt (project root)."""
    env = os.environ.get("EE_PROJECT") or os.environ.get("EARTHENGINE_PROJECT")
    if env:
        return env.strip()
    if os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE) as f:
            return f.read().strip() or None
    return None


def init_ee(project=None):
    import ee
    explicit = project
    project = project or _saved_project()
    try:
        ee.Initialize(project=project) if project else ee.Initialize()
    except Exception as e:
        if "no project" in str(e).lower():
            raise RuntimeError(
                "Earth Engine needs your Google Cloud project ID.\n"
                "  Find it: console.cloud.google.com -> project picker (top bar) -> copy the ID column\n"
                "  (the ID, e.g. nightlight-insights-123456, not the display name).\n"
                "  Then run once:  python run_pipeline.py --city \"Chennai, India\" --project YOUR_ID\n"
                "  It is remembered afterwards (saved in ee_project.txt)."
            )
        raise RuntimeError(
            f"Earth Engine could not start ({e}).\n"
            'If it is a login problem run:  python -c "import ee; ee.Authenticate()"  and retry.\n'
            "If it says the project is not registered / the API is not enabled, use the project you "
            "registered for Earth Engine (--project YOUR_ID)."
        )
    if explicit:                       # worked -> remember it for next time
        with open(PROJECT_FILE, "w") as f:
            f.write(explicit)
    return ee


def _download_url(image, region):
    params = {"region": region, "scale": SCALE_M, "crs": "EPSG:4326", "format": "GEO_TIFF"}
    try:
        return image.getDownloadURL(params)
    except Exception:
        params["region"] = region.toGeoJSONString()
        return image.getDownloadURL(params)


def _save_download(url, out_path):
    with urllib.request.urlopen(url, timeout=180) as resp:
        data = resp.read()

    if data[:2] == b"PK":                                  # zipped GeoTIFF
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            tif_names = [n for n in zf.namelist() if n.lower().endswith(".tif")]
            if not tif_names:
                raise RuntimeError("Earth Engine returned a zip with no .tif inside.")
            data = zf.read(tif_names[0])
    elif data[:4] not in (b"II*\x00", b"MM\x00*"):          # not a TIFF -> probably an error message
        raise RuntimeError(f"Earth Engine did not return a GeoTIFF: {data[:200]!r}")

    with open(out_path, "wb") as f:
        f.write(data)


def fetch_year_tif(ee, region, year, out_path):
    """Median of the 12 monthly composites for `year`. Returns False if no data exists."""
    collection = (
        ee.ImageCollection(VIIRS_ID)
        .filterDate(f"{year}-01-01", f"{year + 1}-01-01")
        .select("avg_rad")
    )
    if collection.size().getInfo() == 0:
        return False
    _save_download(_download_url(collection.median(), region), out_path)
    return True


def fetch_population_tif(ee, region, out_path):
    """Latest GPW population density, resampled onto the same 500 m grid."""
    image = (
        ee.ImageCollection(GPW_ID)
        .filterDate(f"{GPW_YEAR}-01-01", f"{GPW_YEAR + 1}-01-01")
        .first()
        .select("population_density")
        .resample("bilinear")
    )
    _save_download(_download_url(image, region), out_path)


# ------------------------------------------------------------- processing
class _Bounds:
    """Minimal stand-in for rasterio's bounding box."""
    def __init__(self, left, bottom, right, top):
        self.left, self.bottom, self.right, self.top = left, bottom, right, top


def _read_with_rasterio(path):
    import rasterio
    with rasterio.open(path) as src:
        return src.read(1).astype("float64"), src.nodata, _Bounds(*src.bounds)


def _read_with_tifffile(path, fallback_bounds):
    """Pure-Python reader (no DLLs), used when rasterio is blocked or not installed."""
    try:
        import tifffile
    except ImportError:
        raise RuntimeError(
            "Cannot read the downloaded GeoTIFFs: rasterio is blocked by Windows and tifffile is not installed.\n"
            "Fix: pip install tifffile   (then re-run the same command)"
        )
    try:
        with tifffile.TiffFile(path) as tif:
            page = tif.pages[0]
            arr = np.asarray(page.asarray(), dtype="float64")
            meta = tif.geotiff_metadata or {}
            nodata_tag = page.tags.get(42113)          # GDAL_NODATA
            nodata = float(nodata_tag.value) if nodata_tag is not None else None
    except Exception as e:
        raise RuntimeError(
            f"tifffile could not read {os.path.basename(path)} ({e}).\n"
            "Try: pip install imagecodecs   or run from your old venv where rasterio works."
        )

    if arr.ndim == 3:
        arr = arr[0] if arr.shape[0] == 1 else arr[..., 0]
    h, w = arr.shape

    scale, tie = meta.get("ModelPixelScale"), meta.get("ModelTiepoint")
    if scale and tie:
        i, j, _, x, y = tie[:5]
        left = x - i * scale[0]
        top = y + j * scale[1]
        bounds = _Bounds(left, top - h * scale[1], left + w * scale[0], top)
    elif fallback_bounds:
        west, south, east, north = fallback_bounds
        bounds = _Bounds(west, south, east, north)
    else:
        raise RuntimeError(f"No georeferencing found in {os.path.basename(path)}.")
    return arr, nodata, bounds


def read_band(path, fallback_bounds=None):
    try:
        arr, nodata, bounds = _read_with_rasterio(path)
    except ImportError:                      # e.g. "DLL load failed ... Application Control policy"
        arr, nodata, bounds = _read_with_tifffile(path, fallback_bounds)
    if nodata is not None:
        arr = np.where(arr == nodata, 0, arr)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(arr, 0, None), bounds


def tifs_to_npy(tif_by_year, pop_tif, fallback_bounds=None):
    """GeoTIFFs -> the .npy files + grid_bounds.json the rest of the pipeline reads."""
    data_io.clear_brightness_files()

    years = sorted(tif_by_year)
    grids, bounds = {}, None
    for y in years:
        grids[y], b = read_band(tif_by_year[y], fallback_bounds)
        bounds = bounds or b
    shapes = {g.shape for g in grids.values()}
    if len(shapes) != 1:
        raise RuntimeError(f"Yearly grids have different shapes: {shapes}")

    population, _ = read_band(pop_tif, fallback_bounds)
    ref = grids[years[0]]
    if population.shape != ref.shape:
        _, population = align_grids(ref, population)

    if all(g.max() == 0 for g in grids.values()):
        raise RuntimeError("Every brightness grid is all zeros -- check the location and Earth Engine access.")

    for y in years:
        np.save(data_io.brightness_path(y), grids[y])
    np.save(os.path.join(DATA_DIR, "population.npy"), population)

    with open(os.path.join(DATA_DIR, "grid_bounds.json"), "w") as f:
        json.dump({
            "west": bounds.left, "south": bounds.bottom, "east": bounds.right, "north": bounds.top,
            "height": ref.shape[0], "width": ref.shape[1],
        }, f, indent=2)
    return grids, population


# ------------------------------------------------------------------- main
def run(city, start=2019, end=2024, radius_km=20, project=None, lat=None, lon=None):
    if start > end:
        raise ValueError("--start must be <= --end")
    if start < MIN_YEAR:
        raise ValueError(f"VIIRS monthly data only starts in {MIN_YEAR}; use --start {MIN_YEAR} or later.")
    radius_km = min(radius_km, MAX_RADIUS_KM)
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. where is it?
    if lat is None or lon is None:
        print(f"Looking up '{city}'...")
        lat, lon, address = geocode_city(city)
        print(f"  found: {address}")
    else:
        address = "(coordinates given manually)"
    west, south, east, north = bbox_from_center(lat, lon, radius_km)
    print(f"  centre {lat:.4f}, {lon:.4f}  |  box {radius_km} km each way")

    # 2. download every year + population
    ee = init_ee(project)
    region = ee.Geometry.Rectangle([west, south, east, north])

    tif_by_year = {}
    for year in range(start, end + 1):
        path = os.path.join(DATA_DIR, f"brightness_{year}.tif")
        print(f"  [{year}] downloading night-light data...", end=" ", flush=True)
        if fetch_year_tif(ee, region, year, path):
            tif_by_year[year] = path
            print("ok")
        else:
            print("no data for this year, skipped")
    if len(tif_by_year) < 2:
        raise RuntimeError("Need at least two years of data. Try a different --start/--end.")

    pop_tif = os.path.join(DATA_DIR, "population.tif")
    print(f"  [population] downloading GPW {GPW_YEAR} density...", end=" ", flush=True)
    fetch_population_tif(ee, region, pop_tif)
    print("ok")

    # 3. convert to the arrays the pipeline uses
    grids, _ = tifs_to_npy(tif_by_year, pop_tif, (west, south, east, north))
    years = sorted(grids)
    data_io.save_meta(city, years, "real", lat=lat, lon=lon, radius_km=radius_km, address=address)

    ref = grids[years[0]]
    print(f"\nSaved {len(years)} years ({years[0]}-{years[-1]}), grid {ref.shape[0]} x {ref.shape[1]}")
    for y in years:
        print(f"  {y}: mean brightness {grids[y].mean():.2f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--city", required=True, help='e.g. "Mumbai, India"')
    p.add_argument("--start", type=int, default=2019)
    p.add_argument("--end", type=int, default=2024)
    p.add_argument("--radius-km", type=float, default=20)
    p.add_argument("--project", default=None, help="Google Cloud project id (only if Earth Engine asks)")
    p.add_argument("--lat", type=float, default=None)
    p.add_argument("--lon", type=float, default=None)
    a = p.parse_args()
    run(a.city, a.start, a.end, a.radius_km, a.project, a.lat, a.lon)