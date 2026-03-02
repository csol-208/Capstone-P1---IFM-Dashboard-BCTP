/* =====================================================================
   IFM Dashboard – fully client-side, no server needed
   Loads ifm_data.json then does all filtering / aggregation in-browser
   ===================================================================== */

// ── Palette & Plotly defaults ──────────────────────────────────────────
const COLORS = ['#1a4d7e','#2166a0','#4a90cb','#2ba084','#c9a031','#d97f6d','#6b8cba','#a8d5c3'];

const BASE_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor:  'rgba(248,249,250,0.5)',
  font: { family: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif", size: 12 },
  colorway: COLORS,
};
const CFG = { responsive: true, displayModeBar: false };

// Column name constants (must match the JSON keys produced by convert_data.py)
const COL_ISSUED    = 'Total Credits \nIssued';
const COL_RETIRED   = 'Total Credits \nRetired';
const COL_REMAINING = 'Total Credits Remaining';
const VINTAGE_YEARS = Array.from({ length: 30 }, (_, i) => String(1996 + i));

const COUNTRY_COORDS = {
  'United States':[37.09,-95.71],'Canada':[56.13,-106.35],'Brazil':[-14.24,-51.93],
  'Australia':[-25.27,133.78],'Mexico':[23.63,-102.55],'Indonesia':[-0.79,113.92],
  'Malaysia':[4.21,101.70],'Peru':[-9.19,-75.02],'Colombia':[4.57,-74.30],
  'Russia':[61.52,105.32],'China':[35.86,104.20],'Vietnam':[14.06,108.28],
  'Thailand':[15.87,100.99],'Philippines':[12.88,121.77],'Papua New Guinea':[-6.32,143.96],
  'Chile':[-35.68,-71.54],'Argentina':[-38.42,-63.62],'Bolivia':[-16.29,-63.59],
  'Ecuador':[-1.83,-78.18],'Ghana':[7.37,-5.36],'Kenya':[-0.02,37.91],
  'Democratic Republic of Congo':[-4.04,21.76],'Cameroon':[3.85,11.50],
  'Uganda':[1.37,32.29],'Laos':[19.85,102.50],'Myanmar':[21.92,95.96],
  'Zambia':[-13.13,27.85],'Zimbabwe':[-19.02,29.15],'Mozambique':[-18.67,35.53],
  'Turkey':[38.96,35.24],'Congo':[-0.65,15.55],'Central African Republic':[6.61,20.94],
  'Tanzania':[-6.37,34.89],'South Africa':[-30.56,22.94],'Nicaragua':[12.87,-85.21],
  'Costa Rica':[9.75,-83.75],'Panama':[8.78,-80.77],'Honduras':[15.20,-86.24],
  'Guatemala':[15.78,-90.23],'El Salvador':[13.79,-88.90],'Dominican Republic':[18.74,-70.16],
  'Haiti':[18.97,-72.29],
};

// ── App state ──────────────────────────────────────────────────────────
let ALL_DATA = null;
let state = {
  registries: [],
  countries: [],
  statuses: [],
  searchQuery: '',
  page: 1,
  pageSize: 50,
};
let searchTimer = null;

// ── Bootstrap ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadData();
});

async function loadData() {
  showGlobalLoader(true);
  try {
    const res = await fetch('ifm_data.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    ALL_DATA = await res.json();
    onDataReady();
  } catch (err) {
    document.getElementById('globalLoader').innerHTML =
      '<p style="color:#c0392b;font-size:1.1rem;padding:40px 24px;">' +
      '⚠️ Could not load <code>ifm_data.json</code>.<br><br>' +
      'Run <code>python convert_data.py</code> (in the <code>js_app/</code> folder) to generate it, ' +
      'then place <code>ifm_data.json</code> in the same folder as <code>index.html</code>.</p>';
    console.error(err);
  }
}

function onDataReady() {
  showGlobalLoader(false);
  populateFilterSelects();
  renderAll();
}

function showGlobalLoader(show) {
  document.getElementById('globalLoader').style.display = show ? 'flex' : 'none';
  document.getElementById('mainContent').style.display  = show ? 'none' : 'block';
}

// ── Filtering ─────────────────────────────────────────────────────────
function getFiltered() {
  let d = ALL_DATA;
  if (state.registries.length) d = d.filter(r => state.registries.includes(r['Voluntary Registry']));
  if (state.countries.length)  d = d.filter(r => state.countries.includes(r['Country']));
  if (state.statuses.length)   d = d.filter(r => state.statuses.includes(r['Voluntary Status']));
  return d;
}

function populateFilterSelects() {
  const uniq = (key) => [...new Set(ALL_DATA.map(r => r[key]).filter(Boolean))].sort();
  fillSelect('regSelect',     uniq('Voluntary Registry'));
  fillSelect('countrySelect', uniq('Country'));
  fillSelect('statusSelect',  uniq('Voluntary Status'));
  document.getElementById('heroDesc').textContent =
    'Explore ' + ALL_DATA.length.toLocaleString() +
    ' verified forest management projects worldwide protecting millions of trees and storing carbon';
}

function fillSelect(id, items) {
  const sel = document.getElementById(id);
  sel.innerHTML = items.map(v => '<option value="' + esc(v) + '">' + esc(v) + '</option>').join('');
}

// ── Filter controls ───────────────────────────────────────────────────
function clearSelect(id) {
  [...document.getElementById(id).options].forEach(o => o.selected = false);
}

function resetFilters() {
  clearSelect('regSelect'); clearSelect('countrySelect'); clearSelect('statusSelect');
  state.registries = []; state.countries = []; state.statuses = [];
  state.page = 1;
  renderAll();
}

function applyFilters() {
  state.registries = getSelected('regSelect');
  state.countries  = getSelected('countrySelect');
  state.statuses   = getSelected('statusSelect');
  state.page = 1;
  renderAll();
}

function getSelected(id) {
  return [...document.getElementById(id).selectedOptions].map(o => o.value);
}

// ── Render all ────────────────────────────────────────────────────────
function renderAll() {
  const filtered = getFiltered();
  renderMetrics(filtered);
  renderActiveTab(filtered);
}

// ── Tabs ──────────────────────────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
      if (ALL_DATA) renderActiveTab(getFiltered());
    });
  });
}

function activeTab() {
  const b = document.querySelector('.tab-btn.active');
  return b ? b.dataset.tab : 'map';
}

function renderActiveTab(filtered) {
  const tab = activeTab();
  if (tab === 'map')       renderMap(filtered);
  else if (tab === 'analytics') renderAnalytics(filtered);
  else if (tab === 'geo')       renderGeo(filtered);
  else if (tab === 'projects')  renderProjects(filtered);
  else if (tab === 'about')     renderAbout(filtered);
}

// ── Metrics strip ─────────────────────────────────────────────────────
function renderMetrics(d) {
  const issued    = sumCol(d, COL_ISSUED);
  const retired   = sumCol(d, COL_RETIRED);
  const remaining = sumCol(d, COL_REMAINING);
  setText('mProjects',  d.length.toLocaleString());
  setText('mIssued',    fmt(issued));
  setText('mRetired',   fmt(retired));
  setText('mRemaining', fmt(remaining));
}

// ── TAB: World Map ────────────────────────────────────────────────────
function renderMap(d) {
  const byCountry = {};
  for (const r of d) {
    const c = r['Country'];
    if (!c || !COUNTRY_COORDS[c]) continue;
    if (!byCountry[c]) byCountry[c] = { n: 0, issued: 0, remaining: 0 };
    byCountry[c].n++;
    byCountry[c].issued    += r[COL_ISSUED]    || 0;
    byCountry[c].remaining += r[COL_REMAINING] || 0;
  }

  const entries = Object.entries(byCountry);
  if (!entries.length) { plotEmpty('plotMap', 'No geographic data for selected filters'); return; }

  Plotly.react('plotMap', [{
    type: 'scattergeo',
    lat:  entries.map(([c]) => COUNTRY_COORDS[c][0]),
    lon:  entries.map(([c]) => COUNTRY_COORDS[c][1]),
    mode: 'markers',
    text: entries.map(([c,v]) =>
      '<b>' + c + '</b><br>Projects: ' + v.n +
      '<br>Credits Issued: ' + fmt(v.issued) +
      '<br>Credits Remaining: ' + fmt(v.remaining)),
    hovertemplate: '%{text}<extra></extra>',
    marker: {
      size:  entries.map(([,v]) => Math.max(8, Math.sqrt(v.n) * 8)),
      color: entries.map(([,v]) => v.issued),
      colorscale: 'RdYlBu', reversescale: true,
      colorbar: { title: 'Credits<br>Issued', thickness: 14, len: 0.6 },
      sizemode: 'diameter', opacity: 0.85,
      line: { color: 'white', width: 1 },
    },
  }], {
    ...BASE_LAYOUT,
    title: 'IFM Projects by Location  (bubble size = number of projects)',
    height: 580,
    geo: { showland:true, landcolor:'rgb(243,247,250)', showocean:true, oceancolor:'rgb(230,245,255)', showframe:false },
    margin: { t:50, l:0, r:0, b:0 },
  }, CFG);

  const topN = [...entries].sort((a,b) => b[1].n - a[1].n).slice(0,10);
  hBar('plotMapCountProjects', topN.map(e=>e[0]).reverse(), topN.map(e=>e[1].n).reverse(), 'Projects by Country', COLORS[3]);

  const topC = [...entries].sort((a,b) => b[1].issued - a[1].issued).slice(0,10);
  hBar('plotMapCountCredits', topC.map(e=>e[0]).reverse(), topC.map(e=>e[1].issued).reverse(), 'Credits Issued by Country', COLORS[0]);
}

// ── TAB: Analytics ────────────────────────────────────────────────────
function renderAnalytics(d) {
  const regMap = groupSum(d, 'Voluntary Registry', COL_ISSUED);
  const regE   = sortedEntries(regMap);
  pie('plotRegPie', regE.map(e=>e[0]), regE.map(e=>e[1]), 'Credits Issued by Registry');

  const stMap = groupCount(d, 'Voluntary Status');
  const stE   = sortedEntries(stMap);
  donut('plotStatusDonut', stE.map(e=>e[0]), stE.map(e=>e[1]), 'Projects by Status');

  const vintX = [], vintY = [];
  for (const yr of VINTAGE_YEARS) {
    const s = sumCol(d, yr);
    if (s > 0) { vintX.push(Number(yr)); vintY.push(s); }
  }
  Plotly.react('plotVintage', [{
    type:'scatter', mode:'lines+markers', fill:'tozeroy',
    x: vintX, y: vintY,
    line:{ color:COLORS[0], width:3 }, fillcolor:'rgba(26,77,126,.15)',
    name:'Credits Issued',
  }], {
    ...BASE_LAYOUT,
    title:'Credits Issued by Vintage Year',
    xaxis:{title:'Year'}, yaxis:{title:'Credits'},
    hovermode:'x unified', height:380,
  }, CFG);

  const issued    = sumCol(d, COL_ISSUED);
  const retired   = sumCol(d, COL_RETIRED);
  const remaining = sumCol(d, COL_REMAINING);
  Plotly.react('plotLifecycle', [
    mkBar('Issued',    ['Total'], [issued],    COLORS[0]),
    mkBar('Retired',   ['Total'], [retired],   COLORS[3]),
    mkBar('Remaining', ['Total'], [remaining], COLORS[4]),
  ], { ...BASE_LAYOUT, title:'Credit Lifecycle Overview', barmode:'group', height:400 }, CFG);

  const retPct = issued > 0 ? retired   / issued * 100 : 0;
  const remPct = issued > 0 ? remaining / issued * 100 : 0;
  Plotly.react('plotUtilization', [
    mkBar('Retired (%)',   ['Credits'], [retPct], COLORS[3]),
    mkBar('Remaining (%)', ['Credits'], [remPct], COLORS[0]),
  ], {
    ...BASE_LAYOUT, title:'Credit Utilization Rate', barmode:'stack', height:400,
    yaxis:{ title:'Percentage (%)' },
  }, CFG);
}

// ── TAB: Geographic ───────────────────────────────────────────────────
function renderGeo(d) {
  const cntMap   = groupCount(d, 'Country');
  const top15cnt = sortedEntries(cntMap).slice(0,15);
  hBar('plotGeoCount',
    top15cnt.map(e=>e[0]).reverse(), top15cnt.map(e=>e[1]).reverse(),
    'Top 15 Countries by Project Count', COLORS[3], 550);

  const credMap   = groupSum(d, 'Country', COL_ISSUED);
  const top15cred = sortedEntries(credMap).slice(0,15);
  hBar('plotGeoCredits',
    top15cred.map(e=>e[0]).reverse(), top15cred.map(e=>e[1]).reverse(),
    'Top 15 Countries by Credits Issued', COLORS[0], 550);

  const regCredits = groupSum(d, 'Voluntary Registry', COL_ISSUED);
  const regCount   = groupCount(d, 'Voluntary Registry');
  const regs = sortedEntries(regCredits);

  Plotly.react('plotRegistryDual', [{
    type:'bar', name:'Credits Issued',
    x: regs.map(e=>e[0]), y: regs.map(e=>e[1]),
    yaxis:'y', marker:{color:COLORS[0]},
  }, {
    type:'scatter', name:'Project Count', mode:'lines+markers',
    x: regs.map(e=>e[0]), y: regs.map(e => regCount[e[0]] || 0),
    yaxis:'y2', line:{color:COLORS[4],width:3}, marker:{size:10},
  }], {
    ...BASE_LAYOUT,
    title:'Registry Performance: Credits vs Project Count',
    yaxis: {title:'Credits Issued', side:'left'},
    yaxis2:{title:'Number of Projects', overlaying:'y', side:'right'},
    hovermode:'x unified', height:480,
  }, CFG);
}

// ── TAB: Projects table ───────────────────────────────────────────────
function renderProjects(d) {
  const q = state.searchQuery.toLowerCase();
  let rows = q
    ? d.filter(r =>
        (r['Project Name']      || '').toLowerCase().includes(q) ||
        (r['Project Developer'] || '').toLowerCase().includes(q))
    : d;

  rows = [...rows].sort((a,b) => (b[COL_ISSUED]||0) - (a[COL_ISSUED]||0));

  const total = rows.length;
  const ps    = state.pageSize;
  const pg    = state.page;
  const slice = rows.slice((pg-1)*ps, pg*ps);

  setText('showingLabel', total
    ? 'Showing ' + Math.min((pg-1)*ps+1,total).toLocaleString() + '–' + Math.min(pg*ps,total).toLocaleString() + ' of ' + total.toLocaleString() + ' projects'
    : 'No projects match your search');

  document.getElementById('projectsBody').innerHTML = slice.map(r =>
    '<tr>' +
    '<td>' + esc(r['Project ID']||'—') + '</td>' +
    '<td title="' + esc(r['Project Name']||'') + '">' + esc(r['Project Name']||'—') + '</td>' +
    '<td>' + esc(r['Country']||'—') + '</td>' +
    '<td>' + esc(r['Voluntary Registry']||'—') + '</td>' +
    '<td>' + statusBadge(r['Voluntary Status']) + '</td>' +
    '<td>' + (r[COL_ISSUED]   != null ? Math.round(r[COL_ISSUED]).toLocaleString()   : '—') + '</td>' +
    '<td>' + (r[COL_REMAINING]!= null ? Math.round(r[COL_REMAINING]).toLocaleString(): '—') + '</td>' +
    '<td>' + (r['Registry Documents'] ? '<a href="' + esc(r['Registry Documents']) + '" target="_blank" rel="noopener">View ↗</a>' : '—') + '</td>' +
    '</tr>'
  ).join('');

  renderPagination(Math.ceil(total / ps), rows);
}

function renderPagination(totalPages, allRows) {
  const pg  = document.getElementById('pagination');
  const cur = state.page;
  if (totalPages <= 1) { pg.innerHTML = ''; return; }

  const pages = buildPageRange(cur, totalPages);
  let html = '<button class="page-btn" onclick="goPage(' + (cur-1) + ')" ' + (cur===1?'disabled':'') + '>‹</button>';
  for (const p of pages) {
    html += p === '…'
      ? '<span style="padding:6px 8px;color:var(--text-muted)">…</span>'
      : '<button class="page-btn ' + (p===cur?'active':'') + '" onclick="goPage(' + p + ')">' + p + '</button>';
  }
  html += '<button class="page-btn" onclick="goPage(' + (cur+1) + ')" ' + (cur===totalPages?'disabled':'') + '>›</button>';
  pg.innerHTML = html;

  document.getElementById('btnDownload').onclick = () => downloadCSV(allRows);
}

function buildPageRange(cur, total) {
  if (total <= 7) return Array.from({length:total},(_,i)=>i+1);
  const p = [1];
  if (cur > 3) p.push('…');
  for (let i = Math.max(2,cur-1); i <= Math.min(total-1,cur+1); i++) p.push(i);
  if (cur < total-2) p.push('…');
  p.push(total);
  return p;
}

function goPage(p) {
  const filtered = getFiltered();
  const q = state.searchQuery.toLowerCase();
  const rows = q ? filtered.filter(r =>
    (r['Project Name']||'').toLowerCase().includes(q) ||
    (r['Project Developer']||'').toLowerCase().includes(q)) : filtered;
  const totalPages = Math.ceil(rows.length / state.pageSize);
  if (p < 1 || p > totalPages) return;
  state.page = p;
  renderProjects(filtered);
}

function debounceSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.searchQuery = document.getElementById('searchInput').value;
    state.page = 1;
    renderProjects(getFiltered());
  }, 300);
}

function downloadCSV(rows) {
  const headers = ['Project ID','Project Name','Country','Registry','Status','Credits Issued','Credits Remaining','Documents'];
  const body = rows.map(r => [
    r['Project ID']||'', r['Project Name']||'', r['Country']||'',
    r['Voluntary Registry']||'', r['Voluntary Status']||'',
    r[COL_ISSUED]    != null ? Math.round(r[COL_ISSUED])    : '',
    r[COL_REMAINING] != null ? Math.round(r[COL_REMAINING]) : '',
    r['Registry Documents']||'',
  ]);
  const csv = [headers,...body].map(row => row.map(v => '"' + String(v).replace(/"/g,'""') + '"').join(',')).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download = 'ifm_projects.csv';
  a.click();
}

// ── TAB: About ────────────────────────────────────────────────────────
function renderAbout(d) {
  const issued    = sumCol(d, COL_ISSUED);
  const retired   = sumCol(d, COL_RETIRED);
  const remaining = sumCol(d, COL_REMAINING);
  setText('aCountries',     uniqCount(d, 'Country'));
  setText('aRegistries',    uniqCount(d, 'Voluntary Registry'));
  setText('aAvgIssued',     fmt(d.length > 0 ? issued / d.length : 0));
  setText('aRetiredRate',   issued>0 ? (retired/issued*100).toFixed(1)+'%' : '—');
  setText('aRemainingRate', issued>0 ? (remaining/issued*100).toFixed(1)+'%' : '—');

  const stE = sortedEntries(groupCount(d, 'Voluntary Status'));
  Plotly.react('plotAboutStatus', [{
    type:'bar', x: stE.map(e=>e[0]), y: stE.map(e=>e[1]), marker:{color:COLORS[0]},
  }], {
    ...BASE_LAYOUT,
    title:'IFM Projects by Status',
    xaxis:{title:'Status', tickangle:-30}, yaxis:{title:'Number of Projects'},
    height:400,
  }, CFG);
}

// ── Data helpers ──────────────────────────────────────────────────────
function sumCol(rows, col) {
  return rows.reduce((acc,r) => acc + (r[col] != null ? +r[col] : 0), 0);
}

function groupSum(rows, groupKey, valueKey) {
  const m = {};
  for (const r of rows) {
    const k = r[groupKey] || 'Unknown';
    m[k] = (m[k] || 0) + (r[valueKey] || 0);
  }
  return m;
}

function groupCount(rows, groupKey) {
  const m = {};
  for (const r of rows) { const k = r[groupKey] || 'Unknown'; m[k] = (m[k]||0)+1; }
  return m;
}

function sortedEntries(map) {
  return Object.entries(map).sort((a,b) => b[1]-a[1]);
}

function uniqCount(rows, key) {
  return new Set(rows.map(r=>r[key]).filter(Boolean)).size;
}

// ── Plot helpers ──────────────────────────────────────────────────────
function pie(id, labels, values, title) {
  Plotly.react(id, [{
    type:'pie', labels, values, marker:{colors:COLORS},
    hovertemplate:'<b>%{label}</b><br>Credits: %{value:,.0f}<extra></extra>',
  }], { ...BASE_LAYOUT, title, height:400, margin:{t:50,l:20,r:20,b:20} }, CFG);
}

function donut(id, labels, values, title) {
  Plotly.react(id, [{
    type:'pie', hole:0.35, labels, values, marker:{colors:COLORS},
  }], { ...BASE_LAYOUT, title, height:400, margin:{t:50,l:20,r:20,b:20} }, CFG);
}

function hBar(id, ys, xs, title, color, height) {
  height = height || 360;
  Plotly.react(id, [{
    type:'bar', orientation:'h', x:xs, y:ys, marker:{color:color},
  }], { ...BASE_LAYOUT, title, height, margin:{t:50,l:160,r:30,b:50} }, CFG);
}

function mkBar(name, x, y, color) {
  return { type:'bar', name, x, y, marker:{color} };
}

function plotEmpty(id, msg) {
  msg = msg || 'No data';
  Plotly.react(id, [], {
    ...BASE_LAYOUT,
    annotations:[{text:msg,xref:'paper',yref:'paper',x:.5,y:.5,showarrow:false,font:{size:16,color:'#7f8c8d'}}],
    height:400,
  }, CFG);
}

// ── DOM helpers ───────────────────────────────────────────────────────
function setText(id, val) { document.getElementById(id).textContent = val; }

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function fmt(n) {
  if (n == null || isNaN(n)) return '—';
  n = Number(n);
  if (Math.abs(n) >= 1e9) return (n/1e9).toFixed(2)+'B';
  if (Math.abs(n) >= 1e6) return (n/1e6).toFixed(2)+'M';
  if (Math.abs(n) >= 1e3) return (n/1e3).toFixed(1)+'K';
  return Math.round(n).toLocaleString();
}

function statusBadge(s) {
  if (!s) return '—';
  const styles = {
    Active:    'background:#d4edda;color:#155724',
    Retired:   'background:#d1ecf1;color:#0c5460',
    Listed:    'background:#fff3cd;color:#856404',
    Cancelled: 'background:#f8d7da;color:#721c24',
  };
  const style = styles[s] || 'background:#e2e3e5;color:#383d41';
  return '<span style="' + style + ';padding:2px 8px;border-radius:12px;font-size:.8rem;font-weight:600;">' + esc(s) + '</span>';
}
