import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_latest, load_all_years, get_ohio, get_trend, find_column
from utils.sidebar import render_sidebar, fetch_metric, kpi_delta, arrow, diff
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat, CHART_CONFIG, LAYOUT_BASE

st.set_page_config(page_title="👥 Demographics", page_icon="👥", layout="wide")

st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.purple { background: linear-gradient(135deg, #6a11cb, #a855f7); }
.kpi-card.blue   { background: linear-gradient(135deg, #1a6dff, #4facfe); }
.kpi-card.teal   { background: linear-gradient(135deg, #0f9b8e, #4ECDC4); }
.kpi-card.amber  { background: linear-gradient(135deg, #f7971e, #ffd200); }
.kpi-card.green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card.coral  { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
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
    background: rgba(168,85,247,0.2); color: #a855f7;
    border: 1px solid rgba(168,85,247,0.4); margin-bottom: 16px;
}
.headline-insight {
    background: linear-gradient(135deg, rgba(168,85,247,0.08), rgba(168,85,247,0.03));
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

# ---- CENTRALIZED SIDEBAR ----
selected_year, compare_year, show_ohio, selected_charts = render_sidebar(
    page_name="👥 Demographics",
    all_data=all_data,
    chart_options=[
        "Population Composition",
        "Age Distribution",
        "Race & Ethnicity",
        "Income by Race",
        "Single-Parent Households Trend",
        "Disability & Language",
    ]
)

# ---- METRIC HELPERS ----
def gm(col, county='Hancock', sheet='additional'):
    return fetch_metric(all_data, latest, selected_year, col, county, sheet)

def gmc(col, county='Hancock', sheet='additional'):
    if compare_year is None: return None
    return fetch_metric(all_data, latest, compare_year, col, county, sheet)

def safe(val, suffix='', prefix='', fallback='N/A'):
    if val is None: return fallback
    return f"{prefix}{val}{suffix}"

# ---- METRICS ----
pop_h           = gm('Population')
pop_o           = gm('Population', county='Ohio')
pct_under18_h   = gm('% Below 18 Years of Age')
pct_under18_o   = gm('% Below 18 Years of Age', county='Ohio')
pct_65plus_h    = gm('% 65 and Over')
pct_65plus_o    = gm('% 65 and Over', county='Ohio')
pct_female_h    = gm('% Female')
pct_female_o    = gm('% Female', county='Ohio')
pct_rural_h     = gm('% Rural')
pct_rural_o     = gm('% Rural', county='Ohio')
pct_white_h     = gm('% Non-Hispanic White')
pct_white_o     = gm('% Non-Hispanic White', county='Ohio')
pct_black_h     = gm('% Non-Hispanic Black')
pct_black_o     = gm('% Non-Hispanic Black', county='Ohio')
pct_hispanic_h  = gm('% Hispanic')
pct_hispanic_o  = gm('% Hispanic', county='Ohio')
pct_disabled_h  = gm('% with disability')
pct_disabled_o  = gm('% with disability', county='Ohio')
pct_noenglish_h = gm('% Not Proficient in English')
pct_noenglish_o = gm('% Not Proficient in English', county='Ohio')
pct_singlepar_h = gm('% Children in Single-Parent Households')
pct_singlepar_o = gm('% Children in Single-Parent Households', county='Ohio')
income_h        = gm('Median Household Income')
income_o        = gm('Median Household Income', county='Ohio')

# ---- COMPARE METRICS ----
pop_c          = gmc('Population')
pct_rural_c    = gmc('% Rural')
pct_65plus_c   = gmc('% 65 and Over')
pct_disabled_c = gmc('% with disability')
pct_singlepar_c = gmc('% Children in Single-Parent Households')
income_c       = gmc('Median Household Income')
income_c_int   = int(income_c) if income_c else None

# ---- HEADER ----
st.markdown(
    f"# 👥 Demographics & Population Profile "
    f"<span class='year-badge'>Showing: {selected_year}</span>",
    unsafe_allow_html=True
)
st.markdown('<div class="chip-tag">📊 POPULATION CONTEXT — ALL CHIP PRIORITIES</div>', unsafe_allow_html=True)
st.markdown("Who lives in Hancock County — age, race, income, and community characteristics.")

# ---- HEADLINE INSIGHT ----
st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Population Profile ({selected_year}):</strong> Hancock County has a population of
    <strong>{int(pop_h):,}</strong> residents. The county is predominantly rural at
    <strong>{safe(pct_rural_h, '%')}</strong> vs {safe(pct_rural_o, '%')} for Ohio,
    with a higher share of residents aged 65+ at <strong>{safe(pct_65plus_h, '%')}</strong>.
    Understanding the demographic makeup is essential context for all three CHIP priorities —
    an aging, rural population shapes both health needs and service delivery challenges.
</div>
""", unsafe_allow_html=True)

render_ai_banner("Demographics & Population Profile")

# ---- KPI ROW 1 ----
st.markdown('<div class="section-title">Population Overview</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card purple">
        <div class="kpi-icon">👥</div>
        <div class="kpi-label">Total Population</div>
        <div class="kpi-value">{int(pop_h):,}</div>
        <div class="kpi-sub">Ohio: {int(pop_o):,} · Hancock is {round(pop_h/pop_o*100, 2)}% of state</div>
        <div class="kpi-delta">{kpi_delta(pop_h, pop_c, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-icon">🏡</div>
        <div class="kpi-label">Rural Population</div>
        <div class="kpi-value">{safe(pct_rural_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_rural_o, '%')} · {arrow(pct_rural_h, pct_rural_o, lower_is_better=False)} {diff(pct_rural_h, pct_rural_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(pct_rural_h, pct_rural_c, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">👩</div>
        <div class="kpi-label">Female Population</div>
        <div class="kpi-value">{safe(pct_female_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_female_o, '%')}</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Median Household Income</div>
        <div class="kpi-value">${int(income_h):,}</div>
        <div class="kpi-sub">Ohio: ${int(income_o):,} · {arrow(income_h, income_o, lower_is_better=False)} ${diff(income_h, income_o):,.0f} vs state</div>
        <div class="kpi-delta">{kpi_delta(int(income_h) if income_h else None, income_c_int, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 2 ----
st.markdown('<div class="section-title"> </div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card blue">
        <div class="kpi-icon">👶</div>
        <div class="kpi-label">Under 18 Years</div>
        <div class="kpi-value">{safe(pct_under18_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_under18_o, '%')} · {arrow(pct_under18_h, pct_under18_o, lower_is_better=False)} {diff(pct_under18_h, pct_under18_o)}% vs state</div>
    </div>
    <div class="kpi-card coral">
        <div class="kpi-icon">👴</div>
        <div class="kpi-label">65 Years and Older</div>
        <div class="kpi-value">{safe(pct_65plus_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_65plus_o, '%')} · {arrow(pct_65plus_h, pct_65plus_o, lower_is_better=False)} {diff(pct_65plus_h, pct_65plus_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(pct_65plus_h, pct_65plus_c, compare_year=compare_year, lower_is_better=False)}</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">♿</div>
        <div class="kpi-label">Disability Rate</div>
        <div class="kpi-value">{safe(pct_disabled_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_disabled_o, '%')} · {arrow(pct_disabled_h, pct_disabled_o)} {diff(pct_disabled_h, pct_disabled_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(pct_disabled_h, pct_disabled_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-icon">👨‍👦</div>
        <div class="kpi-label">Single-Parent Households</div>
        <div class="kpi-value">{safe(pct_singlepar_h, '%')}</div>
        <div class="kpi-sub">Ohio: {safe(pct_singlepar_o, '%')} · {arrow(pct_singlepar_h, pct_singlepar_o)} {diff(pct_singlepar_h, pct_singlepar_o)}% vs state</div>
        <div class="kpi-delta">{kpi_delta(pct_singlepar_h, pct_singlepar_c, compare_year=compare_year, lower_is_better=True)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- CHART 1: POPULATION COMPOSITION ----
if "Population Composition" in selected_charts:
    st.markdown(f'<div class="section-title">Population Composition — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    comp_data = pd.DataFrame({
        'Category': ['Under 18', '65 and Older', 'Rural', 'Female', 'Disabled', 'Single-Parent HH'],
        'Hancock County': [pct_under18_h, pct_65plus_h, pct_rural_h, pct_female_h, pct_disabled_h, pct_singlepar_h],
        'Ohio': [pct_under18_o, pct_65plus_o, pct_rural_o, pct_female_o, pct_disabled_o, pct_singlepar_o]
    }).dropna()
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    comp_melted = comp_data[['Category'] + cols_to_show].melt(id_vars='Category', var_name='Geography', value_name='Percentage')
    fig1 = px.bar(comp_melted, x='Category', y='Percentage', color='Geography', barmode='group',
                  color_discrete_map={'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
                  labels={'Percentage': 'Percentage (%)', 'Category': ''}, template='plotly_dark')
    fig1.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    fig1.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig1, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 2: AGE DISTRIBUTION PIE ----
if "Age Distribution" in selected_charts:
    st.markdown('<div class="section-title">Age Distribution — Hancock County</div>', unsafe_allow_html=True)
    pct_working = round(100 - (pct_under18_h or 0) - (pct_65plus_h or 0), 1)
    age_df = pd.DataFrame({
        'Age Group': ['Under 18', 'Working Age (18–64)', '65 and Older'],
        'Percentage': [pct_under18_h or 0, pct_working, pct_65plus_h or 0]
    })
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Hancock County**")
        fig2a = px.pie(age_df, values='Percentage', names='Age Group',
                       color_discrete_sequence=['#a855f7', '#4ECDC4', '#ffd200'],
                       template='plotly_dark', hole=0.45)
        fig2a.update_traces(hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>', textinfo='label+percent')
        fig2a.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
                            legend=dict(orientation='h', y=-0.2), margin=dict(t=20, b=20))
        st.plotly_chart(fig2a, use_container_width=True, config=CHART_CONFIG)
    if show_ohio:
        with col2:
            pct_working_o = round(100 - (pct_under18_o or 0) - (pct_65plus_o or 0), 1)
            age_df_o = pd.DataFrame({
                'Age Group': ['Under 18', 'Working Age (18–64)', '65 and Older'],
                'Percentage': [pct_under18_o or 0, pct_working_o, pct_65plus_o or 0]
            })
            st.markdown("**Ohio**")
            fig2b = px.pie(age_df_o, values='Percentage', names='Age Group',
                           color_discrete_sequence=['#a855f7', '#4ECDC4', '#ffd200'],
                           template='plotly_dark', hole=0.45)
            fig2b.update_traces(hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>', textinfo='label+percent')
            fig2b.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
                                legend=dict(orientation='h', y=-0.2), margin=dict(t=20, b=20))
            st.plotly_chart(fig2b, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 3: RACE & ETHNICITY ----
if "Race & Ethnicity" in selected_charts:
    st.markdown(f'<div class="section-title">Race & Ethnicity — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    race_data = pd.DataFrame({
        'Group': ['Non-Hispanic White', 'Non-Hispanic Black', 'Hispanic', 'Other/Mixed'],
        'Hancock County': [pct_white_h or 0, pct_black_h or 0, pct_hispanic_h or 0,
                           round(100 - (pct_white_h or 0) - (pct_black_h or 0) - (pct_hispanic_h or 0), 1)],
        'Ohio': [pct_white_o or 0, pct_black_o or 0, pct_hispanic_o or 0,
                 round(100 - (pct_white_o or 0) - (pct_black_o or 0) - (pct_hispanic_o or 0), 1)]
    })
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    race_melted = race_data[['Group'] + cols_to_show].melt(id_vars='Group', var_name='Geography', value_name='Percentage')
    fig3 = px.bar(race_melted, x='Group', y='Percentage', color='Geography', barmode='group',
                  color_discrete_map={'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
                  labels={'Percentage': 'Percentage (%)', 'Group': ''}, template='plotly_dark')
    fig3.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    fig3.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig3, use_container_width=True, config=CHART_CONFIG)

# ---- CHART 4: INCOME BY RACE ----
if "Income by Race" in selected_charts:
    st.markdown('<div class="section-title">Median Household Income by Race — Ohio Context</div>', unsafe_allow_html=True)
    st.markdown("*Ohio-level income by race shown as context — county-level racial income breakdowns are not available in CHR data.*")
    ohio_row = get_ohio(latest['additional'])
    income_race_cols = {'White': 'Household Income (White)', 'Black': 'Household Income (Black)',
                        'Hispanic': 'Household Income (Hispanic)', 'Asian': 'Household Income (Asian)',
                        'AIAN': 'Household Income (AIAN)'}
    income_race_data = []
    for label, col in income_race_cols.items():
        if col in ohio_row.index and pd.notna(ohio_row[col]):
            income_race_data.append({'Race/Ethnicity': label, 'Median Income ($)': round(ohio_row[col])})
    if income_race_data:
        income_race_df = pd.DataFrame(income_race_data).sort_values('Median Income ($)', ascending=True)
        fig4 = px.bar(income_race_df, x='Median Income ($)', y='Race/Ethnicity', orientation='h',
                      color='Median Income ($)', color_continuous_scale=['#ff416c', '#ffd200', '#38ef7d'],
                      labels={'Median Income ($)': 'Median Household Income ($)', 'Race/Ethnicity': ''},
                      template='plotly_dark')
        fig4.update_traces(hovertemplate='<b>%{y}</b><br>Median Income: $%{x:,.0f}<extra></extra>')
        fig4.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
                           xaxis=dict(tickprefix='$', tickformat=','))
        if income_h:
            fig4.add_vline(x=income_h, line_dash='dash', line_color='#a855f7', opacity=0.8,
                           annotation_text=f'Hancock County: ${int(income_h):,}',
                           annotation_position='top right', annotation_font_color='#a855f7')
        st.plotly_chart(fig4, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Income by race data not available.")

# ---- CHART 5: SINGLE-PARENT TREND ----
if "Single-Parent Households Trend" in selected_charts:
    st.markdown('<div class="section-title">Children in Single-Parent Households — Trend Up To Selected Year</div>', unsafe_allow_html=True)
    col = find_column(all_data['additional'], ['% Children in Single-Parent Households', '% Single-Parent Households'])
    if col:
        trend_df = get_trend(all_data['additional'], col)
        df = trend_df[trend_df['year'] <= selected_year].copy()
        if not show_ohio:
            df = df[df['geography'] == 'Hancock County']
        if not df.empty:
            fig5 = px.scatter(df, x='year', y=col, color='geography',
                              color_discrete_map={'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
                              template='plotly_dark')
            for trace in fig5.data:
                geo_data = df[df['geography'] == trace.name]
                trace.mode = 'lines+markers' if len(geo_data) > 1 else 'markers'
                trace.line = dict(width=3)
                trace.marker = dict(size=9)
                trace.hovertemplate = '<b>%{fullData.name}</b><br>Year: %{x}<br>Single-Parent HH: %{y:.1f}%<extra></extra>'
            fig5.update_layout(**LAYOUT_BASE, xaxis=dict(tickformat='d', dtick=1),
                               yaxis=dict(title='Children in Single-Parent HH (%)'))
            st.plotly_chart(fig5, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No single-parent household data available.")

# ---- CHART 6: DISABILITY & LANGUAGE ----
if "Disability & Language" in selected_charts:
    st.markdown(f'<div class="section-title">Disability & Language Access — Hancock vs Ohio ({selected_year})</div>', unsafe_allow_html=True)
    access_data = pd.DataFrame({
        'Indicator': ['Disability Rate %', 'Not Proficient in English %'],
        'Hancock County': [pct_disabled_h or 0, pct_noenglish_h or 0],
        'Ohio': [pct_disabled_o or 0, pct_noenglish_o or 0]
    })
    cols_to_show = ['Hancock County', 'Ohio'] if show_ohio else ['Hancock County']
    access_melted = access_data[['Indicator'] + cols_to_show].melt(id_vars='Indicator', var_name='Geography', value_name='Value')
    fig6 = px.bar(access_melted, x='Indicator', y='Value', color='Geography', barmode='group',
                  color_discrete_map={'Hancock County': '#a855f7', 'Ohio': '#4ECDC4'},
                  labels={'Value': 'Percentage (%)', 'Indicator': ''}, template='plotly_dark')
    fig6.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    fig6.update_layout(**LAYOUT_BASE)
    st.plotly_chart(fig6, use_container_width=True, config=CHART_CONFIG)

# ---- DOWNLOAD ----
st.markdown("---")
export_df = pd.DataFrame({
    'Indicator': ['Total Population', 'Rural %', 'Female %', 'Under 18 %', '65 and Older %',
                  'Non-Hispanic White %', 'Non-Hispanic Black %', 'Hispanic %',
                  'Disability Rate %', 'Not Proficient in English %',
                  'Single-Parent Households %', 'Median Household Income'],
    'Hancock County': [int(pop_h) if pop_h else None, pct_rural_h, pct_female_h, pct_under18_h,
                       pct_65plus_h, pct_white_h, pct_black_h, pct_hispanic_h, pct_disabled_h,
                       pct_noenglish_h, pct_singlepar_h, int(income_h) if income_h else None],
    'Ohio': [int(pop_o) if pop_o else None, pct_rural_o, pct_female_o, pct_under18_o,
             pct_65plus_o, pct_white_o, pct_black_o, pct_hispanic_o, pct_disabled_o,
             pct_noenglish_o, pct_singlepar_o, int(income_o) if income_o else None]
})
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Demographics Data as CSV", data=csv,
                   file_name=f"hancock_demographics_{selected_year}.csv", mime="text/csv")
if st.checkbox("Show raw comparison data"):
    st.dataframe(export_df, use_container_width=True)

render_disclaimer("Demographics & Population Profile")
render_sidebar_chat("Demographics & Population Profile")
