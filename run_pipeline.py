"""
run_pipeline.py
Runs the entire pipeline end to end in the correct order, in one command.

Usage:
    python run_pipeline.py --mock     # instant, uses fake data
    python run_pipeline.py --real     # uses your downloaded GeoTIFFs in data\

Run this from the project root folder (same level as requirements.txt).
"""

import argparse
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "outputs"))


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


def run(mode):
    if mode == "mock":
        import fetch_data
        step("Fetch mock data", fetch_data.fetch_mock_data)
    else:
        import load_real_data
        step("Load and align real GeoTIFFs", load_real_data.run)

    import overlay_engine
    step("Overlay engine (growth + combined scores)", overlay_engine.run)

    import dev_trend
    step("Output: development trend", dev_trend.run)

    import site_selection
    step("Output: site selection", site_selection.run)

    import policing_priority
    step("Output: policing priority", policing_priority.run)
    # import demand_forecast
    # step("Output: demand forecasting", demand_forecast.run)

    print(f"\n{'=' * 50}")
    print("PIPELINE COMPLETE")
    print("=" * 50)
    print("Check the data\\ folder for .html charts and .npy score files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mock", action="store_true", help="Run with fake/mock data")
    group.add_argument("--real", action="store_true", help="Run with your real downloaded GeoTIFFs")
    args = parser.parse_args()

    run("mock" if args.mock else "real")