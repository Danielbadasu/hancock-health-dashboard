import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_latest, load_all_years, get_trend, find_column
from utils.sidebar import render_sidebar, fetch_metric, kpi_delta, arrow, diff
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat, CHART_CONFIG, LAYOUT_BASE

st.set_page_config(page_title="🌍 Social Factors", page_icon="🌍", layout="wide")

st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.teal   { background: linear-gradient(135deg, #0f9b8e, #4ECDC4); }
.kpi-card.amber  { background: linear-gradient(135deg, #f7971e, #ffd200); }
.kpi-card.green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card.coral  { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
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
.kpi-delta { font-size: 10px; margin-top: 4px; }
.kpi-icon { position: absolute; top: 18px; right: 20px; font-size: 42px; opacity: 0.25; }
.chip-tag {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    background: rgba(78,205,196,0.2); color: #4ECDC4;
    border: 1px solid rgba(78,205,196,0.4); margin-bottom: 16px;
}
.headline-insight {
    background: linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05));
    border: 1px solid rgba(78,205,196,0.3);
    border-left: 4px solid #4ECDC4;
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
    background: rgba(78,205,196,0.2); color: #4ECDC4;
    border: 1px solid rgba(78,205,196,0.3);
    margin-left: 8px; vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
latest   = load_latest()
all_data = load_all_years()

# ---- CENTRALIZED SIDEBAR ----
selected_year, compare_year, show_ohio, selected_charts = render_sidebar(
    page_name="🌍 Social Factors",
    all_data=all_data,
    chart_options=[
        "Social Indicators Comparison",
        "Income Trend",
        "Children in Poverty Trend",
        "Community Conditions Radar",
    ]
)

# ---- METRIC HELPERS ----
def gm(col, county='Hancock', sheet='additional'):
    return fetch_metric(all_data, latest, selected_year, col, county, sheet)

def gmc(col, county='Hancock', sheet='additional'):
    if compare_year is None: return None
    return fetch_metric(all_data, latest, compare_year, col, county, sheet)

# ---- METRICS ----
income_h    = gm('Median Household Income')
income_o    = gm('Median Household Income', county='Ohio')
poverty_h   = gm('% Children in Poverty', sheet='select')
poverty_o   = gm('% Children in Poverty', county='Ohio', sheet='select')
food_h      = gm('% Food Insecure')
food_o      = gm('% Food Insecure', county='Ohio')
housing_h   = gm('% Severe Housing Problems', sheet='select')
housing_o   = gm('% Severe Housing Problems', county='Ohio', sheet='select')
college_h   = gm('% Some College', sheet='select')
college_o   = gm('% Some College', county='Ohio', sheet='select')
unemploy_h  = gm('% Unemployed', sheet='select')
unemploy_o  = gm('% Unemployed', county='Ohio', sheet='select')
broadband_h = gm('% Households with Broadband Access', sheet='select')
broadband_o = gm('% Households with Broadband Access', county='Ohio', sheet='select')
exercise_h  = gm('% With Access to Exercise Opportunities', sheet='select')
exercise_o  = gm('% With Access to Exercise Opportunities', county='Ohio', sheet='select')

income_h_int = int(income_h) if income_h else 0
income_o_int = int(income_o) if income_o else 0

# ---- COMPARE METRICS ----
income_c    = gmc('Median Household Income')
poverty_c   = gmc('% Children in Poverty', sheet='select')
food_c      = gmc('% Food Insecure')
housing_c   = gmc('% Severe Housing Problems', sheet='select')
college_c   = gmc('% Some College', sheet='select')
unemploy_c  = gmc('% Unemployed', sheet='select')
broadband_c = gmc('% Households with Broadband Access', sheet='select')
exercise_c  = gmc('% With Access to Exercise Opportunities', sheet='select')

income_c_int = int(income_c) if income_c else None

# ---- HEADER ----
st.markdown(
    f"# 🌍 Social Determinants & Built Environment "
    f"<span class='year-badge'>Showing: {selected_year}</span>",
    unsafe_allow_html=True
)
st.markdown('<div class="chip-tag">🏥 CHIP PRIORITY 2</div>', unsafe_allow_html=True)
st.markdown("Income, housing, education, food security, and community conditions for Hancock County vs Ohio.")

# ---- HEADLINE INSIGHT ----
income_diff = income_h_int - income_o_int
st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Key Finding ({selected_year}):</strong> Hancock County households earn a median of
    <strong>${income_h_int:,}</strong> — ${abs(income_diff):,}
    {'above' if income_diff > 0 else 'below'} the Ohio average of ${income_o_int:,}.
    Children in poverty stand at just <strong>{poverty_h}%</strong> vs {poverty_o}% statewide.
    However, <strong>{food_h}%</strong> of residents face food insecurity and only
    <strong>{exercise_h}%</strong> have access to exercise opportunities vs {exercise_o}% for Ohio
    — key gaps the CHIP Priority 2 targets.
</div>
""", unsafe_allow_html=True)

render_ai_banner("Social Determinants & Built Environment")

# ---- KPI ROW 1 ----
st.markdown('<div class="section-title">Key Indicators</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card green">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Median Household Income</div>
        <div class="kpi-value">${income_h_int:,}</div>
        <div class="kpi-sub">Ohio: ${income_o_int:,} · {arrow(income_h, income_o, lower_is_better=False)} ${diff(income_h, income_o):,.0f} vs state</div>
        <div class="kpi-delta">{kpi_delta(income_h_int, income_c_int, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">👶</div>
        <div class="kpi-label">Children in Poverty</div>
        <div class="kpi-value">{poverty_h}%</div>
        <div class="kpi-sub">Ohio: {poverty_o}% · {arrow(poverty_h, poverty_o)} {diff(poverty_h, poverty_o)}% better than state</div>
        <div class="kpi-delta">{kpi_delta(poverty_h, poverty_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-icon">🍎</div>
        <div class="kpi-label">Food Insecurity</div>
        <div class="kpi-value">{food_h}%</div>
        <div class="kpi-sub">Ohio: {food_o}% · {arrow(food_h, food_o)} {diff(food_h, food_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(food_h, food_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
    <div class="kpi-card coral">
        <div class="kpi-icon">🏠</div>
        <div class="kpi-label">Severe Housing Problems</div>
        <div class="kpi-value">{housing_h}%</div>
        <div class="kpi-sub">Ohio: {housing_o}% · {arrow(housing_h, housing_o)} {diff(housing_h, housing_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(housing_h, housing_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 2 ----
st.markdown('<div class="section-title"> </div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card teal">
        <div class="kpi-icon">🎓</div>
        <div class="kpi-label">Some College Education</div>
        <div class="kpi-value">{college_h}%</div>
        <div class="kpi-sub">Ohio: {college_o}% · {arrow(college_h, college_o, lower_is_better=False)} {diff(college_h, college_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(college_h, college_c, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-icon">💼</div>
        <div class="kpi-label">Unemployment Rate</div>
        <div class="kpi-value">{unemploy_h}%</div>
        <div class="kpi-sub">Ohio: {unemploy_o}% · {arrow(unemploy_h, unemploy_o)} {diff(unemploy_h, unemploy_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(unemploy_h, unemploy_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-icon">🌐</div>
        <div class="kpi-label">Broadband Access</div>
        <div class="kpi-value">{broadband_h}%</div>
        <div class="kpi-sub">Ohio: {broadband_o}% · {arrow(broadband_h, broadband_o, lower_is_better=False)} {diff(broadband_h, broadband_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(broadband_h, broadband_c, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card coral">
        <div class="kpi-icon">🏃</div>
        <div class="kpi-label">Exercise Access</div>
        <div class="kpi-value">{exercise_h}%</div>
        <div class="kpi-sub">Ohio: {exercise_o}% · {arrow(exercise_h, exercise_o, lower_is_better=False)} {diff(exercise_h, exercise_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(exercise_h, exercise_c, compare_year=compare_year, lower_is_better=False)}</div>
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

# ---- CHART 1: SOCIAL INDICATORS COMPARISON ----
if "Social Indicators Comparison" in selected_charts:
    st.markdown(f'<div class="section-title">Social Indicators — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    compare_df = pd.DataFrame({
        'Indicator': ['Food Insecurity %', 'Severe Housing %', 'Unemployment %', 'Children in Poverty %'],
        'Hancock County': [food_h, housing_h, unemploy_h, poverty_h],
        'Ohio': [food_o, housing_o, unemploy_o, poverty_o]
    })
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    compare_melted = compare_df[['Indicator'] + cols_to_show].melt(id_vars='Indicator', var_name='Geography', value_name='Value')
    fig1 = px.bar(compare_melted, x='Indicator', y='Value', color='Geography', barmode='group',
                  color_discrete_map={'Hancock County': '#4ECDC4', 'Ohio': '#ffd200'},
                  labels={'Value': 'Percentage (%)', 'Indicator': ''}, template='plotly_dark')
    fig1.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    fig1.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig1, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 2: INCOME TREND ----
if "Income Trend" in selected_charts:
    st.markdown('<div class="section-title">Median Household Income — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['Median Household Income', 'Median Income'])
    if col:
        fig = make_trend_chart(get_trend(all_data['additional'], col), col,
                               {'Hancock County': '#4ECDC4', 'Ohio': '#ffd200'}, 'Median Income ($)', '')
        if fig:
            fig.update_layout(yaxis=dict(tickprefix='$', tickformat=','))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No income data available.")

# ---- CHART 3: CHILDREN IN POVERTY TREND ----
if "Children in Poverty Trend" in selected_charts:
    st.markdown('<div class="section-title">Children in Poverty — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['select'], ['% Children in Poverty', 'Children in Poverty %'])
    if col:
        fig = make_trend_chart(get_trend(all_data['select'], col), col,
                               {'Hancock County': '#4ECDC4', 'Ohio': '#ffd200'}, 'Children in Poverty', '%')
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No poverty data available.")

# ---- CHART 4: COMMUNITY CONDITIONS RADAR ----
if "Community Conditions Radar" in selected_charts:
    st.markdown(f'<div class="section-title">Community Conditions — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    categories = ['College Education', 'Broadband Access', 'Exercise Access',
                  'Food Security', 'Employment', 'Housing Quality']
    hancock_vals = [college_h or 0, broadband_h or 0, exercise_h or 0,
                    100 - (food_h or 0), 100 - (unemploy_h or 0), 100 - (housing_h or 0)]
    ohio_vals    = [college_o or 0, broadband_o or 0, exercise_o or 0,
                    100 - (food_o or 0), 100 - (unemploy_o or 0), 100 - (housing_o or 0)]
    fig4 = go.Figure()
    fig4.add_trace(go.Scatterpolar(
        r=hancock_vals, theta=categories, fill='toself',
        name='Hancock County', line_color='#4ECDC4',
        fillcolor='rgba(78,205,196,0.2)',
        hovertemplate='<b>Hancock County</b><br>%{theta}: %{r:.1f}<extra></extra>'
    ))
    if show_ohio:
        fig4.add_trace(go.Scatterpolar(
            r=ohio_vals, theta=categories, fill='toself',
            name='Ohio', line_color='#ffd200',
            fillcolor='rgba(255,210,0,0.1)',
            hovertemplate='<b>Ohio</b><br>%{theta}: %{r:.1f}<extra></extra>'
        ))
    fig4.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        hoverlabel=dict(bgcolor='#1a1a2e', font_size=13)
    )
    st.plotly_chart(fig4, use_container_width=True, config=CHART_CONFIG)

# ---- DOWNLOAD ----
st.markdown("---")
export_df = pd.DataFrame({
    'Indicator': ['Median Household Income', 'Children in Poverty %', 'Food Insecurity %',
                  'Severe Housing Problems %', 'Some College %', 'Unemployment %',
                  'Broadband Access %', 'Exercise Access %'],
    'Hancock County': [income_h_int, poverty_h, food_h, housing_h, college_h, unemploy_h, broadband_h, exercise_h],
    'Ohio': [income_o_int, poverty_o, food_o, housing_o, college_o, unemploy_o, broadband_o, exercise_o]
})
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Social Factors Data as CSV", data=csv,
                   file_name=f"hancock_social_factors_{selected_year}.csv", mime="text/csv")
if st.checkbox("Show raw comparison data"):
    st.dataframe(export_df, use_container_width=True)

render_disclaimer("Social Determinants & Built Environment")
render_sidebar_chat("Social Determinants & Built Environment")
