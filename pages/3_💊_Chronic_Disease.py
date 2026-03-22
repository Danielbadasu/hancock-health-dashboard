import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import (
    load_latest, load_all_years, get_hancock, get_ohio, get_trend, find_column
)
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat, CHART_CONFIG, LAYOUT_BASE

st.set_page_config(page_title="💊 Chronic Disease", page_icon="💊", layout="wide")

st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.orange { background: linear-gradient(135deg, #f7971e, #ffd200); }
.kpi-card.red    { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
.kpi-card.green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card.blue   { background: linear-gradient(135deg, #1a6dff, #4facfe); }
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
    background: rgba(247,151,30,0.2); color: #ffd200;
    border: 1px solid rgba(247,151,30,0.4); margin-bottom: 16px;
}
.headline-insight {
    background: linear-gradient(135deg, rgba(247,151,30,0.1), rgba(247,151,30,0.05));
    border: 1px solid rgba(247,151,30,0.3);
    border-left: 4px solid #ffd200;
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
    background: rgba(255,210,0,0.2); color: #ffd200;
    border: 1px solid rgba(255,210,0,0.3);
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
        "Chronic Disease Comparison",
        "Obesity Trend",
        "Diabetes Trend",
        "Smoking Trend",
        "PCP Access Trend",
    ],
    default=[
        "Chronic Disease Comparison",
        "Obesity Trend",
        "Diabetes Trend",
        "Smoking Trend",
        "PCP Access Trend",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 CHIP Priority 3")
st.sidebar.markdown("Chronic Disease & Healthy Lifestyle")
st.sidebar.markdown("**Focus areas:**")
st.sidebar.markdown("- Obesity & diabetes")
st.sidebar.markdown("- Smoking & inactivity")
st.sidebar.markdown("- Preventive care access")

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
obesity_h     = get_metric('% Adults with Obesity')
obesity_o     = get_metric('% Adults with Obesity', county='Ohio')
diabetes_h    = get_metric('% Adults with Diabetes')
diabetes_o    = get_metric('% Adults with Diabetes', county='Ohio')
smoking_h     = get_metric('% Adults Reporting Currently Smoking')
smoking_o     = get_metric('% Adults Reporting Currently Smoking', county='Ohio')
inactive_h    = get_metric('% Physically Inactive')
inactive_o    = get_metric('% Physically Inactive', county='Ohio')
poor_health_h = get_metric('% Fair or Poor Health', sheet='select')
poor_health_o = get_metric('% Fair or Poor Health', county='Ohio', sheet='select')
phys_days_h   = get_metric('Average Number of Physically Unhealthy Days', sheet='select')
phys_days_o   = get_metric('Average Number of Physically Unhealthy Days', county='Ohio', sheet='select')
uninsured_h   = get_metric('% Uninsured', sheet='select')
uninsured_o   = get_metric('% Uninsured', county='Ohio', sheet='select')
pcp_h_raw     = get_metric('Primary Care Physicians Rate', sheet='select')
pcp_o_raw     = get_metric('Primary Care Physicians Rate', county='Ohio', sheet='select')
pcp_h         = round(pcp_h_raw) if pcp_h_raw else 0
pcp_o         = round(pcp_o_raw) if pcp_o_raw else 0

# ---- HEADER ----
st.markdown(
    f"# 💊 Chronic Disease & Healthy Lifestyle "
    f"<span class='year-badge'>Showing: {selected_year}</span>",
    unsafe_allow_html=True
)
st.markdown('<div class="chip-tag">🏥 CHIP PRIORITY 3</div>', unsafe_allow_html=True)
st.markdown("Obesity, diabetes, smoking, physical inactivity, and healthcare access for Hancock County vs Ohio.")

# ---- HEADLINE INSIGHT ----
st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Key Finding ({selected_year}):</strong> Hancock County's chronic disease profile
    closely mirrors Ohio — obesity at <strong>{obesity_h}%</strong> (Ohio: {obesity_o}%) and
    diabetes at <strong>{diabetes_h}%</strong> (Ohio: {diabetes_o}%). The most actionable gap
    is physical inactivity at <strong>{inactive_h}%</strong> and only
    <strong>{pcp_h} primary care physicians per 100k</strong> vs {pcp_o} statewide —
    access to preventive care is where CHIP Priority 3 can make the biggest difference.
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Chronic Disease & Healthy Lifestyle")

# ---- KPI ROW 1 ----
st.markdown('<div class="section-title">Key Indicators</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card orange">
        <div class="kpi-icon">⚖️</div>
        <div class="kpi-label">Adult Obesity</div>
        <div class="kpi-value">{obesity_h}%</div>
        <div class="kpi-sub">Ohio: {obesity_o}% · {arrow(obesity_h, obesity_o)} {diff(obesity_h, obesity_o)}% vs state</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-icon">🩺</div>
        <div class="kpi-label">Diabetes Prevalence</div>
        <div class="kpi-value">{diabetes_h}%</div>
        <div class="kpi-sub">Ohio: {diabetes_o}% · {arrow(diabetes_h, diabetes_o)} {diff(diabetes_h, diabetes_o)}% vs state</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-icon">🚬</div>
        <div class="kpi-label">Adult Smoking</div>
        <div class="kpi-value">{smoking_h}%</div>
        <div class="kpi-sub">Ohio: {smoking_o}% · {arrow(smoking_h, smoking_o)} {diff(smoking_h, smoking_o)}% vs state</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-icon">🛋️</div>
        <div class="kpi-label">Physical Inactivity</div>
        <div class="kpi-value">{inactive_h}%</div>
        <div class="kpi-sub">Ohio: {inactive_o}% · {arrow(inactive_h, inactive_o)} {diff(inactive_h, inactive_o)}% vs state</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 2 ----
st.markdown('<div class="section-title"> </div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card blue">
        <div class="kpi-icon">😷</div>
        <div class="kpi-label">Fair or Poor Health</div>
        <div class="kpi-value">{poor_health_h}%</div>
        <div class="kpi-sub">Ohio: {poor_health_o}% · {arrow(poor_health_h, poor_health_o)} {diff(poor_health_h, poor_health_o)}% vs state</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Physically Unhealthy Days</div>
        <div class="kpi-value">{phys_days_h}</div>
        <div class="kpi-sub">Days/month · Ohio: {phys_days_o}</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">🏥</div>
        <div class="kpi-label">Primary Care Physicians</div>
        <div class="kpi-value">{pcp_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {pcp_o} · {pcp_o - pcp_h} fewer than state</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">💳</div>
        <div class="kpi-label">Uninsured Rate</div>
        <div class="kpi-value">{uninsured_h}%</div>
        <div class="kpi-sub">Ohio: {uninsured_o}% · {arrow(uninsured_h, uninsured_o)} {diff(uninsured_h, uninsured_o)}% vs state</div>
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
    n_years = df['year'].nunique()
    fig = px.scatter(df, x='year', y=col, color='geography',
                     color_discrete_map=color_map, template='plotly_dark')
    for trace in fig.data:
        geo_data = df[df['geography'] == trace.name]
        trace.mode = 'lines+markers' if len(geo_data) > 1 else 'markers'
        trace.line = dict(width=3)
        trace.marker = dict(size=9 if len(geo_data) > 1 else 14)
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
    return fig, n_years

# ---- CHART 1: COMPARISON BAR ----
if "Chronic Disease Comparison" in selected_charts:
    st.markdown(f'<div class="section-title">Chronic Disease Rates — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    bar_data = pd.DataFrame({
        'Indicator': ['Obesity %', 'Diabetes %', 'Smoking %', 'Physical Inactivity %', 'Fair/Poor Health %'],
        'Hancock County': [obesity_h, diabetes_h, smoking_h, inactive_h, poor_health_h],
        'Ohio': [obesity_o, diabetes_o, smoking_o, inactive_o, poor_health_o]
    })
    cols_to_melt = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    bar_melted = bar_data[['Indicator'] + cols_to_melt].melt(
        id_vars='Indicator', var_name='Geography', value_name='Value'
    )
    fig1 = px.bar(
        bar_melted, x='Indicator', y='Value',
        color='Geography', barmode='group',
        color_discrete_map={'Hancock County': '#ffd200', 'Ohio': '#4ECDC4'},
        labels={'Value': 'Percentage (%)', 'Indicator': ''},
        template='plotly_dark'
    )
    fig1.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    fig1.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig1, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 2: OBESITY TREND ----
if "Obesity Trend" in selected_charts:
    st.markdown('<div class="section-title">Adult Obesity — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['% Adults with Obesity', '% Obese', 'Adult Obesity Rate'])
    if col:
        result = make_trend_chart(get_trend(all_data['additional'], col), col,
                                  {'Hancock County': '#ffd200', 'Ohio': '#4ECDC4'}, 'Adults with Obesity', '%')
        if result:
            fig, _ = result
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No obesity data available.")

# ---- CHART 3: DIABETES TREND ----
if "Diabetes Trend" in selected_charts:
    st.markdown('<div class="section-title">Diabetes Prevalence — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['% Adults with Diabetes', '% Diabetic', 'Diabetes Rate'])
    if col:
        result = make_trend_chart(get_trend(all_data['additional'], col), col,
                                  {'Hancock County': '#ffd200', 'Ohio': '#4ECDC4'}, 'Adults with Diabetes', '%')
        if result:
            fig, _ = result
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No diabetes data available.")

# ---- CHART 4: SMOKING TREND ----
if "Smoking Trend" in selected_charts:
    st.markdown('<div class="section-title">Adult Smoking — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], [
        '% Adults Reporting Currently Smoking', '% Smokers', 'Adult Smoking Rate'
    ])
    if col:
        result = make_trend_chart(get_trend(all_data['additional'], col), col,
                                  {'Hancock County': '#ffd200', 'Ohio': '#4ECDC4'}, 'Adults Smoking', '%')
        if result:
            fig, n_years = result
            if n_years <= 1:
                st.info("ℹ️ Only one year of smoking data available. Showing as data point.")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 5: PCP TREND ----
if "PCP Access Trend" in selected_charts:
    st.markdown('<div class="section-title">Primary Care Physician Access — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['select'], ['Primary Care Physicians Rate', 'Primary Care Physician Rate'])
    if col:
        result = make_trend_chart(get_trend(all_data['select'], col), col,
                                  {'Hancock County': '#38ef7d', 'Ohio': '#4ECDC4'}, 'Physicians per 100k', '')
        if result:
            fig, _ = result
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No PCP data available.")

# ---- DOWNLOAD ----
st.markdown("---")
export_df = pd.DataFrame({
    'Indicator': ['Adult Obesity %', 'Diabetes %', 'Adult Smoking %', 'Physical Inactivity %',
                  'Fair/Poor Health %', 'Physically Unhealthy Days', 'Primary Care Physicians per 100k', 'Uninsured %'],
    'Hancock County': [obesity_h, diabetes_h, smoking_h, inactive_h, poor_health_h, phys_days_h, pcp_h, uninsured_h],
    'Ohio': [obesity_o, diabetes_o, smoking_o, inactive_o, poor_health_o, phys_days_o, pcp_o, uninsured_o]
})
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Chronic Disease Data as CSV", data=csv,
                   file_name=f"hancock_chronic_disease_{selected_year}.csv", mime="text/csv")
if st.checkbox("Show raw comparison data"):
    st.dataframe(export_df, use_container_width=True)

render_disclaimer("Chronic Disease & Healthy Lifestyle")
render_sidebar_chat("Chronic Disease & Healthy Lifestyle")