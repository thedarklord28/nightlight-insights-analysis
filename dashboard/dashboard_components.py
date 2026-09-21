import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def get_area_name(lat, lon):
    """Micro-locality mapping covering 2,500 grid cells across the Chennai metropolitan region."""
    # 1. OMR IT Corridor (Sholinganallur, Perungudi, Thoraipakkam, Navalur, Siruseri)
    if 12.870 <= lat <= 12.910 and 80.215 <= lon <= 80.255:
        return "Sholinganallur / OMR IT Junction"
    elif 12.910 <= lat <= 12.940 and 80.220 <= lon <= 80.260:
        return "Thoraipakkam / OMR Expressway"
    elif 12.940 <= lat <= 12.970 and 80.230 <= lon <= 80.265:
        return "Perungudi / OMR IT Toll Hub"
    elif 12.820 <= lat <= 12.870 and 80.210 <= lon <= 80.250:
        return "Navalur / Siruseri IT Park"

    # 2. ECR Coastal Belt & Adyar / Besant Nagar
    elif 12.980 <= lat <= 13.010 and 80.245 <= lon <= 80.275:
        return "Adyar / Besant Nagar Beach Zone"
    elif 12.900 <= lat <= 12.980 and 80.250 <= lon <= 80.285:
        return "ECR Coastal Belt / Palavakkam"
    elif 12.800 <= lat <= 12.900 and 80.240 <= lon <= 80.270:
        return "Kovalam / ECR Resort Belt"

    # 3. South Chennai (Velachery, Medavakkam, Madipakkam, Guindy)
    elif 12.965 <= lat <= 12.995 and 80.205 <= lon <= 80.235:
        return "Velachery / Phoenix Marketcity Zone"
    elif 12.930 <= lat <= 12.965 and 80.180 <= lon <= 80.215:
        return "Madipakkam / Keelkattalai Hub"
    elif 12.900 <= lat <= 12.930 and 80.170 <= lon <= 80.210:
        return "Medavakkam / Perumbakkam Corridor"
    elif 12.995 <= lat <= 13.020 and 80.195 <= lon <= 80.230:
        return "Guindy / Industrial Estate Hub"

    # 4. GST Road Corridor (Tambaram, Chromepet, Pallavaram, Airport)
    elif 12.980 <= lat <= 13.005 and 80.155 <= lon <= 80.185:
        return "Chennai Airport / Meenambakkam"
    elif 12.950 <= lat <= 12.980 and 80.145 <= lon <= 80.175:
        return "Pallavaram / GST Road North"
    elif 12.920 <= lat <= 12.950 and 80.135 <= lon <= 80.165:
        return "Chromepet / MIT Campus Zone"
    elif 12.900 <= lat <= 12.920 and 80.115 <= lon <= 80.145:
        return "Tambaram Sanatorium / MEPZ Zone"
    elif 12.870 <= lat <= 12.900 and 80.100 <= lon <= 80.135:
        return "West Tambaram / Mudichur Road"

    # 5. Porur / Valasaravakkam / Poonamallee Corridor
    elif 13.030 <= lat <= 13.050 and 80.150 <= lon <= 80.170:
        return "Porur Junction / Ramachandra Hospital"
    elif 13.025 <= lat <= 13.040 and 80.170 <= lon <= 80.190:
        return "Valasaravakkam / Arcot Road"
    elif 13.015 <= lat <= 13.030 and 80.150 <= lon <= 80.168:
        return "Mugalivakkam / DLF IT Park"
    elif 13.005 <= lat <= 13.020 and 80.168 <= lon <= 80.185:
        return "Manapakkam / L&T Campus"
    elif 13.035 <= lat <= 13.060 and 80.100 <= lon <= 80.145:
        return "Poonamallee / Outer Ring Road Hub"
    elif 13.005 <= lat <= 13.025 and 80.125 <= lon <= 80.150:
        return "Iyyappanthangal / Kanchipuram Hwy"

    # 6. Central Chennai Metro (T. Nagar, Anna Nagar, Nungambakkam, Egmore, Mylapore)
    elif 13.075 <= lat <= 13.095 and 80.200 <= lon <= 80.230:
        return "Anna Nagar West / Tower Park"
    elif 13.075 <= lat <= 13.095 and 80.230 <= lon <= 80.260:
        return "Anna Nagar East / Kilpauk"
    elif 13.060 <= lat <= 13.080 and 80.250 <= lon <= 80.280:
        return "Egmore / Central Railway Hub"
    elif 13.050 <= lat <= 13.075 and 80.230 <= lon <= 80.260:
        return "Nungambakkam / Valluvar Kottam"
    elif 13.030 <= lat <= 13.050 and 80.220 <= lon <= 80.250:
        return "T. Nagar / Pondy Bazaar Commercial Hub"
    elif 13.030 <= lat <= 13.050 and 80.250 <= lon <= 80.280:
        return "Royapettah / Express Avenue Zone"
    elif 13.010 <= lat <= 13.030 and 80.260 <= lon <= 80.285:
        return "Mylapore / Kapaleeshwarar Zone"

    # 7. Ambattur / Avadi / Mogappair Industrial Belt
    elif 13.115 <= lat <= 13.140 and 80.165 <= lon <= 80.190:
        return "Ambattur OT / Industrial Estate"
    elif 13.095 <= lat <= 13.115 and 80.165 <= lon <= 80.190:
        return "Ambattur Industrial Estate South"
    elif 13.095 <= lat <= 13.115 and 80.135 <= lon <= 80.160:
        return "Padi / Lucas TVS Industrial Zone"
    elif 13.080 <= lat <= 13.095 and 80.160 <= lon <= 80.180:
        return "Mogappair West / Golden Flats"
    elif 13.100 <= lat <= 13.130 and 80.080 <= lon <= 80.125:
        return "Avadi / Heavy Vehicles Factory Hub"

    # 8. North Chennai (Royapuram, Port, Ennore, Puzhal, Red Hills)
    elif 13.100 <= lat <= 13.150 and 80.270 <= lon <= 80.310:
        return "Royapuram / Chennai Port Terminal"
    elif 13.070 <= lat <= 13.100 and 80.270 <= lon <= 80.300:
        return "George Town / Parrys Corner"
    elif 13.150 <= lat <= 13.220 and 80.280 <= lon <= 80.330:
        return "Ennore / Thermal Power Port Zone"
    elif 13.140 <= lat <= 13.220 and 80.160 <= lon <= 80.240:
        return "Red Hills / Puzhal Reservoir Zone"

    # 9. West Industrial Belt (Sriperumbudur corridor)
    elif 12.950 <= lat <= 13.020 and 80.000 <= lon <= 80.100:
        return "Sriperumbudur / Industrial Corridor"

    # Fallback descriptors
    elif lat > 13.00 and lon > 80.20:
        return f"Central Metro ({lat:.2f}°N, {lon:.2f}°E)"
    elif lat > 13.00 and lon <= 80.20:
        return f"North-West Sector ({lat:.2f}°N, {lon:.2f}°E)"
    elif lat <= 13.00 and lon > 80.20:
        return f"South-East OMR Corridor ({lat:.2f}°N, {lon:.2f}°E)"
    else:
        return f"South-West GST Corridor ({lat:.2f}°N, {lon:.2f}°E)"

def create_kpi_cards(score_array, lat_steps, lon_steps):
    """Generates clean enterprise metric cards with thermal indicator badges."""
    clean_score = np.nan_to_num(score_array, nan=0.0)

    total_zones = clean_score.size
    high_activity = int(np.sum(clean_score > 0.60))
    pct_high = (high_activity / total_zones) * 100 if total_zones > 0 else 0.0

    valid_scores = clean_score[clean_score > 0.05]
    avg_score = float(np.mean(valid_scores)) if len(valid_scores) > 0 else 0.0

    max_idx = np.argmax(clean_score)
    r, c = np.unravel_index(max_idx, clean_score.shape)
    max_score = float(clean_score[r, c])
    peak_area = get_area_name(lat_steps[r], lon_steps[c])

    # SVG Vector Icons
    icon_grid = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'''
    icon_zap = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'''
    icon_chart = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'''
    icon_flame = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3.5z"/></svg>'''

    cards_html = f'''
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">TOTAL MONITORED ZONES</span>
                <span class="kpi-icon-box blue-icon">{icon_grid}</span>
            </div>
            <div class="kpi-value">{total_zones:,}</div>
            <div class="kpi-footer">
                <span class="kpi-subtext">Grid Resolution: {clean_score.shape[0]} × {clean_score.shape[1]} Cells</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">HIGH DEMAND ZONES (&gt;0.60)</span>
                <span class="kpi-icon-box amber-icon">{icon_zap}</span>
            </div>
            <div class="kpi-value">{high_activity}</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-amber">+{pct_high:.1f}% of regional area</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">AVG INTENSITY SCORE</span>
                <span class="kpi-icon-box emerald-icon">{icon_chart}</span>
            </div>
            <div class="kpi-value">{avg_score:.2f}</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-emerald">Regional baseline index</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">PEAK HOTSPOT SCORE</span>
                <span class="kpi-icon-box red-icon">{icon_flame}</span>
            </div>
            <div class="kpi-value">{max_score:.2f}</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-red">{peak_area}</span>
            </div>
        </div>
    </div>
    '''
    return cards_html

def create_distribution_chart(score_array):
    """Generates a Plotly score distribution histogram with authentic thermal color spectrum."""
    clean_score = np.nan_to_num(score_array, nan=0.0)
    scores = clean_score[clean_score > 0.02].flatten()
    if len(scores) == 0:
        scores = np.array([0.1])

    counts, bin_edges = np.histogram(scores, bins=16)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=bin_centers,
        y=counts,
        marker=dict(
            color=bin_centers,
            colorscale=[
                [0.0, '#2563EB'],
                [0.25, '#06B6D4'],
                [0.50, '#10B981'],
                [0.75, '#F59E0B'],
                [1.0, '#EF4444']
            ],
            line=dict(color='rgba(255,255,255,0.15)', width=0.5)
        ),
        hovertemplate="Score Range: %{x:.2f}<br>Zone Count: %{y}<extra></extra>",
        name="Zones"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=240,
        margin=dict(l=15, r=15, t=15, b=25),
        xaxis=dict(
            title="Intensity Score Threshold",
            showgrid=False,
            zeroline=False,
            color="#64748B",
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Cell Count",
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.15)",
            zeroline=False,
            color="#64748B",
            tickfont=dict(size=10)
        ),
        bargap=0.15,
        showlegend=False
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

def create_hotspots_ranking_chart(score_array, lat_steps, lon_steps):
    """Generates a horizontal bar chart ranking top priority hotspots with fine-grained area names."""
    clean_score = np.nan_to_num(score_array, nan=0.0)
    flat_indices = np.argsort(clean_score.ravel())[::-1][:7]

    top_scores = []
    labels = []

    for idx in flat_indices:
        r, c = np.unravel_index(idx, clean_score.shape)
        score = float(clean_score[r, c])
        lat, lon = float(lat_steps[r]), float(lon_steps[c])
        area_name = get_area_name(lat, lon)
        top_scores.append(score)
        labels.append(area_name)

    top_scores = top_scores[::-1]
    labels = labels[::-1]

    fig = go.Figure(go.Bar(
        x=top_scores,
        y=labels,
        orientation='h',
        marker=dict(
            color=top_scores,
            colorscale=[
                [0.0, '#2563EB'],
                [0.4, '#10B981'],
                [0.7, '#F59E0B'],
                [1.0, '#EF4444']
            ],
            line=dict(color='rgba(255,255,255,0.15)', width=0.5)
        ),
        hovertemplate="Area: %{y}<br>Score: %{x:.3f}<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=240,
        margin=dict(l=170, r=15, t=15, b=25),
        xaxis=dict(
            title="Combined Score",
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.15)",
            zeroline=False,
            range=[0, 1.05],
            color="#64748B"
        ),
        yaxis=dict(
            showgrid=False,
            color="#64748B",
            tickfont=dict(size=10)
        ),
        bargap=0.25
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

def create_quadrant_chart(score_array):
    """Generates a donut chart representing spatial sector breakdown."""
    clean_score = np.nan_to_num(score_array, nan=0.0)
    rows, cols = clean_score.shape
    mid_r, mid_c = rows // 2, cols // 2

    north_east = np.sum(clean_score[:mid_r, mid_c:])
    north_west = np.sum(clean_score[:mid_r, :mid_c])
    south_east = np.sum(clean_score[mid_r:, mid_c:])
    south_west = np.sum(clean_score[mid_r:, :mid_c])

    labels = ['North-East (Port)', 'North-West (Industrial)', 'South-East (OMR IT)', 'South-West (Suburbs)']
    values = [float(north_east), float(north_west), float(south_east), float(south_west)]
    colors = ['#2563EB', '#06B6D4', '#10B981', '#F59E0B']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.2)', width=1)),
        hoverinfo='label+percent+value',
        textinfo='percent',
        textfont=dict(size=10, color='#FFFFFF')
    )])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=9, color="#64748B")
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})


def create_growth_trend_chart(brightness_2019, brightness_2024):
    """Line chart: average brightness change between the two years."""
    clean_2019 = np.nan_to_num(brightness_2019, nan=0.0)
    clean_2024 = np.nan_to_num(brightness_2024, nan=0.0)

    years = [2019, 2024]
    avg = [float(np.mean(clean_2019)), float(np.mean(clean_2024))]
    pct_change = ((avg[1] - avg[0]) / avg[0] * 100) if avg[0] != 0 else 0.0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=avg,
        mode="lines+markers",
        line=dict(width=3, color="#2563EB"),
        marker=dict(size=10, color="#2563EB"),
        fill="tozeroy",
        fillcolor="rgba(37,99,235,0.08)",
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=240,
        margin=dict(l=45, r=15, t=35, b=25),
        title=dict(text=f"Brightness change: {pct_change:+.1f}%", font=dict(size=12, color="#0F172A")),
        xaxis=dict(tickmode="array", tickvals=years, showgrid=False, color="#64748B"),
        yaxis=dict(title="Avg brightness", showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", color="#64748B"),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})


def create_growth_heatmap(growth_score, lat_steps, lon_steps):
    """Spatial heatmap of where brightness increased (red) vs decreased (blue) 2019->2024."""
    clean = np.nan_to_num(growth_score, nan=0.0)
    max_abs = float(np.max(np.abs(clean))) if clean.size else 1.0
    max_abs = max_abs if max_abs > 0 else 1.0

    fig = go.Figure(data=go.Heatmap(
        z=clean,
        x=lon_steps,
        y=lat_steps,
        zmid=0,
        zmin=-max_abs,
        zmax=max_abs,
        colorscale=[[0.0, '#1e3a8a'], [0.5, '#f8fafc'], [1.0, '#dc2626']],
        colorbar=dict(title=dict(text="\u0394 Brightness", font=dict(size=10, color="#64748B")),
                       tickfont=dict(size=9, color="#64748B")),
        hovertemplate="Lat: %{y:.4f}<br>Lon: %{x:.4f}<br>Change: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=280,
        margin=dict(l=45, r=15, t=15, b=30),
        xaxis=dict(title="Longitude", showgrid=False, color="#64748B"),
        yaxis=dict(title="Latitude", showgrid=False, color="#64748B"),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})


def _split_into_zones(grid: np.ndarray, lat_steps=None, lon_steps=None, zone_rows=4, zone_cols=4):
    """Same zone-splitting logic used by site_selection.py / policing_priority.py.
    If lat_steps/lon_steps are given, each zone is labeled with its real
    locality name (via get_area_name) instead of an abstract 'Zone A1' code."""
    h, w = grid.shape
    row_step = max(h // zone_rows, 1)
    col_step = max(w // zone_cols, 1)
    letters = "ABCD"
    zones = {}
    for i in range(zone_rows):
        for j in range(zone_cols):
            r1, r2 = i * row_step, (i + 1) * row_step
            c1, c2 = j * col_step, (j + 1) * col_step
            block = grid[r1:r2, c1:c2]
            if block.size == 0:
                continue

            if lat_steps is not None and lon_steps is not None:
                mid_r = min((r1 + r2) // 2, h - 1)
                mid_c = min((c1 + c2) // 2, w - 1)
                lat, lon = lat_steps[mid_r], lon_steps[mid_c]
                name = get_area_name(lat, lon)
                if name in zones:
                    name = f"{name} ({letters[i]}{j + 1})"
            else:
                name = f"Zone {letters[i]}{j + 1}"

            zones[name] = float(block.mean())
    return zones


def create_policing_chart(population, brightness, lat_steps=None, lon_steps=None, top_n=5):
    """Dual bar chart: under-lit/high-population zones (policing priority)
    vs. over-illuminated/low-population zones (commercial areas)."""
    clean_pop = np.nan_to_num(population, nan=0.0)
    clean_bright = np.nan_to_num(brightness, nan=0.0)

    pop_zones = _split_into_zones(clean_pop, lat_steps, lon_steps)
    bright_zones = _split_into_zones(clean_bright, lat_steps, lon_steps)

    max_pop = max(pop_zones.values()) + 1e-9 if pop_zones else 1.0
    max_bright = max(bright_zones.values()) + 1e-9 if bright_zones else 1.0

    mismatch = {}
    for name in pop_zones:
        pop_norm = pop_zones[name] / max_pop
        bright_norm = bright_zones.get(name, 0.0) / max_bright
        mismatch[name] = pop_norm - bright_norm

    pos_zones = sorted([i for i in mismatch.items() if i[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]
    neg_zones = sorted([i for i in mismatch.items() if i[1] < 0], key=lambda x: x[1])[:top_n]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Under-Lit / Policing Priority", "Over-Illuminated / Commercial"),
    )

    if pos_zones:
        names = [z[0] for z in reversed(pos_zones)]
        vals = [z[1] for z in reversed(pos_zones)]
        fig.add_trace(go.Bar(x=vals, y=names, orientation='h', marker_color='#EF4444', name="Under-lit"), row=1, col=1)

    if neg_zones:
        names = [z[0] for z in reversed(neg_zones)]
        vals = [abs(z[1]) for z in reversed(neg_zones)]
        fig.add_trace(go.Bar(x=vals, y=names, orientation='h', marker_color='#2563EB', name="Over-illuminated"), row=1, col=2)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=10),
        height=260,
        margin=dict(l=10, r=10, t=35, b=25),
        showlegend=False,
    )
    fig.update_annotations(font=dict(size=11, color="#0F172A"))
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", color="#64748B")
    fig.update_yaxes(showgrid=False, color="#64748B", tickfont=dict(size=9))

    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})


def create_demand_forecast_chart(growth_score, lat_steps=None, lon_steps=None, top_n=5):
    """Bar chart of zones ranked by growth score -- highest = fastest-rising demand."""
    clean = np.nan_to_num(growth_score, nan=0.0)
    zones = _split_into_zones(clean, lat_steps, lon_steps)
    ranked = sorted(zones.items(), key=lambda x: x[1], reverse=True)[:top_n]

    names = [r[0] for r in reversed(ranked)]
    vals = [r[1] for r in reversed(ranked)]

    fig = go.Figure(go.Bar(
        x=vals, y=names,
        orientation='h',
        marker=dict(
            color=vals,
            colorscale=[[0.0, '#D1FAE5'], [1.0, '#10B981']],
            line=dict(color='rgba(255,255,255,0.15)', width=0.5),
        ),
        hovertemplate="%{y}<br>Growth: %{x:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748B", family="Inter, system-ui, sans-serif", size=11),
        height=240,
        margin=dict(l=170, r=15, t=15, b=25),
        xaxis=dict(title="Growth score (2019 to 2024)", showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", color="#64748B"),
        yaxis=dict(showgrid=False, color="#64748B", tickfont=dict(size=10)),
        bargap=0.25,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})