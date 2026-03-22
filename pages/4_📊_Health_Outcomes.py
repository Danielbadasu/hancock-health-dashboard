import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import (
    load_latest, load_all_years, get_hancock, get_ohio,
    get_trend, get_all_counties, find_column
)
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat

st.set_page_config(page_title="📊 Health Outcomes", page_icon="📊", layout="wide")

# ---- CSS ----
st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.teal   { background: linear-gradient(135deg, #0f9b8e, #4ECDC4); }
.kpi-card.green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card.coral  { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
.kpi-card.purple { background: linear-gradient(135deg, #6a11cb, #a855f7); }
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
    background: rgba(78,205,196,0.15); color: #4ECDC4;
    border: 1px solid rgba(78,205,196,0.4); margin-bottom: 16px;
}
.headline-insight {
    background: linear-gradient(135deg, rgba(56,239,125,0.08), rgba(56,239,125,0.03));
    border: 1px solid rgba(56,239,125,0.25);
    border-left: 4px solid #38ef7d;
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
    background: rgba(56,239,125,0.2); color: #38ef7d;
    border: 1px solid rgba(56,239,125,0.3);
    margin-left: 8px; vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ---- CHART CONFIG ----
CHART_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': [
        'zoom2d', 'pan2d', 'select2d', 'lasso2d',
        'zoomIn2d', 'zoomOut2d', 'autoScale2d',
        'hoverClosestCartesian', 'hoverCompareCartesian',
        'toggleSpikelines'
    ],
    'displaylogo': False,
    'scrollZoom': False,
}

LAYOUT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0.2)',
    hovermode='closest',
    hoverlabel=dict(bgcolor='#1a1a2e', font_size=13),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
)

# ---- LOAD DATA ----
latest   = load_latest()
all_data = load_all_years()

# ---- SIDEBAR FILTERS — defined first so KPIs are driven by them ----
st.sidebar.header("Filters")

show_ohio = st.sidebar.toggle("Show Ohio Benchmark", value=True)

all_years_list = sorted([
    int(y) for y in all_data['additional']['year'].dropna().unique()
])

selected_year = st.sidebar.selectbox(
    "KPI Reference Year",
    options=sorted(all_years_list, reverse=True),
    index=0,
    help="Changes the scorecard values above"
)

if len(all_years_list) >= 2:
    year_range = st.sidebar.slider(
        "Chart Year Range",
        min_value=min(all_years_list),
        max_value=max(all_years_list),
        value=(min(all_years_list), max(all_years_list)),
        step=1
    )
else:
    year_range = (
        min(all_years_list) if all_years_list else 2020,
        max(all_years_list) if all_years_list else 2025
    )

selected_charts = st.sidebar.multiselect(
    "Charts to Display",
    options=[
        "Life Expectancy Trend",
        "YPLL Trend",
        "Health Outcomes Comparison",
        "County Ranking",
    ],
    default=[
        "Life Expectancy Trend",
        "YPLL Trend",
        "Health Outcomes Comparison",
        "County Ranking",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Health Outcomes")
st.sidebar.markdown("Cross-cutting across all CHIP priorities")
st.sidebar.markdown("**Indicators:**")
st.sidebar.markdown("- Life expectancy")
st.sidebar.markdown("- Premature mortality")
st.sidebar.markdown("- Birth outcomes")
st.sidebar.markdown("- Injury deaths")

# ---- DYNAMIC METRIC HELPER ----
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

# ---- DYNAMIC METRICS ----
life_exp_h   = get_metric('Life Expectancy')
life_exp_o   = get_metric('Life Expectancy', county='Ohio')
ypll_h       = get_metric('Years of Potential Life Lost Rate', sheet='select')
ypll_o       = get_metric('Years of Potential Life Lost Rate', county='Ohio', sheet='select')
injury_h     = get_metric('Injury Death Rate', sheet='select')
injury_o     = get_metric('Injury Death Rate', county='Ohio', sheet='select')
infant_h     = get_metric('Infant Mortality Rate')
infant_o     = get_metric('Infant Mortality Rate', county='Ohio')
child_mort_h = get_metric('Child Mortality Rate')
child_mort_o = get_metric('Child Mortality Rate', county='Ohio')
lbw_h        = get_metric('% Low Birth Weight', sheet='select')
lbw_o        = get_metric('% Low Birth Weight', county='Ohio', sheet='select')

life_diff = round((life_exp_h or 0) - (life_exp_o or 0), 1)
ypll_diff = round((ypll_o or 0) - (ypll_h or 0))

# ---- HEADER ----
st.markdown(
    f"# 📊 Health Outcomes & Mortality "
    f"<span class='year-badge'>Showing: {selected_year}</span>",
    unsafe_allow_html=True
)
st.markdown('<div class="chip-tag">📊 CROSS-CUTTING — ALL CHIP PRIORITIES</div>', unsafe_allow_html=True)
st.markdown("Life expectancy, mortality, and birth outcomes for Hancock County vs Ohio.")

# ---- HEADLINE INSIGHT ----
st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Key Finding ({selected_year}):</strong> Hancock County residents live an average of
    <strong>{life_exp_h} years</strong> — {life_diff} years longer than the Ohio average of {life_exp_o}.
    The county also loses <strong>{ypll_diff:,} fewer years of potential life</strong> per 100k residents
    than the state average, reflecting stronger overall health outcomes. These strengths support
    the case for continued investment across all three CHIP priority areas.
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Health Outcomes & Mortality")

# ---- KPI ROW 1 ----
st.markdown('<div class="section-title">Key Indicators</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card teal">
        <div class="kpi-icon">❤️</div>
        <div class="kpi-label">Life Expectancy</div>
        <div class="kpi-value">{life_exp_h} yrs</div>
        <div class="kpi-sub">Ohio: {life_exp_o} yrs · {arrow(life_exp_h, life_exp_o, lower_is_better=False)} {diff(life_exp_h, life_exp_o)} yrs vs state</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-label">Years of Potential Life Lost</div>
        <div class="kpi-value">{int(ypll_h):,}</div>
        <div class="kpi-sub">Per 100k · Ohio: {int(ypll_o):,} · {ypll_diff:,} fewer than state</div>
    </div>
    <div class="kpi-card coral">
        <div class="kpi-icon">🚑</div>
        <div class="kpi-label">Injury Death Rate</div>
        <div class="kpi-value">{injury_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {injury_o} · {arrow(injury_h, injury_o)} {diff(injury_h, injury_o)} vs state</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-icon">👶</div>
        <div class="kpi-label">Infant Mortality Rate</div>
        <div class="kpi-value">{infant_h}</div>
        <div class="kpi-sub">Per 1,000 live births · Ohio: {infant_o} · {arrow(infant_h, infant_o)} {diff(infant_h, infant_o)} vs state</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 2 ----
st.markdown('<div class="section-title"> </div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card blue">
        <div class="kpi-icon">🧒</div>
        <div class="kpi-label">Child Mortality Rate</div>
        <div class="kpi-value">{child_mort_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {child_mort_o} · {arrow(child_mort_h, child_mort_o)} {diff(child_mort_h, child_mort_o)} vs state</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">⚖️</div>
        <div class="kpi-label">Low Birth Weight</div>
        <div class="kpi-value">{lbw_h}%</div>
        <div class="kpi-sub">Ohio: {lbw_o}% · {arrow(lbw_h, lbw_o)} {diff(lbw_h, lbw_o)}% vs state</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- TREND CHART HELPER ----
def make_trend_chart(trend_df, col, color_map, y_label, value_suffix=""):
    df = trend_df[
        (trend_df['year'] >= year_range[0]) &
        (trend_df['year'] <= year_range[1])
    ].copy()
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

# ---- CHART 1: LIFE EXPECTANCY TREND ----
if "Life Expectancy Trend" in selected_charts:
    st.markdown('<div class="section-title">Life Expectancy — Trend Over Time</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['Life Expectancy', 'life_expectancy'])
    if col:
        fig = make_trend_chart(
            get_trend(all_data['additional'], col), col,
            {'Hancock County': '#38ef7d', 'Ohio': '#4ECDC4'},
            'Life Expectancy', ' yrs'
        )
        if fig:
            fig.update_layout(yaxis=dict(range=[68, 82], title='Life Expectancy (years)'))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No life expectancy data in selected year range.")

# ---- CHART 2: YPLL TREND ----
if "YPLL Trend" in selected_charts:
    st.markdown('<div class="section-title">Years of Potential Life Lost — Trend Over Time</div>', unsafe_allow_html=True)
    col = find_column(all_data['select'], [
        'Years of Potential Life Lost Rate', 'YPLL Rate', 'Premature Death Rate'
    ])
    if col:
        trend_df = get_trend(all_data['select'], col)
        df = trend_df[
            (trend_df['year'] >= year_range[0]) &
            (trend_df['year'] <= year_range[1])
        ].copy()
        if not show_ohio:
            df = df[df['geography'] == 'Hancock County']
        if not df.empty:
            fig2 = px.area(
                df, x='year', y=col, color='geography',
                labels={col: 'YPLL Rate (per 100k)', 'year': 'Year', 'geography': ''},
                color_discrete_map={'Hancock County': '#38ef7d', 'Ohio': '#4ECDC4'},
                template='plotly_dark'
            )
            fig2.update_traces(
                opacity=0.7, line=dict(width=2),
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>YPLL: %{y:,.0f}<extra></extra>'
            )
            fig2.update_layout(
                **LAYOUT_BASE,
                xaxis=dict(tickformat='d', dtick=1)
            )
            st.plotly_chart(fig2, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No YPLL data in selected year range.")

# ---- CHART 3: OUTCOMES COMPARISON BAR ----
if "Health Outcomes Comparison" in selected_charts:
    st.markdown('<div class="section-title">Health Outcomes — Hancock vs Ohio</div>', unsafe_allow_html=True)
    compare_df = pd.DataFrame({
        'Indicator': [
            'Injury Death Rate', 'Infant Mortality Rate',
            'Child Mortality Rate', 'Low Birth Weight %'
        ],
        'Hancock County': [injury_h, infant_h, child_mort_h, lbw_h],
        'Ohio': [injury_o, infant_o, child_mort_o, lbw_o]
    })
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    compare_melted = compare_df[['Indicator'] + cols_to_show].melt(
        id_vars='Indicator', var_name='Geography', value_name='Value'
    )
    fig3 = px.bar(
        compare_melted, x='Indicator', y='Value',
        color='Geography', barmode='group',
        color_discrete_map={'Hancock County': '#38ef7d', 'Ohio': '#4ECDC4'},
        labels={'Value': 'Rate / %', 'Indicator': ''},
        template='plotly_dark'
    )
    fig3.update_traces(
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<extra></extra>'
    )
    fig3.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig3, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 4: COUNTY RANKING ----
if "County Ranking" in selected_charts:
    st.markdown('<div class="section-title">Life Expectancy — Hancock Ranked Among All 88 Ohio Counties</div>', unsafe_allow_html=True)
    all_counties = get_all_counties(latest['additional'])
    if not all_counties.empty and 'Life Expectancy' in all_counties.columns:
        counties_clean = (
            all_counties[['County', 'Life Expectancy']]
            .dropna()
            .sort_values('Life Expectancy', ascending=True)
            .reset_index(drop=True)
        )
        total = len(counties_clean)
        hancock_idx = counties_clean[counties_clean['County'] == 'Hancock'].index
        hancock_rank_from_top = total - hancock_idx[0] if len(hancock_idx) > 0 else None

        counties_clean['highlight'] = counties_clean['County'].apply(
            lambda x: 'Hancock County' if x == 'Hancock' else 'Other Ohio Counties'
        )
        fig4 = px.bar(
            counties_clean,
            x='Life Expectancy', y='County',
            orientation='h', color='highlight',
            color_discrete_map={
                'Hancock County': '#38ef7d',
                'Other Ohio Counties': '#1D6B8A'
            },
            labels={'Life Expectancy': 'Life Expectancy (years)', 'County': ''},
            template='plotly_dark'
        )
        fig4.update_traces(
            hovertemplate='<b>%{y}</b><br>Life Expectancy: %{x:.1f} years<extra></extra>'
        )
        fig4.update_layout(
            **LAYOUT_BASE,
            height=2400,
            yaxis=dict(tickfont=dict(size=10)),
            xaxis=dict(range=[66, 82], title='Life Expectancy (years)'),
            bargap=0.12,
        )
        if hancock_rank_from_top:
            st.markdown(
                f"Hancock County ranks **#{hancock_rank_from_top} out of {total}** Ohio counties "
                f"for life expectancy at **{life_exp_h} years** — highlighted in green below."
            )
        st.plotly_chart(fig4, use_container_width=True, config=CHART_CONFIG)

# ---- DOWNLOAD ----
st.markdown("---")
export_df = pd.DataFrame({
    'Indicator': [
        'Life Expectancy (years)', 'YPLL Rate (per 100k)', 'Injury Death Rate',
        'Infant Mortality Rate', 'Child Mortality Rate', 'Low Birth Weight %'
    ],
    'Hancock County': [life_exp_h, ypll_h, injury_h, infant_h, child_mort_h, lbw_h],
    'Ohio': [life_exp_o, ypll_o, injury_o, infant_o, child_mort_o, lbw_o]
})
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Health Outcomes Data as CSV",
    data=csv,
    file_name=f"hancock_health_outcomes_{selected_year}.csv",
    mime="text/csv"
)
if st.checkbox("Show raw comparison data"):
    st.dataframe(export_df, use_container_width=True)

# ---- DISCLAIMER ----
render_disclaimer("Health Outcomes & Mortality")

# ---- SIDEBAR CHAT ----
render_sidebar_chat("Health Outcomes & Mortality")