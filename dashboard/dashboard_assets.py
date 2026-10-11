"""CSS and JavaScript for the dashboard page, kept out of generate_map.py so the
big template doesn't need doubled curly braces."""

CSS = """
:root {
    --bg-body: #F8FAFC; --bg-card: #FFFFFF; --bg-hover: #F1F5F9;
    --border: #E2E8F0; --border-subtle: #F1F5F9;
    --text-main: #0F172A; --text-muted: #64748B; --text-sub: #94A3B8;
    --primary: #2563EB; --primary-light: #EFF6FF;
    --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
}
[data-theme="dark"] {
    --bg-body: #0B0F17; --bg-card: #151D2A; --bg-hover: #1E293B;
    --border: #232E3F; --border-subtle: #1E293B;
    --text-main: #F8FAFC; --text-muted: #94A3B8; --text-sub: #64748B;
    --primary: #3B82F6; --primary-light: rgba(59, 130, 246, 0.15);
    --card-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
}
* { box-sizing: border-box; margin: 0; padding: 0;
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease; }
body { background-color: var(--bg-body); color: var(--text-main);
    font-family: 'Inter', system-ui, -apple-system, sans-serif; min-height: 100vh; padding: 24px; line-height: 1.5; }

.navbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
    margin-bottom: 24px; background: var(--bg-card); border: 1px solid var(--border);
    padding: 16px 24px; border-radius: 12px; box-shadow: var(--card-shadow); }
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon { width: 40px; height: 40px; background: var(--primary); color: #FFFFFF; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; }
.brand-title { font-size: 18px; font-weight: 700; color: var(--text-main); letter-spacing: -0.3px; }
.brand-sub { font-size: 12px; color: var(--text-muted); }
.nav-actions { display: flex; align-items: center; gap: 12px; }
.status-pill { display: inline-flex; align-items: center; gap: 6px; background: var(--primary-light);
    color: var(--primary); border: 1px solid rgba(37, 99, 235, 0.2); padding: 6px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 600; }
.status-dot { width: 6px; height: 6px; background-color: var(--primary); border-radius: 50%; }
.btn-theme { background: var(--bg-body); border: 1px solid var(--border); color: var(--text-main);
    padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500;
    display: flex; align-items: center; gap: 8px; }
.btn-theme:hover { background: var(--bg-hover); }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
    padding: 18px 20px; box-shadow: var(--card-shadow); }
.kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.kpi-title { font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.5px; text-transform: uppercase; }
.kpi-icon-box { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.blue-icon { background: #EFF6FF; color: #2563EB; }
.amber-icon { background: #FFFBEB; color: #D97706; }
.emerald-icon { background: #ECFDF5; color: #10B981; }
.red-icon { background: #FEF2F2; color: #EF4444; }
[data-theme="dark"] .blue-icon { background: rgba(37, 99, 235, 0.15); color: #60A5FA; }
[data-theme="dark"] .amber-icon { background: rgba(217, 119, 6, 0.15); color: #FBBF24; }
[data-theme="dark"] .emerald-icon { background: rgba(16, 185, 129, 0.15); color: #34D399; }
[data-theme="dark"] .red-icon { background: rgba(239, 68, 68, 0.15); color: #F87171; }
.kpi-value { font-size: 26px; font-weight: 700; color: var(--text-main); letter-spacing: -0.5px; margin-bottom: 4px; }
.kpi-footer { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.kpi-subtext { color: var(--text-muted); }
.badge-pill { padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.badge-amber { background: #FFFBEB; color: #B45309; }
.badge-emerald { background: #ECFDF5; color: #059669; }
.badge-red { background: #FEF2F2; color: #DC2626; }
[data-theme="dark"] .badge-amber { background: rgba(217, 119, 6, 0.2); color: #FCD34D; }
[data-theme="dark"] .badge-emerald { background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }
[data-theme="dark"] .badge-red { background: rgba(239, 68, 68, 0.2); color: #FCA5A5; }

.dashboard-grid { display: grid; grid-template-columns: 1.6fr 1fr; gap: 20px; margin-bottom: 24px; }
.panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px;
    box-shadow: var(--card-shadow); display: flex; flex-direction: column; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
    padding-bottom: 12px; border-bottom: 1px solid var(--border-subtle); }
.panel-title { font-size: 15px; font-weight: 600; color: var(--text-main); }
.panel-sub { font-size: 12px; color: var(--text-muted); }
.map-wrapper { height: 520px; width: 100%; border-radius: 8px; overflow: hidden;
    border: 1px solid var(--border); position: relative; }
.map-wrapper iframe { width: 100%; height: 100%; border: none; }

.tab-bar { display: flex; gap: 4px; background: var(--bg-body); padding: 4px; border-radius: 8px;
    border: 1px solid var(--border); margin-bottom: 16px; flex-wrap: wrap; }
.tab-btn { flex: 1; min-width: 90px; padding: 7px 10px; background: transparent; border: none;
    color: var(--text-muted); font-size: 11px; font-weight: 600; border-radius: 6px; cursor: pointer; }
.tab-btn.active { background: var(--bg-card); color: var(--primary); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.tab-content { display: none; }
.tab-content.active { display: block; }

.table-responsive { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border);
    -webkit-overflow-scrolling: touch; max-height: 520px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; min-width: 600px; }
th { background: var(--bg-body); color: var(--text-muted); font-weight: 600; padding: 12px 16px;
    border-bottom: 1px solid var(--border); text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;
    position: sticky; top: 0; z-index: 10; }
td { padding: 12px 16px; border-bottom: 1px solid var(--border-subtle); color: var(--text-main); }
tr:hover td { background: var(--bg-hover); }
.font-medium { font-weight: 600; color: var(--text-muted); }
.badge-tag { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-red { background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; }
.tag-amber { background: #FFFBEB; color: #D97706; border: 1px solid #FCD34D; }
.tag-blue { background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }
[data-theme="dark"] .tag-red { background: rgba(239, 68, 68, 0.2); color: #F87171; border-color: rgba(239, 68, 68, 0.3); }
[data-theme="dark"] .tag-amber { background: rgba(217, 119, 6, 0.2); color: #FBBF24; border-color: rgba(217, 119, 6, 0.3); }
[data-theme="dark"] .tag-blue { background: rgba(37, 99, 235, 0.2); color: #60A5FA; border-color: rgba(37, 99, 235, 0.3); }
.btn-action { background: var(--primary-light); color: var(--primary); border: 1px solid rgba(37, 99, 235, 0.2);
    padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; }
.btn-action:hover { background: var(--primary); color: #FFFFFF; }

.search-box-container { position: relative; display: flex; align-items: center; }
.search-input { background: var(--bg-body); border: 1px solid var(--border); color: var(--text-main);
    padding: 8px 14px 8px 34px; border-radius: 8px; font-size: 13px; width: 340px; outline: none; }
.search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
.search-icon { position: absolute; left: 10px; color: var(--text-muted); pointer-events: none; }

@media (max-width: 1024px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .map-wrapper { height: 440px; }
}
@media (max-width: 768px) {
    body { padding: 12px; }
    .navbar { flex-direction: column; align-items: flex-start; gap: 12px; }
    .nav-actions { width: 100%; justify-content: space-between; }
    .map-wrapper { height: 380px; }
    .search-input { width: 100%; }
    .search-box-container { width: 100%; margin-top: 8px; }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    .panel-header { flex-direction: column; align-items: flex-start; gap: 10px; }
}
@media (max-width: 480px) {
    .kpi-grid { grid-template-columns: 1fr; }
    .panel { padding: 14px; }
    .brand-title { font-size: 16px; }
}
"""

JS = """
function toggleTheme() {
    const html = document.documentElement;
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    document.getElementById('themeBtnText').textContent = next === 'light' ? 'Dark Mode' : 'Light Mode';
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    btn.classList.add('active');
    window.dispatchEvent(new Event('resize'));
}

function filterTable() {
    const filter = document.getElementById('globalSearchInput').value.trim().toUpperCase();
    const tr = document.getElementById('hotspotsTable').getElementsByTagName('tr');
    for (let i = 1; i < tr.length; i++) {
        const tds = tr[i].getElementsByTagName('td');
        const txtRank = tds[0] ? tds[0].textContent : '';
        const txtArea = tds[1] ? tds[1].textContent : '';
        const txtCoords = tds[2] ? tds[2].textContent : '';
        if (filter === '') {
            tr[i].style.display = i <= 30 ? '' : 'none';
        } else if (txtArea.toUpperCase().indexOf(filter) > -1 ||
                   txtCoords.toUpperCase().indexOf(filter) > -1 ||
                   txtRank.toUpperCase() === filter) {
            tr[i].style.display = '';
        } else {
            tr[i].style.display = 'none';
        }
    }
}

function locateZone(lat, lon, areaName, score) {
    document.getElementById('mapPanel').scrollIntoView({ behavior: 'smooth', block: 'center' });
    const iframe = document.querySelector('.map-wrapper iframe');
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({ action: 'flyTo', lat: lat, lon: lon, areaName: areaName, score: score }, '*');
    }
}
"""
