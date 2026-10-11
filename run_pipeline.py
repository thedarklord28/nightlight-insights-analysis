"""
run_pipeline.py
Runs the whole project in one command.

DATA STEP (pick one):
    python run_pipeline.py --mock                         fake data, instant, works offline
    python run_pipeline.py --city "Mumbai, India"         REAL data for any city (needs Earth Engine login)
    python run_pipeline.py --city "Chennai, India" --start 2016 --end 2024 --radius-km 25
    python run_pipeline.py --use-existing                 skip fetching, re-run on whatever is in data\\
    python run_pipeline.py --real                         old flow: convert GeoTIFFs you downloaded by hand

Everything after the data step (scores, charts, dashboard) is identical for all of them.
Run from the project root folder (same level as requirements.txt).
"""

import argparse
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "src", "outputs"))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

# ---------------------------------------------------------------------------
# Layout check: every file the pipeline needs, and the folder it belongs in.
# Finds misplaced / misnamed copies (e.g. "site_selection (1).py") and says so.
# ---------------------------------------------------------------------------
OUT = os.path.join("src", "outputs")
EXPECTED = [
    ("data_io", "src"), ("fetch_data", "src"), ("fetch_city", "src"), ("align", "src"),
    ("overlay_engine", "src"),
    ("dev_trend", OUT), ("site_selection", OUT), ("policing_priority", OUT), ("demand_forecast", OUT),
    ("generate_map", "dashboard"), ("dashboard_components", "dashboard"), ("dashboard_assets", "dashboard"),
]
SKIP_DIRS = {"venv", ".venv", "env", "data", "__pycache__", "node_modules"}


def _search(name):
    exact, similar = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            low = f.lower()
            if low == name + ".py":
                exact.append(dirpath)
            elif low.startswith(name) and ".py" in low:
                similar.append(os.path.join(dirpath, f))
    return exact, similar


def preflight(extra=()):
    problems = []
    for name, rel in list(EXPECTED) + list(extra):
        if os.path.isfile(os.path.join(ROOT, rel, name + ".py")):
            continue
        exact, similar = _search(name)
        if exact:
            problems.append(f"  {name}.py is in {os.path.relpath(exact[0], ROOT)}\\ but must be in {rel}\\ -> move it there")
        elif similar:
            found = ", ".join(os.path.relpath(p, ROOT) for p in similar)
            problems.append(f"  {name}.py is missing, but found: {found}\n"
                            f"      -> rename it to exactly {name}.py and put it in {rel}\\")
        else:
            problems.append(f"  {name}.py is missing -> put it in {rel}\\")

    if problems:
        print(f"Project folder: {ROOT}\n")
        print("Cannot start. Fix these first:")
        print("\n".join(problems))
        for rel in ("src", OUT, "dashboard"):
            full = os.path.join(ROOT, rel)
            names = sorted(os.listdir(full)) if os.path.isdir(full) else "(folder does not exist)"
            print(f"\nWhat is actually in {rel}\\ : {names}")
        sys.exit(1)


def step(name, fn):
    print(f"\n{'=' * 50}")
    print(f"STEP: {name}")
    print("=" * 50)
    try:
        fn()
        print(f"[OK] {name} finished")
    except Exception:
        print(f"[FAILED] {name}")
        traceback.print_exc()
        print(f"\nPipeline stopped at: {name}")
        sys.exit(1)


def _legacy_tif_flow():
    import data_io
    import load_real_data
    data_io.clear_brightness_files()      # never mix with years left over from another run
    load_real_data.run()
    data_io.save_meta("Chennai, India", [2019, 2024], "manual-geotiff")


def run(args):
    if args.mock:
        import fetch_data
        step("Fetch mock data (multi-year)", fetch_data.fetch_mock_data)
    elif args.city:
        import fetch_city
        step(f"Fetch real data for {args.city}", lambda: fetch_city.run(
            args.city, args.start, args.end, args.radius_km, args.project, args.lat, args.lon))
    elif args.real:
        step("Load and align hand-downloaded GeoTIFFs", _legacy_tif_flow)
    else:
        print("Skipping data step (--use-existing): using whatever is already in data\\")

    import overlay_engine
    step("Overlay engine (growth + combined scores)", overlay_engine.run)

    import dev_trend
    step("Output: development trend (year by year)", dev_trend.run)

    import site_selection
    step("Output: site selection", site_selection.run)

    import policing_priority
    step("Output: policing priority", policing_priority.run)

    import demand_forecast
    step("Output: demand forecasting", demand_forecast.run)

    import generate_map
    step("Dashboard", generate_map.generate_chennai_dashboard)

    import data_io
    meta = data_io.load_meta()
    print(f"\n{'=' * 50}")
    print("PIPELINE COMPLETE")
    print("=" * 50)
    print(f"City: {meta['city']}  |  years: {meta['first_year']}-{meta['last_year']}")
    print(f"Open data\\{data_io.city_slug(meta['city'])}_heatmap.html in your browser.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Night-Light Insights pipeline")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--mock", action="store_true", help="fake data, no internet")
    g.add_argument("--city", type=str, help='real data for any city, e.g. "Mumbai, India"')
    g.add_argument("--use-existing", action="store_true", help="re-run analysis on the data already in data\\")
    g.add_argument("--real", action="store_true", help="old flow: GeoTIFFs downloaded by hand")
    p.add_argument("--start", type=int, default=2019, help="first year (with --city)")
    p.add_argument("--end", type=int, default=2024, help="last year (with --city)")
    p.add_argument("--radius-km", type=float, default=20, help="half-width of the area around the city centre")
    p.add_argument("--project", default=None, help="Google Cloud project id, only if Earth Engine asks for it")
    p.add_argument("--lat", type=float, default=None, help="skip geocoding: city centre latitude")
    p.add_argument("--lon", type=float, default=None, help="skip geocoding: city centre longitude")
    args = p.parse_args()
    preflight(extra=[("load_real_data", "src")] if args.real else [])
    run(args)