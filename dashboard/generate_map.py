import html
import json
import os
import sys

import numpy as np
import folium
from folium.plugins import HeatMap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)

import data_io
from dashboard_assets import CSS, JS
from dashboard_components import (
    configure_area_names,
    save_area_cache,
    uses_name_table,
    coord_label,
    get_area_name,
    create_kpi_cards,
    create_distribution_chart,
    create_hotspots_ranking_chart,
    create_quadrant_chart,
    create_growth_trend_chart,
    create_growth_heatmap,
    create_policing_chart,
    create_demand_forecast_chart,
)

NAMED_CELLS_WHEN_LOOKUP = 40    # non-Chennai cities: only name the top N cells (live lookups are slow)
TABLE_MAX_ROWS = 500            # keep the page light for big grids


def _note(text):
    return f"<p style='color:#64748B;font-size:13px;padding:20px;'>{text}</p>"


def generate_chennai_dashboard():
    """Builds the dashboard for whatever city is currently in data/ (name kept for run_pipeline)."""
    data_dir = data_io.DATA_DIR
    score_path = os.path.join(data_dir, "combined_score.npy")
    bounds_path = os.path.join(data_dir, "grid_bounds.json")
    growth_path = os.path.join(data_dir, "growth_score.npy")
    population_path = os.path.join(data_dir, "population.npy")

    if not os.path.exists(score_path):
        print(f"Error: {score_path} not found. Run 'python run_pipeline.py --mock' (or --city ...) first.")
        return

    meta = data_io.load_meta()
    city = meta["city"]
    city_name = data_io.city_short(city)
    slug = data_io.city_slug(city)
    configure_area_names(city, cache_path=os.path.join(data_dir, f"area_names_{slug}.json"))

    # 1. Load data safely
    clean_score = np.nan_to_num(np.load(score_path), nan=0.0)
    min_val, max_val = float(np.min(clean_score)), float(np.max(clean_score))
    if max_val > 1.0 or min_val < 0.0:
        combined_score = (clean_score - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(clean_score)
    else:
        combined_score = clean_score
    rows, cols = combined_score.shape

    if os.path.exists(bounds_path):
        with open(bounds_path, "r") as f:
            bounds = json.load(f)
        min_lat, max_lat = float(bounds["south"]), float(bounds["north"])
        min_lon, max_lon = float(bounds["west"]), float(bounds["east"])
    else:
        min_lat, max_lat = 12.80, 13.20
        min_lon, max_lon = 80.00, 80.35

    lat_steps = np.linspace(max_lat, min_lat, rows)
    lon_steps = np.linspace(min_lon, max_lon, cols)

    heat_data = []
    all_monitored_cells = []
    for r in range(rows):
        for c in range(cols):
            score = float(combined_score[r, c])
            if score > 0.02:
                lat, lon = float(lat_steps[r]), float(lon_steps[c])
                heat_data.append([lat, lon, score])
                all_monitored_cells.append({'lat': lat, 'lon': lon, 'score': score})

    all_monitored_cells.sort(key=lambda x: x['score'], reverse=True)

    # Name the cells (Chennai: free table lookup for all; other cities: top N via cached lookups)
    for idx, cell in enumerate(all_monitored_cells):
        if uses_name_table() or idx < NAMED_CELLS_WHEN_LOOKUP:
            cell['area'] = get_area_name(cell['lat'], cell['lon'])
        else:
            cell['area'] = coord_label(cell['lat'], cell['lon'])

    # 2. Folium map
    m = folium.Map(location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2], zoom_start=11,
                   tiles=None, zoom_control=True)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Street Map", name="Street Road Network", max_zoom=16, show=True).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo Map", name="Topographic Detail", max_zoom=16, show=False).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Dark Canvas", name="Dark Base", max_zoom=16, show=False).add_to(m)

    HeatMap(heat_data, radius=24, blur=28, min_opacity=0.35,
            gradient={0.15: '#0000ff', 0.35: '#00ffff', 0.60: '#00ff00', 0.80: '#ffff00', 0.98: '#ff0000'},
            control=False).add_to(m)

    folium.Rectangle(bounds=[[min_lat, min_lon], [max_lat, max_lon]], color="#2563EB", weight=1.5,
                     dash_array="4, 6", fill=False, popup=f"Monitored {city_name} Region Bounds",
                     control=False).add_to(m)

    for idx, h in enumerate(all_monitored_cells[:15], 1):
        popup_html = f'''
        <div style="font-family: 'Inter', system-ui, sans-serif; font-size: 12px; color: #0F172A; padding: 4px;">
            <div style="font-weight: 700; color: #2563EB; margin-bottom: 4px;">#{idx} {html.escape(h['area'])}</div>
            <div style="color: #475569; margin-bottom: 2px;">Latitude: {h['lat']:.4f}°N</div>
            <div style="color: #475569; margin-bottom: 4px;">Longitude: {h['lon']:.4f}°E</div>
            <div style="margin-top: 6px;">
                <span style="background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">Intensity Score: {h['score']:.3f}</span>
            </div>
        </div>
        '''
        folium.CircleMarker(location=[h['lat'], h['lon']], radius=7, color="#FFFFFF", fill=True,
                            fill_color="#FF0000", fill_opacity=0.95, weight=2,
                            popup=folium.Popup(popup_html, max_width=240)).add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    legend_html = '''
    <div style="position: absolute; bottom: 24px; left: 20px; z-index: 1000;
                background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(8px);
                border: 1px solid rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px;
                color: #F8FAFC; font-family: 'Inter', system-ui, sans-serif; font-size: 11px; box-shadow: 0 4px 20px rgba(0,0,0,0.25); width: 200px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-weight: 600; color: #F8FAFC;">Thermal Spectrum</span>
            <span style="font-size: 10px; color: #94A3B8;">Intensity</span>
        </div>
        <div style="height: 8px; width: 100%; background: linear-gradient(to right, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000); border-radius: 4px; margin-bottom: 6px;"></div>
        <div style="display: flex; justify-content: space-between; color: #94A3B8; font-size: 10px; font-weight: 500;">
            <span>Low (0.1)</span>
            <span>Med (0.5)</span>
            <span>Max (1.0)</span>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    postmessage_js = '''
    <script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.action === 'flyTo') {
            var lat = event.data.lat;
            var lon = event.data.lon;
            var areaName = event.data.areaName;
            var score = event.data.score;

            for (var key in window) {
                if (key.startsWith('map_') && window[key] && typeof window[key].flyTo === 'function') {
                    var mapObj = window[key];
                    mapObj.flyTo([lat, lon], 14, { duration: 1.2 });

                    var box = document.createElement('div');
                    box.style.cssText = 'font-family: system-ui, sans-serif; font-size: 12px; padding: 4px;';
                    var title = document.createElement('strong');
                    title.style.color = '#2563EB';
                    title.textContent = areaName;
                    box.appendChild(title);
                    box.appendChild(document.createElement('br'));
                    box.appendChild(document.createTextNode('Latitude: ' + lat.toFixed(4) + '°N, Longitude: ' + lon.toFixed(4) + '°E'));
                    box.appendChild(document.createElement('br'));
                    var badge = document.createElement('span');
                    badge.style.cssText = 'background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 6px; border-radius: 4px; font-weight: bold; display: inline-block; margin-top: 4px;';
                    badge.textContent = 'Intensity Score: ' + score.toFixed(3);
                    box.appendChild(badge);

                    L.popup().setLatLng([lat, lon]).setContent(box).openOn(mapObj);
                    break;
                }
            }
        }
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(postmessage_js))
    map_html = m._repr_html_()

    # 3. Plotly components
    kpi_html = create_kpi_cards(combined_score, lat_steps, lon_steps)
    dist_chart_html = create_distribution_chart(combined_score)
    ranking_chart_html = create_hotspots_ranking_chart(combined_score, lat_steps, lon_steps)
    quadrant_chart_html = create_quadrant_chart(combined_score)

    # Year-wise growth trend (every year available)
    try:
        brightness_by_year = data_io.load_all_brightness()
        growth_trend_html = create_growth_trend_chart(brightness_by_year)
        latest_brightness = brightness_by_year[max(brightness_by_year)]
    except FileNotFoundError:
        brightness_by_year, latest_brightness = None, None
        growth_trend_html = _note("brightness_<year>.npy files not found. Run the pipeline first.")

    if os.path.exists(growth_path):
        growth_score = np.load(growth_path)
        growth_heatmap_html = create_growth_heatmap(growth_score, lat_steps, lon_steps)
        demand_forecast_html = create_demand_forecast_chart(growth_score, lat_steps, lon_steps)
    else:
        growth_heatmap_html = demand_forecast_html = _note("growth_score.npy not found. Run the pipeline first.")

    if os.path.exists(population_path) and latest_brightness is not None:
        policing_html = create_policing_chart(np.load(population_path), latest_brightness, lat_steps, lon_steps)
    else:
        policing_html = _note("population.npy / brightness data not found. Run the pipeline first.")

    save_area_cache()

    # 4. Directory table
    table_rows_html = ""
    for idx, h in enumerate(all_monitored_cells[:TABLE_MAX_ROWS], 1):
        status_badge = ('<span class="badge-tag tag-red">CRITICAL</span>' if h['score'] >= 0.75 else
                        ('<span class="badge-tag tag-amber">HIGH</span>' if h['score'] >= 0.40 else
                         '<span class="badge-tag tag-blue">MODERATE</span>'))
        row_display = "" if idx <= 30 else 'style="display: none;"'
        area_js = html.escape(json.dumps(h['area']), quote=True)
        table_rows_html += f'''
        <tr {row_display}>
            <td class="font-medium">{idx}</td>
            <td><strong>{html.escape(h['area'])}</strong></td>
            <td><code>{h['lat']:.4f}°N, {h['lon']:.4f}°E</code></td>
            <td><span class="font-semibold text-primary">{h['score']:.3f}</span></td>
            <td>{status_badge}</td>
            <td><button class="btn-action" onclick="locateZone({h['lat']:.5f}, {h['lon']:.5f}, {area_js}, {h['score']:.3f})">Locate on Map</button></td>
        </tr>
        '''

    if uses_name_table():
        placeholder = "Search Sholinganallur, Velachery, T. Nagar..."
    else:
        placeholder = "Search by area name or coordinates..."

    years = meta["years"]
    year_span = f"{years[0]}\u2013{years[-1]}" if years else ""
    page_title = f"Night-Light Insights Platform | {city_name}"
    brand_sub = f"{html.escape(city_name)} Spatial Overlay &amp; Population Density Analytics {year_span}"

    dashboard_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{html.escape(page_title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>{CSS}</style>
</head>
<body>

    <div class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg>
            </div>
            <div>
                <h1 class="brand-title">Night-Light Insights Platform</h1>
                <div class="brand-sub">{brand_sub}</div>
            </div>
        </div>
        <div class="nav-actions">
            <div class="status-pill"><span class="status-dot"></span> Pipeline Active</div>
            <button class="btn-theme" onclick="toggleTheme()">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                <span id="themeBtnText">Dark Mode</span>
            </button>
        </div>
    </div>

    {kpi_html}

    <div class="dashboard-grid">
        <div class="panel" id="mapPanel">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Thermal Night-Light Heatmap</div>
                    <div class="panel-sub">Grid Bounds: {min_lat:.2f}°N - {max_lat:.2f}°N | {min_lon:.2f}°E - {max_lon:.2f}°E</div>
                </div>
            </div>
            <div class="map-wrapper">{map_html}</div>
        </div>

        <div class="panel">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Geospatial Analytics</div>
                    <div class="panel-sub">Regional data distribution</div>
                </div>
            </div>
            <div class="tab-bar">
                <button class="tab-btn active" onclick="switchTab('distTab', this)">Distribution</button>
                <button class="tab-btn" onclick="switchTab('rankTab', this)">Top Hotspots</button>
                <button class="tab-btn" onclick="switchTab('sectorTab', this)">Sectors</button>
                <button class="tab-btn" onclick="switchTab('growthTab', this)">Growth Trend</button>
                <button class="tab-btn" onclick="switchTab('growthHeatTab', this)">Growth Map</button>
                <button class="tab-btn" onclick="switchTab('policingTab', this)">Policing</button>
                <button class="tab-btn" onclick="switchTab('demandTab', this)">Demand</button>
            </div>
            <div id="distTab" class="tab-content active">{dist_chart_html}</div>
            <div id="rankTab" class="tab-content">{ranking_chart_html}</div>
            <div id="sectorTab" class="tab-content">{quadrant_chart_html}</div>
            <div id="growthTab" class="tab-content">{growth_trend_html}</div>
            <div id="growthHeatTab" class="tab-content">{growth_heatmap_html}</div>
            <div id="policingTab" class="tab-content">{policing_html}</div>
            <div id="demandTab" class="tab-content">{demand_forecast_html}</div>
        </div>
    </div>

    <div class="panel">
        <div class="panel-header">
            <div>
                <div class="panel-title">Geospatial Regional Directory</div>
                <div class="panel-sub">Top {min(len(all_monitored_cells), TABLE_MAX_ROWS)} cells in {html.escape(city_name)} by intensity score</div>
            </div>
            <div class="search-box-container">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" id="globalSearchInput" class="search-input" placeholder="{html.escape(placeholder)}" onkeyup="filterTable()">
            </div>
        </div>
        <div class="table-responsive">
            <table id="hotspotsTable">
                <thead>
                    <tr>
                        <th>Regional Rank</th>
                        <th>Area / Locality Name</th>
                        <th>Coordinates (Lat, Lon)</th>
                        <th>Intensity Score</th>
                        <th>Priority Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="tableBody">{table_rows_html}</tbody>
            </table>
        </div>
    </div>

    <script>{JS}</script>
</body>
</html>
'''

    output_path = os.path.join(data_dir, f"{slug}_heatmap.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print(f"SUCCESS: Dashboard for {city_name} generated at {os.path.abspath(output_path)}")


if __name__ == "__main__":
    generate_chennai_dashboard()
