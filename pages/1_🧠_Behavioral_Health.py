import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import (
    load_latest, load_all_years, get_hancock, get_ohio, get_trend, find_column
)
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat, CHART_CONFIG, LAYOUT_BASE

st.set_page_config(page_title="🧠 Behavioral Health", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.purple { background: linear-gradient(135deg, #6a11cb, #a855f7); }
.kpi-card.red    { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
.kpi-card.blue   { background: linear-gradient(135deg, #1a6dff, #4facfe); }
.kpi-card.teal   { background: linear-gradient(135deg, #0f9b8e, #4ECDC4); }
.kpi-label {
    font-size: 12px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,0.75); margin-bottom: 10px; font-weight: 600;
}
.kpi-value {
    font-size: 36px; font-weight: 800; letter-spacing: -1px;
    margin-bottom: 6px; color: #ffffff;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.kpi-sub { font-size: 12px; color: rgba(255,255,255,0.65); }
.kpi-icon { position: absolute; top: 18px; right: 20px; font-size: 42px; opacity: 0.25; }
.chip-tag {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    background: rgba(168,85,247,0.2); color: #a855f7;
    border: 1px solid rgba(168,85,247,0.4); margin-bottom: 16px;
}
.headline-insight {
    background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(168,85,247,0.05));
    border: 1px solid rgba(168,85,247,0.3);
    border-left: 4px solid #a855f7;
    border-radius: 12px; padding: 18px 24px; margin-bottom: 28px;
    font-size: 15px; color: rgba(255,255,255,0.9); line-height: 1.6;
}
.section-title {
    font-size: 13px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: rgba(255,255,255,0.4);
    margin-bottom: 16px; margin-top: 32px;
}
.year-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 700;
    background: rgba(168,85,247,0.2); color: #a855f7;
    border: 1px solid rgba(168,85,247,0.3);
    margin-left: 8px; vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
latest   = load_latest()
all_data = load_all_years()

# ---- SIDEBAR ----
st.sidebar.header("Filters")

show_ohio = st.sidebar.toggle("Show Ohio Benchmark", value=True)

all_years_list = sorted([
    int(y) for y in all_data['additional']['year'].dropna().unique()
])

selected_year = st.sidebar.selectbox(
    "Select Year",
    options=sorted(all_years_list, reverse=True),
    index=0,
    help="Filters all scorecards and charts to this year"
)

selected_charts = st.sidebar.multiselect(
    "Charts to Display",
    options=[
        "Mental Health Indicators Comparison",
        "Drug Overdose Trend",
        "Mental Health Provider Trend",
        "Suicide Rate Trend",
    ],
    default=[
        "Mental Health Indicators Comparison",
        "Drug Overdose Trend",
        "Mental Health Provider Trend",
        "Suicide Rate Trend",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 CHIP Priority 1")
st.sidebar.markdown("Behavioral Health & Substance Use")
st.sidebar.markdown("**Focus areas:**")
st.sidebar.markdown("- Mental health access")
st.sidebar.markdown("- Substance use & overdose")
st.sidebar.markdown("- Suicide prevention")

# ---- METRIC HELPER ----
def get_metric(col, county='Hancock', sheet='additional'):
    df = all_data[sheet]
    year_df = df[df['year'] == selected_year]
    if county == 'Hancock':
        row = year_df[year_df['County'] == 'Hancock']
    else:
        row = year_df[(year_df['County'].isna()) & (year_df['State'] == 'Ohio')]
    if row.empty or col not in row.columns:
        fallback = get_hancock(latest[sheet]) if county == 'Hancock' else get_ohio(latest[sheet])
        val = fallback[col] if col in fallback.index else None
        return round(float(val), 1) if val is not None and pd.notna(val) else None
    val = row.iloc[0][col]
    return round(float(val), 1) if pd.notna(val) else None

def arrow(h, o, lower_is_better=True):
    if h is None or o is None: return '–'
    return '▼' if (h < o) else '▲'

def diff(h, o):
    if h is None or o is None: return 0
    return round(abs(h - o), 1)

# ---- METRICS ----
mh_days_h  = get_metric('Average Number of Mentally Unhealthy Days', sheet='select')
mh_days_o  = get_metric('Average Number of Mentally Unhealthy Days', county='Ohio', sheet='select')
mh_prov_h  = get_metric('Mental Health Provider Rate', sheet='select')
mh_prov_o  = get_metric('Mental Health Provider Rate', county='Ohio', sheet='select')
overdose_h = get_metric('Drug Overdose Mortality Rate')
overdose_o = get_metric('Drug Overdose Mortality Rate', county='Ohio')
suicide_h  = get_metric('Suicide Rate (Age-Adjusted)')
suicide_o  = get_metric('Suicide Rate (Age-Adjusted)', county='Ohio')
distress_h = get_metric('% Frequent Mental Distress')
distress_o = get_metric('% Frequent Mental Distress', county='Ohio')
drinking_h = get_metric('% Excessive Drinking')
drinking_o = get_metric('% Excessive Drinking', county='Ohio')

mh_prov_h_int = round(mh_prov_h) if mh_prov_h else 0
mh_prov_o_int = round(mh_prov_o) if mh_prov_o else 0

# ---- HEADER ----
st.markdown(
    f"# 🧠 Behavioral Health & Substance Use "
    f"<span class='year-badge'>Showing: {selected_year}</span>",
    unsafe_allow_html=True
)
st.markdown('<div class="chip-tag">🏥 CHIP PRIORITY 1</div>', unsafe_allow_html=True)
st.markdown("Mental health, substance use, and suicide trends for Hancock County vs Ohio.")

# ---- HEADLINE INSIGHT ----
st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Key Finding ({selected_year}):</strong> Hancock County's drug overdose death rate of
    <strong>{overdose_h} per 100k</strong> is {diff(overdose_h, overdose_o)} points below the
    Ohio average of {overdose_o} — a meaningful advantage. However, the county has only
    <strong>{mh_prov_h_int} mental health providers per 100k</strong> residents vs
    {mh_prov_o_int} statewide, leaving significant gaps in access to care precisely where
    CHIP Priority 1 focuses.
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Behavioral Health & Substance Use")

# ---- KPI CARDS ----
st.markdown('<div class="section-title">Key Indicators</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card purple">
        <div class="kpi-icon">🧠</div>
        <div class="kpi-label">Mentally Unhealthy Days</div>
        <div class="kpi-value">{mh_days_h}</div>
        <div class="kpi-sub">Days/month · Ohio: {mh_days_o} · {arrow(mh_days_h, mh_days_o)} {diff(mh_days_h, mh_days_o)} vs state</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-icon">💊</div>
        <div class="kpi-label">Drug Overdose Deaths</div>
        <div class="kpi-value">{overdose_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {overdose_o} · {diff(overdose_h, overdose_o)} better than state</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">💔</div>
        <div class="kpi-label">Suicide Rate</div>
        <div class="kpi-value">{suicide_h}</div>
        <div class="kpi-sub">Per 100k (age-adj) · Ohio: {suicide_o} · {arrow(suicide_h, suicide_o)} {diff(suicide_h, suicide_o)} vs state</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-icon">🏥</div>
        <div class="kpi-label">Mental Health Providers</div>
        <div class="kpi-value">{mh_prov_h_int}</div>
        <div class="kpi-sub">Per 100k · Ohio: {mh_prov_o_int} · {mh_prov_o_int - mh_prov_h_int} fewer than state</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- TREND CHART HELPER ----
def make_trend_chart(trend_df, col, color_map, y_label, value_suffix=""):
    df = trend_df[trend_df['year'] <= selected_year].copy()
    if not show_ohio:
        df = df[df['geography'] == 'Hancock County']
    if df.empty:
        return None
    fig = px.scatter(df, x='year', y=col, color='geography',
                     color_discrete_map=color_map, template='plotly_dark')
    for trace in fig.data:
        geo_data = df[df['geography'] == trace.name]
        trace.mode = 'lines+markers' if len(geo_data) > 1 else 'markers'
        trace.line = dict(width=3)
        trace.marker = dict(size=9)
        trace.hovertemplate = (
            '<b>%{fullData.name}</b><br>'
            'Year: %{x}<br>'
            f'{y_label}: %{{y:.1f}}{value_suffix}'
            '<extra></extra>'
        )
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(tickformat='d', dtick=1),
        yaxis=dict(title=y_label),
    )
    return fig

# ---- CHART 1: COMPARISON BAR ----
if "Mental Health Indicators Comparison" in selected_charts:
    st.markdown(f'<div class="section-title">Mental Health Indicators — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    compare_df = pd.DataFrame({
        'Indicator': [
            'Mentally Unhealthy Days', 'Frequent Mental Distress %',
            'Excessive Drinking %', 'Suicide Rate (per 100k)'
        ],
        'Hancock County': [mh_days_h, distress_h, drinking_h, suicide_h],
        'Ohio': [mh_days_o, distress_o, drinking_o, suicide_o]
    })
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    compare_melted = compare_df[['Indicator'] + cols_to_show].melt(
        id_vars='Indicator', var_name='Geography', value_name='Value'
    )
    fig1 = px.bar(
        compare_melted, x='Indicator', y='Value',
        color='Geography', barmode='group',
        color_discrete_map={'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
        labels={'Value': 'Rate / %', 'Indicator': ''},
        template='plotly_dark'
    )
    fig1.update_traces(
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<extra></extra>'
    )
    fig1.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig1, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 2: OVERDOSE TREND ----
if "Drug Overdose Trend" in selected_charts:
    st.markdown('<div class="section-title">Drug Overdose Deaths — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['Drug Overdose Mortality Rate', 'Drug Overdose Death Rate'])
    if col:
        fig = make_trend_chart(
            get_trend(all_data['additional'], col), col,
            {'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
            'Deaths per 100k', ''
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No overdose data available.")

# ---- CHART 3: MH PROVIDER TREND ----
if "Mental Health Provider Trend" in selected_charts:
    st.markdown('<div class="section-title">Mental Health Provider Access — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['select'], ['Mental Health Provider Rate', 'Mental Health Providers Rate'])
    if col:
        fig = make_trend_chart(
            get_trend(all_data['select'], col), col,
            {'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
            'Providers per 100k', ''
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No provider data available.")

# ---- CHART 4: SUICIDE TREND ----
if "Suicide Rate Trend" in selected_charts:
    st.markdown('<div class="section-title">Suicide Rate — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['Suicide Rate (Age-Adjusted)', 'Suicide Rate'])
    if col:
        fig = make_trend_chart(
            get_trend(all_data['additional'], col), col,
            {'Hancock County': '#ff416c', 'Ohio': '#4ECDC4'},
            'Rate per 100k (age-adj)', ''
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No suicide data available.")

# ---- DOWNLOAD ----
st.markdown("---")
export_df = pd.DataFrame({
    'Indicator': [
        'Drug Overdose Rate', 'Suicide Rate', 'Mental Health Providers',
        'Mentally Unhealthy Days', 'Frequent Mental Distress %', 'Excessive Drinking %'
    ],
    'Hancock County': [overdose_h, suicide_h, mh_prov_h_int, mh_days_h, distress_h, drinking_h],
    'Ohio': [overdose_o, suicide_o, mh_prov_o_int, mh_days_o, distress_o, drinking_o]
})
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Behavioral Health Data as CSV",
    data=csv,
    file_name=f"hancock_behavioral_health_{selected_year}.csv",
    mime="text/csv"
)
if st.checkbox("Show raw comparison data"):
    st.dataframe(export_df, use_container_width=True)

render_disclaimer("Behavioral Health & Substance Use")
render_sidebar_chat("Behavioral Health & Substance Use")