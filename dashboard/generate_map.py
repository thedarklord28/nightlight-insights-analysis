import os
import json
import numpy as np
import folium
from folium.plugins import HeatMap
from dashboard_components import (
    get_area_name,
    create_kpi_cards,
    create_distribution_chart,
    create_hotspots_ranking_chart,
    create_quadrant_chart
)

def generate_chennai_dashboard():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    
    score_path = os.path.join(data_dir, "combined_score.npy")
    bounds_path = os.path.join(data_dir, "grid_bounds.json")
    
    if not os.path.exists(score_path):
        print(f"Error: {score_path} not found. Run 'python create_mock_data.py' first.")
        return

    # 1. Load data safely
    raw_score = np.load(score_path)
    clean_score = np.nan_to_num(raw_score, nan=0.0)
    
    # Auto-scale if raw un-normalized values
    min_val, max_val = float(np.min(clean_score)), float(np.max(clean_score))
    if max_val > 1.0 or min_val < 0.0:
        combined_score = (clean_score - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(clean_score)
    else:
        combined_score = clean_score

    rows, cols = combined_score.shape

    if os.path.exists(bounds_path):
        with open(bounds_path, "r") as f:
            bounds = json.load(f)
            min_lat = float(bounds.get("south", 12.80))
            max_lat = float(bounds.get("north", 13.20))
            min_lon = float(bounds.get("west", 80.00))
            max_lon = float(bounds.get("east", 80.35))
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
            lat, lon = float(lat_steps[r]), float(lon_steps[c])
            if score > 0.02:
                heat_data.append([lat, lon, score])
                all_monitored_cells.append({
                    'lat': lat,
                    'lon': lon,
                    'score': score,
                    'area': get_area_name(lat, lon)
                })

    # Sort all monitored cells by score descending
    all_monitored_cells.sort(key=lambda x: x['score'], reverse=True)

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    # 2. Build Folium Map with default Street View & Control=False on overlays
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles=None,
        zoom_control=True
    )

    # Esri Street View Map (Detailed Streets, Roads & Highways) - DEFAULT VISIBLE
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Street Map",
        name="Street Road Network",
        max_zoom=16,
        show=True
    ).add_to(m)

    # Esri Topo Base Layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo Map",
        name="Topographic Detail",
        max_zoom=16,
        show=False
    ).add_to(m)

    # Esri Dark Base Layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Dark Canvas",
        name="Dark Base",
        max_zoom=16,
        show=False
    ).add_to(m)

    # Thermal Satellite Heatmap Spectrum (control=False prevents macro_element!)
    HeatMap(
        heat_data,
        radius=24,
        blur=28,
        min_opacity=0.35,
        gradient={
            0.15: '#0000ff',
            0.35: '#00ffff',
            0.60: '#00ff00',
            0.80: '#ffff00',
            0.98: '#ff0000'
        },
        control=False
    ).add_to(m)

    # Monitored Region Bounding Box (control=False prevents macro_element!)
    folium.Rectangle(
        bounds=[[min_lat, min_lon], [max_lat, max_lon]],
        color="#2563EB",
        weight=1.5,
        dash_array="4, 6",
        fill=False,
        popup="Monitored Chennai Region Bounds",
        control=False
    ).add_to(m)

    # Top Hotspot Pin Markers
    for idx, h in enumerate(all_monitored_cells[:15], 1):
        popup_html = f'''
        <div style="font-family: 'Inter', system-ui, sans-serif; font-size: 12px; color: #0F172A; padding: 4px;">
            <div style="font-weight: 700; color: #2563EB; margin-bottom: 4px;">#{idx} {h['area']}</div>
            <div style="color: #475569; margin-bottom: 2px;">Latitude: {h['lat']:.4f}°N</div>
            <div style="color: #475569; margin-bottom: 4px;">Longitude: {h['lon']:.4f}°E</div>
            <div style="margin-top: 6px;">
                <span style="background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">Intensity Score: {h['score']:.3f}</span>
            </div>
        </div>
        '''
        folium.CircleMarker(
            location=[h['lat'], h['lon']],
            radius=7,
            color="#FFFFFF",
            fill=True,
            fill_color="#FF0000",
            fill_opacity=0.95,
            weight=2,
            popup=folium.Popup(popup_html, max_width=240)
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    # Thermal Legend
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

    # PostMessage listener inside map iframe for smooth flyTo map pan & zoom without browser alerts
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
                    
                    var popup = L.popup()
                        .setLatLng([lat, lon])
                        .setContent('<div style="font-family: system-ui, sans-serif; font-size: 12px; padding: 4px;"><strong style="color: #2563EB;">' + areaName + '</strong><br>Latitude: ' + lat.toFixed(4) + '°N, Longitude: ' + lon.toFixed(4) + '°E<br><span style="background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 6px; border-radius: 4px; font-weight: bold; display: inline-block; margin-top: 4px;">Intensity Score: ' + score.toFixed(3) + '</span></div>')
                        .openOn(mapObj);
                    break;
                }
            }
        }
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(postmessage_js))

    map_html = m._repr_html_()

    # Generate Plotly Components
    kpi_html = create_kpi_cards(combined_score, lat_steps, lon_steps)
    dist_chart_html = create_distribution_chart(combined_score)
    ranking_chart_html = create_hotspots_ranking_chart(combined_score, lat_steps, lon_steps)
    quadrant_chart_html = create_quadrant_chart(combined_score)

    # Hotspots Data Table HTML covering ALL monitored grid cells across Chennai
    table_rows_html = ""
    for idx, h in enumerate(all_monitored_cells, 1):
        status_badge = '<span class="badge-tag tag-red">CRITICAL</span>' if h['score'] >= 0.75 else ('<span class="badge-tag tag-amber">HIGH</span>' if h['score'] >= 0.40 else '<span class="badge-tag tag-blue">MODERATE</span>')
        row_display = "" if idx <= 30 else 'style="display: none;"'
        clean_area = h['area'].replace("'", "\\'").replace('"', '\\"')
        table_rows_html += f'''
        <tr {row_display}>
            <td class="font-medium">{idx}</td>
            <td><strong>{h['area']}</strong></td>
            <td><code>{h['lat']:.4f}°N, {h['lon']:.4f}°E</code></td>
            <td><span class="font-semibold text-primary">{h['score']:.3f}</span></td>
            <td>{status_badge}</td>
            <td><button class="btn-action" onclick="locateZone({h['lat']:.5f}, {h['lon']:.5f}, '{clean_area}', {h['score']:.3f})">Locate on Map</button></td>
        </tr>
        '''

    # Responsive Dashboard HTML Template
    dashboard_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Night-Light Insights Platform | Enterprise Analytics</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Plotly CDN -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    
    <style>
        :root {{
            --bg-body: #F8FAFC;
            --bg-card: #FFFFFF;
            --bg-hover: #F1F5F9;
            --border: #E2E8F0;
            --border-subtle: #F1F5F9;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --text-sub: #94A3B8;
            --primary: #2563EB;
            --primary-light: #EFF6FF;
            --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        }}

        [data-theme="dark"] {{
            --bg-body: #0B0F17;
            --bg-card: #151D2A;
            --bg-hover: #1E293B;
            --border: #232E3F;
            --border-subtle: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --text-sub: #64748B;
            --primary: #3B82F6;
            --primary-light: rgba(59, 130, 246, 0.15);
            --card-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            padding: 24px;
            line-height: 1.5;
        }}

        /* Header Navigation */
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-icon {{
            width: 40px;
            height: 40px;
            background: var(--primary);
            color: #FFFFFF;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .brand-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.3px;
        }}

        .brand-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .nav-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--primary-light);
            color: var(--primary);
            border: 1px solid rgba(37, 99, 235, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}

        .status-dot {{
            width: 6px;
            height: 6px;
            background-color: var(--primary);
            border-radius: 50%;
        }}

        .btn-theme {{
            background: var(--bg-body);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-theme:hover {{
            background: var(--bg-hover);
        }}

        /* KPI Scorecards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: var(--card-shadow);
        }}

        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .kpi-title {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .kpi-icon-box {{
            width: 34px;
            height: 34px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .blue-icon {{ background: #EFF6FF; color: #2563EB; }}
        .amber-icon {{ background: #FFFBEB; color: #D97706; }}
        .emerald-icon {{ background: #ECFDF5; color: #10B981; }}
        .red-icon {{ background: #FEF2F2; color: #EF4444; }}

        [data-theme="dark"] .blue-icon {{ background: rgba(37, 99, 235, 0.15); color: #60A5FA; }}
        [data-theme="dark"] .amber-icon {{ background: rgba(217, 119, 6, 0.15); color: #FBBF24; }}
        [data-theme="dark"] .emerald-icon {{ background: rgba(16, 185, 129, 0.15); color: #34D399; }}
        [data-theme="dark"] .red-icon {{ background: rgba(239, 68, 68, 0.15); color: #F87171; }}

        .kpi-value {{
            font-size: 26px;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }}

        .kpi-footer {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
        }}

        .kpi-subtext {{
            color: var(--text-muted);
        }}

        .badge-pill {{
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}

        .badge-amber {{ background: #FFFBEB; color: #B45309; }}
        .badge-emerald {{ background: #ECFDF5; color: #059669; }}
        .badge-red {{ background: #FEF2F2; color: #DC2626; }}

        [data-theme="dark"] .badge-amber {{ background: rgba(217, 119, 6, 0.2); color: #FCD34D; }}
        [data-theme="dark"] .badge-emerald {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }}
        [data-theme="dark"] .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #FCA5A5; }}

        /* Layout Grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}

        .panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            display: flex;
            flex-direction: column;
        }}

        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .panel-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .panel-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .map-wrapper {{
            height: 520px;
            width: 100%;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
            position: relative;
        }}

        .map-wrapper iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        /* Tabs */
        .tab-bar {{
            display: flex;
            gap: 4px;
            background: var(--bg-body);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
        }}

        .tab-btn {{
            flex: 1;
            padding: 7px 12px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
        }}

        .tab-btn.active {{
            background: var(--bg-card);
            color: var(--primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Table & Global Search */
        .table-responsive {{
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid var(--border);
            -webkit-overflow-scrolling: touch;
            max-height: 520px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
            min-width: 600px;
        }}

        th {{
            background: var(--bg-body);
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-subtle);
            color: var(--text-main);
        }}

        tr:hover td {{
            background: var(--bg-hover);
        }}

        .font-medium {{
            font-weight: 600;
            color: var(--text-muted);
        }}

        .badge-tag {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}

        .tag-red {{ background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; }}
        .tag-amber {{ background: #FFFBEB; color: #D97706; border: 1px solid #FCD34D; }}
        .tag-blue {{ background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }}

        [data-theme="dark"] .tag-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border-color: rgba(239, 68, 68, 0.3); }}
        [data-theme="dark"] .tag-amber {{ background: rgba(217, 119, 6, 0.2); color: #FBBF24; border-color: rgba(217, 119, 6, 0.3); }}
        [data-theme="dark"] .tag-blue {{ background: rgba(37, 99, 235, 0.2); color: #60A5FA; border-color: rgba(37, 99, 235, 0.3); }}

        .btn-action {{
            background: var(--primary-light);
            color: var(--primary);
            border: 1px solid rgba(37, 99, 235, 0.2);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }}

        .btn-action:hover {{
            background: var(--primary);
            color: #FFFFFF;
        }}

        .search-box-container {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-input {{
            background: var(--bg-body);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 14px 8px 34px;
            border-radius: 8px;
            font-size: 13px;
            width: 340px;
            outline: none;
        }}

        .search-input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }}

        .search-icon {{
            position: absolute;
            left: 10px;
            color: var(--text-muted);
            pointer-events: none;
        }}

        /* Responsive Mobile Breakpoints */
        @media (max-width: 1024px) {{
            .dashboard-grid {{ grid-template-columns: 1fr; }}
            .map-wrapper {{ height: 440px; }}
        }}

        @media (max-width: 768px) {{
            body {{ padding: 12px; }}
            .navbar {{ flex-direction: column; align-items: flex-start; gap: 12px; }}
            .nav-actions {{ width: 100%; justify-content: space-between; }}
            .map-wrapper {{ height: 380px; }}
            .search-input {{ width: 100%; }}
            .search-box-container {{ width: 100%; margin-top: 8px; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .panel-header {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
        }}

        @media (max-width: 480px) {{
            .kpi-grid {{ grid-template-columns: 1fr; }}
            .panel {{ padding: 14px; }}
            .brand-title {{ font-size: 16px; }}
        }}
    </style>
</head>
<body>

    <!-- Header Navbar -->
    <div class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg>
            </div>
            <div>
                <h1 class="brand-title">Night-Light Insights Platform</h1>
                <div class="brand-sub">Chennai Spatial Overlay & Population Density Analytics</div>
            </div>
        </div>
        <div class="nav-actions">
            <div class="status-pill">
                <span class="status-dot"></span> Pipeline Active
            </div>
            <button class="btn-theme" onclick="toggleTheme()">
                <svg id="themeIconSvg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                <span id="themeBtnText">Dark Mode</span>
            </button>
        </div>
    </div>

    <!-- Executive KPI Cards -->
    {kpi_html}

    <!-- Main Grid Layout -->
    <div class="dashboard-grid">
        
        <!-- Left Panel: Interactive Thermal Heatmap -->
        <div class="panel" id="mapPanel">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Thermal Night-Light Heatmap</div>
                    <div class="panel-sub">Grid Bounds: {min_lat:.2f}°N - {max_lat:.2f}°N | {min_lon:.2f}°E - {max_lon:.2f}°E</div>
                </div>
            </div>
            <div class="map-wrapper">
                {map_html}
            </div>
        </div>

        <!-- Right Panel: Multi-Tab Analytics -->
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
            </div>

            <!-- Tab 1: Intensity Histogram -->
            <div id="distTab" class="tab-content active">
                {dist_chart_html}
            </div>

            <!-- Tab 2: Top Hotspots Ranking -->
            <div id="rankTab" class="tab-content">
                {ranking_chart_html}
            </div>

            <!-- Tab 3: Sector Breakdown -->
            <div id="sectorTab" class="tab-content">
                {quadrant_chart_html}
            </div>
        </div>

    </div>

    <!-- Bottom Panel: Global Monitored Directory & Real-Time Search -->
    <div class="panel">
        <div class="panel-header">
            <div>
                <div class="panel-title">Geospatial Regional Directory</div>
                <div class="panel-sub">Search and locate any Chennai area across monitored cells</div>
            </div>
            <div class="search-box-container">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" id="globalSearchInput" class="search-input" placeholder="Search Sholinganallur, Velachery, T. Nagar..." onkeyup="filterTable()">
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
                <tbody id="tableBody">
                    {table_rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Interactive Script Engine -->
    <script>
        function toggleTheme() {{
            const html = document.documentElement;
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            
            const btnText = document.getElementById('themeBtnText');
            btnText.textContent = next === 'light' ? 'Dark Mode' : 'Light Mode';
        }}

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
            
            window.dispatchEvent(new Event('resize'));
        }}

        // Real-Time Search Engine filtering ALL monitored cells
        function filterTable() {{
            const input = document.getElementById('globalSearchInput');
            const filter = input.value.trim().toUpperCase();
            const table = document.getElementById('hotspotsTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) {{
                let tdRank = tr[i].getElementsByTagName('td')[0];
                let tdArea = tr[i].getElementsByTagName('td')[1];
                let tdCoords = tr[i].getElementsByTagName('td')[2];
                if (tdArea || tdCoords) {{
                    let txtRank = tdRank ? (tdRank.textContent || tdRank.innerText) : "";
                    let txtArea = tdArea ? (tdArea.textContent || tdArea.innerText) : "";
                    let txtCoords = tdCoords ? (tdCoords.textContent || tdCoords.innerText) : "";
                    
                    if (filter === "") {{
                        tr[i].style.display = i <= 30 ? "" : "none";
                    }} else {{
                        if (txtArea.toUpperCase().indexOf(filter) > -1 || 
                            txtCoords.toUpperCase().indexOf(filter) > -1 ||
                            txtRank.toUpperCase() === filter) {{
                            tr[i].style.display = "";
                        }} else {{
                            tr[i].style.display = "none";
                        }}
                    }}
                }}
            }}
        }}

        // Locate Zone: Pans & Zooms map directly without browser alerts!
        function locateZone(lat, lon, areaName, score) {{
            // 1. Smooth scroll to map panel
            document.getElementById('mapPanel').scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            
            // 2. Send postMessage to Leaflet iframe map to flyTo location
            const iframe = document.querySelector('.map-wrapper iframe');
            if (iframe && iframe.contentWindow) {{
                iframe.contentWindow.postMessage({{
                    action: 'flyTo',
                    lat: lat,
                    lon: lon,
                    areaName: areaName,
                    score: score
                }}, '*');
            }}
        }}
    </script>
</body>
</html>
'''

    output_path = os.path.join(data_dir, "chennai_heatmap.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
        
    print(f"SUCCESS: Dashboard generated at {output_path}")

if __name__ == "__main__":
    generate_chennai_dashboard()