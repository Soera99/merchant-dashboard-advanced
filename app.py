from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Klikko Merchant Intelligence", page_icon="K", layout="wide", initial_sidebar_state="collapsed")


@dataclass(frozen=True)
class KPI:
    label: str
    value: str
    delta: str
    comparison: str
    target: int
    trend: tuple[int, ...]


@st.cache_data
def load_dashboard_data(user_id: str = "demo-merchant") -> dict:
    """Demo adapter. Replace this body with an authenticated API call later."""
    months = [calendar.month_abbr[i] for i in range(1, 13)]
    kpis = [
        KPI("Total Revenue", "Rp 4.82B", "+12.8%", "vs last period", 86, (42, 48, 45, 57, 63, 61, 70, 78)),
        KPI("Revenue Growth", "12.8%", "+2.4pp", "period over period", 78, (35, 44, 40, 52, 56, 63, 61, 71)),
        KPI("Total Consumers", "286,430", "+8.4%", "all time", 82, (45, 49, 52, 57, 62, 66, 71, 77)),
        KPI("Active Consumers", "48,291", "+6.7%", "last 30 days", 74, (54, 58, 55, 62, 60, 69, 72, 76)),
        KPI("Total Campaigns", "62", "+5", "active and completed", 79, (31, 38, 43, 47, 53, 60, 66, 72)),
        KPI("Voucher Redeemed", "428,800", "+22.4%", "total redeemed", 91, (39, 44, 41, 53, 59, 57, 67, 75)),
        KPI("Redemption Rate", "62.4%", "+3.1pp", "claimed to redeemed", 89, (48, 51, 55, 58, 61, 64, 68, 71)),
        KPI("Campaign ROI", "3.8x", "+0.6x", "revenue divided by cost", 84, (40, 46, 43, 55, 62, 58, 68, 74)),
        KPI("Avg Basket Value", "Rp 48K", "+4.9%", "per transaction", 76, (51, 54, 52, 58, 61, 66, 64, 70)),
        KPI("Forecast Revenue", "Rp 1.4B", "+9.2%", "next 30 days", 88, (38, 45, 49, 55, 61, 66, 73, 80)),
    ]
    geography = pd.DataFrame(
        [
            ("DKI Jakarta", -6.2088, 106.8456, 1200, 14200, 48300),
            ("West Java", -6.9175, 107.6191, 820, 12100, 41200),
            ("East Java", -7.2575, 112.7521, 690, 9600, 35800),
            ("Central Java", -7.0051, 110.4381, 610, 8800, 31900),
            ("Bali", -8.4095, 115.1889, 520, 7200, 26400),
            ("North Sumatra", 3.5952, 98.6722, 470, 6800, 24100),
            ("South Sulawesi", -5.1477, 119.4327, 390, 5900, 19800),
            ("East Kalimantan", -0.5022, 117.1536, 350, 4700, 17200),
            ("Riau", 0.5071, 101.4478, 310, 4200, 15800),
            ("West Sumatra", -0.9471, 100.4172, 280, 3900, 14300),
            ("South Kalimantan", -3.3186, 114.5944, 260, 3500, 12800),
            ("Papua", -2.5916, 140.6690, 220, 2800, 9400),
        ],
        columns=["province", "lat", "lon", "revenue", "consumers", "vouchers"],
    )
    return {
        "user_id": user_id, "kpis": kpis, "months": months,
        "revenue": [280, 325, 305, 370, 405, 390, 455, 510, 445, 535, 505, 585],
        "consumer": [18, 21, 23, 22, 28, 30, 32, 35, 38, 41, 44, 48],
        "campaign": [12, 17, 20, 23, 27, 29, 32, 35, 34, 37, 36, 39],
        "redemption": [42, 48, 46, 55, 61, 59, 70, 76, 72, 88, 94, 105],
        "geography": geography,
    }


def inject_css() -> None:
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
      :root { --ink:#182230; --muted:#7d8999; --line:#e7ebf1; --blue:#5577d4; --canvas:#f5f7fa; }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
      .stApp { background:var(--canvas); color:var(--ink); }
      .block-container { max-width:1092px; padding:1.25rem 1rem 3rem; }
      #MainMenu, footer, header, [data-testid="stToolbar"] { visibility:hidden; }
      .topbar { display:flex; justify-content:space-between; align-items:flex-end; gap:2rem; margin-bottom:1.15rem; }
      .eyebrow { color:#5570da; font-size:.72rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
      .page-title { margin:.18rem 0 0; font-size:2rem; letter-spacing:-.04em; font-weight:700; }
      .subtitle { color:var(--muted); margin:.3rem 0 0; font-size:.88rem; }
      .live-pill { background:#e9f8ef; color:#138a50; border:1px solid #d4f0df; border-radius:99px; padding:.42rem .72rem; font-size:.74rem; font-weight:700; white-space:nowrap; }
      div[data-baseweb="tab-list"] { gap:.32rem; background:#fff; border:1px solid var(--line); padding:.36rem; border-radius:14px; overflow-x:auto; box-shadow:0 3px 14px rgba(39,57,86,.025); }
      button[data-baseweb="tab"] { border-radius:9px; padding:.62rem .8rem; color:#748094; white-space:nowrap; }
      button[data-baseweb="tab"] p { font-size:.79rem; }
      button[data-baseweb="tab"][aria-selected="true"] { background:#edf2ff; color:#3157cc; }
      div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display:none; }
      [data-testid="stTabs"] [role="tablist"] { gap:.25rem; background:#fff; border:1px solid var(--line); padding:.32rem; border-radius:14px; box-shadow:0 3px 14px rgba(39,57,86,.025); }
      [data-testid="stTabs"] [role="tab"] { border-radius:9px; padding:.55rem .7rem; white-space:nowrap; }
      [data-testid="stTabs"] [role="tab"][aria-selected="true"] { background:#edf2ff; color:#3157cc; }
      [data-testid="stTabs"] [data-baseweb="tab-highlight"] { display:none; }
      .section-head { margin:1.55rem 0 .65rem; }
      .section-title { font-size:1.02rem; font-weight:700; letter-spacing:-.02em; }
      .kpi-card, .simple-card, .snapshot-card { background:#fff; border:1px solid var(--line); border-radius:16px; box-shadow:0 5px 18px rgba(39,57,86,.03); }
      .kpi-card { min-height:155px; padding:1rem 1rem .85rem; position:relative; overflow:hidden; }
      .kpi-icon { width:28px; height:28px; display:flex; align-items:center; justify-content:center; border-radius:9px; background:#eef3ff; color:#5577d4; font-weight:700; font-size:.7rem; }
      .kpi-delta { position:absolute; right:.85rem; top:1rem; color:#476cc8; background:#edf2ff; border-radius:99px; padding:.2rem .42rem; font-size:.66rem; font-weight:700; }
      .kpi-label { color:#7d8999; font-size:.72rem; margin-top:.65rem; }
      .kpi-value { font-size:1.34rem; font-weight:700; letter-spacing:-.035em; margin-top:.1rem; }
      .comparison { color:#a1a9b5; font-size:.65rem; margin-top:.05rem; }
      .kpi-bottom { display:flex; align-items:flex-end; gap:.55rem; margin-top:.72rem; }
      .target-wrap { flex:1; }.target-label { display:flex; justify-content:space-between; color:#697586; font-size:.62rem; margin-bottom:.25rem; }
      .target-track { height:4px; background:#edf0f4; border-radius:99px; overflow:hidden; }.target-fill { height:100%; background:#5577d4; border-radius:99px; }
      .sparkline { width:55px; height:22px; }
      .simple-card { padding:1rem; display:flex; flex-direction:column; justify-content:center; overflow:hidden; }
      .simple-label { color:#293548; font-size:.72rem; font-weight:700; }
      .simple-metric-row { display:flex; align-items:center; flex-wrap:wrap; gap:.45rem; margin-top:.32rem; }
      .simple-value { color:#111827; font-size:1.34rem; font-weight:700; letter-spacing:-.035em; white-space:nowrap; }
      .simple-delta { color:#0d9c5f; background:#e9faf2; border-radius:99px; padding:.22rem .45rem; font-size:.66rem; font-weight:700; white-space:nowrap; }
      .simple-comparison { color:#98a2b3; font-size:.65rem; margin-top:.42rem; }
      .kpi-row-gap { height:1rem; }
      .active-filter-wrap { margin:.3rem 0 .8rem; padding:.75rem .8rem; background:#f7f9fc; border:1px solid #e8edf4; border-radius:12px; }
      .active-filter-title { color:#667085; font-size:.68rem; font-weight:700; margin-bottom:.45rem; text-transform:uppercase; letter-spacing:.05em; }
      .active-filter-list { display:flex; flex-wrap:wrap; gap:.4rem; }
      .active-filter-chip { display:inline-flex; align-items:center; gap:.28rem; color:#3157a7; background:#eaf0ff; border:1px solid #d9e4ff; border-radius:99px; padding:.26rem .5rem; font-size:.68rem; white-space:nowrap; }
      .active-filter-chip b { color:#263a70; }
      .no-active-filter { color:#98a2b3; font-size:.72rem; }
      div[data-testid="stPlotlyChart"] { background:#fff; border:1px solid var(--line); border-radius:16px; overflow:hidden; box-shadow:0 5px 18px rgba(39,57,86,.03); }
      .snapshot-card { min-height:286px; padding:1rem 1.05rem; }.card-kicker { color:#293548; font-size:.78rem; font-weight:700; margin-bottom:.55rem; }
      .snapshot-row { display:flex; justify-content:space-between; gap:.7rem; padding:.62rem 0; border-top:1px solid #eef1f5; }
      .snap-type { color:#99a2b0; font-size:.61rem; }.snap-name { font-size:.74rem; font-weight:600; margin-top:.08rem; }.snap-value { font-size:.75rem; font-weight:700; text-align:right; align-self:center; white-space:nowrap; }
      .placeholder { margin-top:1rem; background:#fff; border:1px dashed #d6dce5; border-radius:16px; padding:4rem 2rem; text-align:center; color:#7c8797; }.placeholder b { color:#273244; }
      .stDownloadButton button { border-radius:10px; border-color:#dce2ec; font-size:.76rem; }
      [data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:14px; }
      @media(max-width:900px){ .block-container{padding:1rem}.topbar{align-items:flex-start}.live-pill{display:none}.page-title{font-size:1.65rem}.simple-value,.kpi-value{font-size:1.15rem} }
    </style>
    """, unsafe_allow_html=True)


def section(title: str) -> None:
    st.markdown(f'<div class="section-head"><div class="section-title">{title}</div></div>', unsafe_allow_html=True)


def sparkline_svg(values: tuple[int, ...]) -> str:
    width, height, pad = 55, 22, 2
    low, high = min(values), max(values)
    span = max(high - low, 1)
    points = " ".join(f"{pad + i * (width - 2 * pad) / (len(values) - 1):.1f},{height - pad - (v - low) * (height - 2 * pad) / span:.1f}" for i, v in enumerate(values))
    return f'<svg class="sparkline" viewBox="0 0 {width} {height}"><polyline points="{points}" fill="none" stroke="#5577d4" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def render_kpi(kpi: KPI) -> None:
    initials = "".join(part[0] for part in kpi.label.split()[:2]).upper()
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">{initials}</div><div class="kpi-delta">{kpi.delta}</div>
      <div class="kpi-label">{kpi.label}</div><div class="kpi-value">{kpi.value}</div><div class="comparison">{kpi.comparison}</div>
      <div class="kpi-bottom"><div class="target-wrap"><div class="target-label"><span>Target</span><b>{kpi.target}%</b></div>
      <div class="target-track"><div class="target-fill" style="width:{kpi.target}%"></div></div></div>{sparkline_svg(kpi.trend)}</div></div>""", unsafe_allow_html=True)


def render_simple_card(label: str, value: str, delta: str, comparison: str) -> None:
    st.markdown(f"""<div class="simple-card"><div class="simple-label">{label}</div>
      <div class="simple-metric-row"><div class="simple-value">{value}</div><div class="simple-delta">↑ {delta}</div></div>
      <div class="simple-comparison">{comparison}</div></div>""", unsafe_allow_html=True)


def trend_chart(title: str, subtitle: str, x: list[str], y: list[int], color: str, kind: str = "line") -> go.Figure:
    fig = go.Figure()
    if kind == "bar":
        fig.add_bar(x=x, y=y, marker_color=color, marker_line_width=0, opacity=.9, hovertemplate="%{x}: %{y:,}<extra></extra>")
    else:
        rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        fig.add_scatter(x=x, y=y, mode="lines+markers", line=dict(color=color, width=2.2, shape="spline"), marker=dict(size=5, color=color, line=dict(color="white", width=1)), fill="tozeroy", fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.10)", hovertemplate="%{x}: %{y:,}<extra></extra>")
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><span style='font-size:11px;color:#98a2b3'>{subtitle}</span>", x=.045, y=.92), height=315, margin=dict(l=30, r=25, t=75, b=30), paper_bgcolor="white", plot_bgcolor="white", font=dict(family="DM Sans", color="#344054"), showlegend=False, dragmode=False, xaxis=dict(showgrid=False, zeroline=False, fixedrange=True, tickfont=dict(size=10, color="#98a2b3")), yaxis=dict(showgrid=True, gridcolor="#eef1f5", zeroline=False, fixedrange=True, showticklabels=False), hoverlabel=dict(bgcolor="white", font_color="#182230"), bargap=.42)
    return fig


def render_snapshot(kicker: str, rows: list[tuple[str, str, str]]) -> None:
    content = "".join(f'<div class="snapshot-row"><div><div class="snap-type">{kind}</div><div class="snap-name">{name}</div></div><div class="snap-value">{value}</div></div>' for kind, name, value in rows)
    st.markdown(f'<div class="snapshot-card"><div class="card-kicker">{kicker}</div>{content}</div>', unsafe_allow_html=True)


def map_chart(frame: pd.DataFrame, metric: str) -> go.Figure:
    config = {"Revenue": ("revenue", "Revenue", "Rp %{customdata[1]:,.0f}M", "#5577d4"), "Consumer": ("consumers", "Consumers", "%{customdata[1]:,.0f}", "#8b6bd8"), "Voucher": ("vouchers", "Vouchers", "%{customdata[1]:,.0f}", "#2f9b78")}
    field, label, value_template, color = config[metric]
    values = frame[field]
    sizes = 10 + 34 * (values - values.min()) / max(values.max() - values.min(), 1)
    custom = pd.concat([frame["province"], values], axis=1).to_numpy()
    fig = go.Figure(go.Scattergeo(lon=frame["lon"], lat=frame["lat"], mode="markers+text", text=frame["province"].str.replace(" ", "<br>"), textposition="top center", textfont=dict(size=8, color="#667085"), marker=dict(size=sizes, color=values, colorscale=[[0, "#dbe5ff"], [1, color]], opacity=.88, line=dict(color="white", width=1), showscale=False), customdata=custom, hovertemplate=f"<b>%{{customdata[0]}}</b><br>{label}: {value_template}<extra></extra>"))
    fig.update_geos(scope="asia", projection_type="mercator", showland=True, landcolor="#f0f3f9", showocean=True, oceancolor="#fbfcfe", showcountries=True, countrycolor="#d9e0ea", showcoastlines=False, lataxis_range=[-12, 7], lonaxis_range=[94, 143], bgcolor="white")
    fig.update_layout(height=430, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="white", geo=dict(center=dict(lat=-2.5, lon=118)), font=dict(family="DM Sans"))
    return fig


def filter_bar(data: dict) -> None:
    filters = {
        "Business Owner": ["All business owners", "Klikko Group", "Partner Network"],
        "Brand": ["All brands", "Brand A", "Brand B", "Brand C"],
        "Merchant": ["All merchants", "Guardian", "Klik Indomaret", "Outlet Network"],
        "Campaign": ["All campaigns", "Campaign Merdeka", "Klikko Payday", "Weekend Deal"],
        "Program Type": ["All program types", "Voucher", "Sampling", "Retail Media"],
        "Machine": ["All machines", "Vending BSD 01", "Kiosk JKT 041", "Kiosk SBY 018"],
        "Province": ["All provinces", "DKI Jakarta", "West Java", "East Java", "Bali"],
        "City": ["All cities", "Jakarta", "Bandung", "Surabaya", "Denpasar"],
        "Category": ["All categories", "Beverages", "Snacks", "Health & Beauty"],
        "Product": ["All products", "Iced Latte 250ml", "Matcha Cloud", "Caramel Macchiato"],
        "Consumer Segment": ["All consumer segments", "New", "Active", "Returning", "At risk"],
        "Gender": ["All genders", "Female", "Male", "Prefer not to say"],
        "Age Group": ["All age groups", "13–17", "18–24", "25–34", "35–50", "50+"],
    }
    with st.expander("Filters", expanded=False):
        names = list(filters)
        selected_filters = {}
        for start in range(0, len(names), 4):
            columns = st.columns(4, gap="small")
            for column, name in zip(columns, names[start:start + 4]):
                with column:
                    selected = st.selectbox(name, filters[name], key=f"filter_{name}")
                    if selected != filters[name][0]:
                        selected_filters[name] = selected
        if selected_filters:
            chips = "".join(
                f'<span class="active-filter-chip"><b>{escape(name)}:</b> {escape(value)}</span>'
                for name, value in selected_filters.items()
            )
            active_content = f'<div class="active-filter-list">{chips}</div>'
        else:
            active_content = '<div class="no-active-filter">No active filters</div>'
        st.markdown(
            f'<div class="active-filter-wrap"><div class="active-filter-title">Active filters</div>{active_content}</div>',
            unsafe_allow_html=True,
        )
        export = pd.DataFrame([{"Metric": k.label, "Value": k.value, "Change": k.delta} for k in data["kpis"]]).to_csv(index=False)
        st.download_button("Download KPI data", export, "executive-overview.csv", "text/csv")


def executive_overview(data: dict) -> None:
    filter_bar(data)
    section("Executive KPI Cards")
    for start in (0, 5):
        cols = st.columns(5, gap="medium")
        for col, kpi in zip(cols, data["kpis"][start:start + 5]):
            with col:
                if start == 0:
                    render_kpi(kpi)
                else:
                    render_simple_card(kpi.label, kpi.value, kpi.delta, kpi.comparison)
        if start == 0:
            st.markdown('<div class="kpi-row-gap"></div>', unsafe_allow_html=True)

    section("Business Growth Trend")
    charts = [("Revenue Trend", "Last 12 Months", data["revenue"], "#5577d4", "line"), ("Consumer Trend", "Last 12 Months", data["consumer"], "#8467d7", "line"), ("Campaign Trend", "Last 12 Months", data["campaign"], "#5577d4", "bar"), ("Voucher Redemption Trend", "Last 12 Months", data["redemption"], "#2f9b78", "line")]
    for pair_start in (0, 2):
        cols = st.columns(2, gap="large")
        for col, item in zip(cols, charts[pair_start:pair_start + 2]):
            with col: st.plotly_chart(trend_chart(item[0], item[1], data["months"], item[2], item[3], item[4]), width="stretch", config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False})

    section("Business Snapshot")
    snapshots = [
        ("Ranked performance", [("TOP CAMPAIGN", "Campaign Merdeka", "Rp 840M"), ("TOP PRODUCT", "Iced Latte 250ml", "9,820"), ("TOP MERCHANT", "Guardian BSD Central", "Rp 420M"), ("TOP MACHINE", "Vending BSD Central 01", "Rp 180M"), ("TOP PROVINCE", "DKI Jakarta", "Rp 1.2B")]),
        ("Attention required", [("BOTTOM CAMPAIGN", "Bakery Weekday Deal", "Rp 12M"), ("BOTTOM PRODUCT", "Expired Bakery Item", "284"), ("BOTTOM MERCHANT", "Outlet Cikini", "Rp 8M"), ("LOWEST ROI", "Morning Snack Trial", "0.7x"), ("LOWEST REDEMPTION", "Weekend Bundle", "18.2%")]),
        ("Key operating signals", [("ACTIVE USERS", "Last 30 days", "48,291"), ("CAMPAIGN SUCCESS", "Above ROI threshold", "76.4%"), ("MERCHANT COVERAGE", "Active locations", "1,284"), ("AVG SESSION", "Merchant portal", "08m 42s"), ("AVG CAMPAIGN ROI", "Revenue per cost", "3.8x")]),
    ]
    cols = st.columns(3, gap="large")
    for col, (kicker, rows) in zip(cols, snapshots):
        with col: render_snapshot(kicker, rows)

    section("Indonesia Business Heatmap")
    map_left, map_right = st.columns([4, 1])
    with map_right:
        metric = st.radio("Map metric", ["Revenue", "Consumer", "Voucher"])
        st.caption("Select a metric to resize and recolor each province bubble.")
        top_field = {"Revenue": "revenue", "Consumer": "consumers", "Voucher": "vouchers"}[metric]
        top = data["geography"].sort_values(top_field, ascending=False).iloc[0]
        st.metric("Leading province", top["province"])
        st.metric("Network coverage", f'{len(data["geography"])} provinces')
    with map_left: st.plotly_chart(map_chart(data["geography"], metric), width="stretch", config={"displayModeBar": False})

    section("Forecast Summary — Next 30 Days")
    forecasts = [("Revenue Forecast", "Rp 1.4B", "+9.2% expected", "#5577d4"), ("Consumer Forecast", "+28,400", "+7.8% expected", "#8467d7"), ("Redemption Forecast", "88,400", "+14.0% expected", "#2f9b78"), ("Campaign Completion", "84%", "+4.0pp expected", "#3578c8")]
    cols = st.columns(4, gap="large")
    for col, (label, value, note, accent) in zip(cols, forecasts):
        with col: render_simple_card(label, value, note.replace(" expected", ""), "vs. current 30-day run rate")


def placeholder_tab(name: str, source: str) -> None:
    st.markdown(f'<div class="placeholder"><b>{name}</b><br><br>The navigation and responsive shell are ready. The next build can populate this module from {source}.</div>', unsafe_allow_html=True)


inject_css()
data = load_dashboard_data()
updated = date.today() - timedelta(days=1)
st.markdown(f'<div class="topbar"><div><div class="eyebrow">Klikko Intelligence</div><div class="page-title">Merchant Dashboard</div><div class="subtitle">Executive performance across revenue, customers, campaigns, vouchers, and operations · Updated {updated:%d %b %Y}</div></div><div class="live-pill">● &nbsp; Demo data connected</div></div>', unsafe_allow_html=True)

tab_names = ["Executive Overview", "Marketing & Campaign Intelligence", "Klikko-Hub & Operational Intelligence", "Product & Sales Intelligence", "Consumer & Merchant Intelligence"]
tabs = st.tabs(tab_names)
with tabs[0]: executive_overview(data)
with tabs[1]: placeholder_tab(tab_names[1], "the remaining campaign specifications in Sheet 1")
with tabs[2]: placeholder_tab(tab_names[2], "the operational specifications in Sheet 2")
with tabs[3]: placeholder_tab(tab_names[3], "the product and sales specifications in Sheet 2")
with tabs[4]: placeholder_tab(tab_names[4], "the consumer and merchant specifications in Sheet 2")
