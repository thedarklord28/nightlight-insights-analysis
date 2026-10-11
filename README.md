# Night-Light Insights Platform

Turns satellite night-light data and population density into practical
insights for any city: where to open a business, which areas are under-lit
relative to how many people live there, where activity is rising fastest, and
how a city has developed year by year. Everything is shown on one interactive
dashboard.

## How it works

```
Earth Engine (VIIRS night-lights, every year + GPW population)
        |
   fetch_city.py  ->  one grid per year + population grid (same pixel grid)
        |
   overlay_engine.py  ->  growth_score and combined_score
        |
   +-- dev_trend.py          year-by-year brightness trend
   +-- site_selection.py     best zones for a new business
   +-- policing_priority.py  under-lit vs over-illuminated zones
   +-- demand_forecast.py    fastest-rising zones
        |
   dashboard/generate_map.py  ->  <city>_heatmap.html
```

**Scores**
- `growth_score` = brightness in the last year minus the first year (per cell)
- `combined_score` = 0.6 x normalised latest brightness + 0.4 x normalised population

**Data sources (both free, via Google Earth Engine)**
- Night lights: NOAA VIIRS monthly composites (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG`, band `avg_rad`). Each year is the median of that year's monthly images, sampled at 500 m.
- Population: CIESIN GPW v4.11 population density, 2020 (`CIESIN/GPWv411/GPW_Population_Density`).

## Setup (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create the venv once; activate it every time you open a new terminal.

Earth Engine (only needed for real data):
1. Register for free at https://earthengine.google.com/signup (non-commercial / academic).
2. `python -c "import ee; ee.Authenticate()"`
3. Find your Google Cloud **project ID** (console.cloud.google.com, project picker, the ID column) and run once with `--project YOUR_ID`. It is remembered afterwards in `ee_project.txt`.

## Running it (from the project root)

| Command | What it does |
|---|---|
| `python run_pipeline.py --mock` | Fake data, instant, works offline. Use this to test your setup. |
| `python run_pipeline.py --city "Chennai, India" --start 2019 --end 2024` | Real data for any city. |
| `python run_pipeline.py --city "Mumbai, India" --radius-km 25` | Another city, wider window. |
| `python run_pipeline.py --use-existing` | Skip fetching, re-run everything on the data already in `data\`. |
| `python run_pipeline.py --real` | Old flow: GeoTIFFs downloaded by hand into `data\`. |

Useful options: `--lat 13.08 --lon 80.27` (skip the city lookup), `--project ID`.

Then open `data\<city>_heatmap.html` in a browser (for example `data\chennai_heatmap.html`).
Each city gets its own file, so you can generate several and open them later.

## What you get (in `data\`)

| File | Contents |
|---|---|
| `<city>_heatmap.html` | The dashboard: map, KPI cards, 7 analytics tabs, searchable directory |
| `dev_trend.html` | Average brightness per year with year-on-year % change |
| `site_selection.html` | Top zones for a new business (with coordinates and Google Maps links in the terminal) |
| `policing_priority.html` | Under-lit (high population, low light) vs over-illuminated zones |
| `demand_forecast.html` | Zones ranked by growth |
| `brightness_<year>.npy`, `population.npy`, `growth_score.npy`, `combined_score.npy` | The grids |
| `grid_bounds.json`, `meta.json` | Real lat/lon edges of the grid; city and years |

The dashboard needs an internet connection (map tiles, fonts and Plotly load online).

## Study area

The analysis window is a square centred on the city, `--radius-km` in each
direction (default 20, so 40 x 40 km). It is deliberately **not** the municipal
boundary: night-light activity does not stop at administrative limits, and a
fixed window processes every city the same way. Cells over sea or empty land
simply have no light.

## Area names on the dashboard

- Chennai uses a hand-built locality table.
- Any other city is reverse-geocoded from OpenStreetMap for the top cells and
  zones, then cached in `data\area_names_<city>.json`. The first run for a new
  city takes about a minute longer; later runs are instant. If lookups fail,
  coordinates are shown instead.

## Project layout

```
run_pipeline.py            one-command runner (checks the file layout first)
requirements.txt
src/
  data_io.py               shared helpers: finding files, city/years metadata
  fetch_city.py            real data for any city from Earth Engine
  fetch_data.py            mock data generator
  align.py                 grid alignment safety net
  overlay_engine.py        growth_score + combined_score
  outputs/
    dev_trend.py  site_selection.py  policing_priority.py  demand_forecast.py
dashboard/
  generate_map.py          builds the dashboard page
  dashboard_components.py  charts, KPI cards, area naming
  dashboard_assets.py      page CSS and JavaScript
data/                      generated files (not committed)
```

## Limitations

- Population is a single 2020 snapshot (GPW updates every 5 years), so it is
  combined with the latest night-light year.
- Daytime mobile-density data is not used; population stands in as the
  daytime activity proxy.
- Night-light resolution is about 500 m and zones are a coarse 4 x 4 split.
- Scores are relative within one study window. Changing the radius changes the
  normalisation, and scores should not be compared between cities.
- "Policing priority" is a lighting-versus-population signal for prioritising
  patrol and street-lighting attention. It is not crime prediction.
- Growth compares the first and last year only; the trend chart shows every
  year in between.

## Troubleshooting

| Problem | Fix |
|---|---|
| `run_pipeline.py` stops with "X.py is missing / must be in ..." | A file is missing, misnamed (e.g. `site_selection (1).py`) or in the wrong folder. Follow the message. |
| `No module named ...` | The venv is not active (`venv\Scripts\activate`) or `pip install -r requirements.txt` was not run. |
| Earth Engine: "no project found" | Run once with `--project YOUR_PROJECT_ID`. |
| Earth Engine login errors | `python -c "import ee; ee.Authenticate()"` |
| City lookup fails | Pass `--lat` and `--lon` yourself. |
| `DLL load failed ... Application Control policy` | Windows is blocking a compiled package. Plotly is used instead of matplotlib for this reason, and GeoTIFFs fall back to the pure-Python `tifffile` reader if rasterio is blocked. |
| Dashboard map is blank | Needs internet for map tiles; check your connection. |
