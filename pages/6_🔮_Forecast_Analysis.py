import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader import (
    load_latest, load_all_years, get_hancock, get_ohio, get_trend, find_column
)
from chatbot_widget import render_ai_banner, render_disclaimer, render_sidebar_chat

st.set_page_config(page_title="🔮 Forecast Analysis", page_icon="🔮", layout="wide")

# ---- CSS ----
st.markdown("""
<style>
.kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
.kpi-card {
    flex: 1; padding: 24px 28px; border-radius: 16px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.purple { background: linear-gradient(135deg, #6a11cb, #a855f7); }
.kpi-card.green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card.amber  { background: linear-gradient(135deg, #f7971e, #ffd200); }
.kpi-card.red    { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
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
.scenario-box {
    border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;
    font-size: 13px; line-height: 1.6;
}
.scenario-optimistic {
    background: rgba(56,239,125,0.08);
    border: 1px solid rgba(56,239,125,0.3);
    border-left: 4px solid #38ef7d;
}
.scenario-moderate {
    background: rgba(255,210,0,0.08);
    border: 1px solid rgba(255,210,0,0.3);
    border-left: 4px solid #ffd200;
}
.scenario-pessimistic {
    background: rgba(255,65,108,0.08);
    border: 1px solid rgba(255,65,108,0.3);
    border-left: 4px solid #ff416c;
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

hancock_a = get_hancock(latest['additional'])
ohio_a    = get_ohio(latest['additional'])
hancock_s = get_hancock(latest['select'])
ohio_s    = get_ohio(latest['select'])

# ---- SIDEBAR ----
st.sidebar.header("Simulation Settings")

scenario = st.sidebar.radio(
    "Select Scenario",
    options=["🟢 Optimistic", "🟡 Moderate", "🔴 Pessimistic"],
    index=1
)

target_year = st.sidebar.slider(
    "Project to Year",
    min_value=2026,
    max_value=2040,
    value=2030,
    step=1
)

selected_metrics = st.sidebar.multiselect(
    "Metrics to Project",
    options=[
        "Drug Overdose Rate",
        "Life Expectancy",
        "Adult Obesity",
        "Mental Health Providers",
        "Children in Poverty",
        "Physical Inactivity",
    ],
    default=[
        "Drug Overdose Rate",
        "Life Expectancy",
        "Adult Obesity",
        "Mental Health Providers",
        "Children in Poverty",
        "Physical Inactivity",
    ]
)

show_ohio = st.sidebar.toggle("Show Ohio Benchmark", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Scenario Guide")
st.sidebar.markdown("🟢 **Optimistic** — CHIP fully implemented, strong community investment")
st.sidebar.markdown("🟡 **Moderate** — Current pace continues, partial CHIP implementation")
st.sidebar.markdown("🔴 **Pessimistic** — Resource constraints, trends worsen")

# ---- SCENARIO CONFIG ----
scenarios = {
    "🟢 Optimistic": {
        "color": "#38ef7d",
        "label": "Aggressive CHIP implementation — strong investment in all 3 priority areas",
        "rates": {
            "Drug Overdose Rate":      -0.05,
            "Life Expectancy":         +0.008,
            "Adult Obesity":           -0.02,
            "Mental Health Providers": +0.04,
            "Children in Poverty":     -0.03,
            "Physical Inactivity":     -0.025,
        }
    },
    "🟡 Moderate": {
        "color": "#ffd200",
        "label": "Current pace — partial CHIP implementation, steady progress",
        "rates": {
            "Drug Overdose Rate":      -0.02,
            "Life Expectancy":         +0.003,
            "Adult Obesity":           +0.005,
            "Mental Health Providers": +0.015,
            "Children in Poverty":     -0.01,
            "Physical Inactivity":     +0.005,
        }
    },
    "🔴 Pessimistic": {
        "color": "#ff416c",
        "label": "Resource constraints — CHIP underfunded, trends worsen",
        "rates": {
            "Drug Overdose Rate":      +0.03,
            "Life Expectancy":         -0.002,
            "Adult Obesity":           +0.02,
            "Mental Health Providers": -0.01,
            "Children in Poverty":     +0.02,
            "Physical Inactivity":     +0.02,
        }
    }
}

config = scenarios[scenario]
years_ahead = target_year - 2025

# ---- BASE VALUES (2025) ----
base_values = {
    "Drug Overdose Rate":      round(hancock_a['Drug Overdose Mortality Rate'], 1),
    "Life Expectancy":         round(hancock_a['Life Expectancy'], 1),
    "Adult Obesity":           round(hancock_a['% Adults with Obesity'], 1),
    "Mental Health Providers": round(hancock_s['Mental Health Provider Rate']),
    "Children in Poverty":     round(hancock_s['% Children in Poverty'], 1),
    "Physical Inactivity":     round(hancock_a['% Physically Inactive'], 1),
}

ohio_values = {
    "Drug Overdose Rate":      round(ohio_a['Drug Overdose Mortality Rate'], 1),
    "Life Expectancy":         round(ohio_a['Life Expectancy'], 1),
    "Adult Obesity":           round(ohio_a['% Adults with Obesity'], 1),
    "Mental Health Providers": round(ohio_s['Mental Health Provider Rate']),
    "Children in Poverty":     round(ohio_s['% Children in Poverty'], 1),
    "Physical Inactivity":     round(ohio_a['% Physically Inactive'], 1),
}

units = {
    "Drug Overdose Rate":      "per 100k",
    "Life Expectancy":         "years",
    "Adult Obesity":           "%",
    "Mental Health Providers": "per 100k",
    "Children in Poverty":     "%",
    "Physical Inactivity":     "%",
}

lower_is_better = {
    "Drug Overdose Rate":      True,
    "Life Expectancy":         False,
    "Adult Obesity":           True,
    "Mental Health Providers": False,
    "Children in Poverty":     True,
    "Physical Inactivity":     True,
}

card_colors = {
    "Drug Overdose Rate":      "red",
    "Life Expectancy":         "teal",
    "Adult Obesity":           "amber",
    "Mental Health Providers": "purple",
    "Children in Poverty":     "green",
    "Physical Inactivity":     "amber",
}

# ---- PROJECTED VALUES ----
def project(base, rate, years):
    return round(base * ((1 + rate) ** years), 1)

projected = {
    m: project(base_values[m], config['rates'][m], years_ahead)
    for m in base_values
}

# ---- HEADER ----
st.markdown("# 🔮 Forecast Analysis")
st.markdown('<div class="chip-tag">📊 CHIP SCENARIO SIMULATOR</div>', unsafe_allow_html=True)
st.markdown(f"Projecting Hancock County health metrics to **{target_year}** under the **{scenario}** scenario.")

# ---- HEADLINE INSIGHT ----
overdose_proj  = projected["Drug Overdose Rate"]
life_proj      = projected["Life Expectancy"]
overdose_base  = base_values["Drug Overdose Rate"]
life_base      = base_values["Life Expectancy"]

st.markdown(f"""
<div class="headline-insight">
    💡 <strong>{scenario} Scenario to {target_year}:</strong> {config['label']}.
    Under this scenario, Hancock County's drug overdose death rate is projected to reach
    <strong>{overdose_proj} per 100k</strong> (from {overdose_base} in 2025) and life expectancy
    is projected at <strong>{life_proj} years</strong> (from {life_base} in 2025).
    These projections are mathematical estimates based on current trends — not official forecasts.
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Health Forecast & Scenario Analysis")

# ---- SCENARIO DESCRIPTION BOXES ----
st.markdown('<div class="section-title">Scenario Descriptions</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="scenario-box scenario-optimistic">
        <strong>🟢 Optimistic</strong><br>
        Full CHIP implementation. Strong funding for behavioral health, social determinants,
        and chronic disease prevention. Community partnerships active.
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="scenario-box scenario-moderate">
        <strong>🟡 Moderate</strong><br>
        Partial CHIP implementation. Current trends continue with incremental improvements.
        Resource constraints limit some initiatives.
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="scenario-box scenario-pessimistic">
        <strong>🔴 Pessimistic</strong><br>
        CHIP underfunded. Economic pressures worsen social determinants.
        Health outcomes stagnate or decline without intervention.
    </div>
    """, unsafe_allow_html=True)

# ---- KPI CARDS — 2025 vs PROJECTED ----
st.markdown(f'<div class="section-title">2025 Baseline vs {target_year} Projection</div>', unsafe_allow_html=True)

metric_list = [m for m in selected_metrics if m in base_values]
rows = [metric_list[i:i+4] for i in range(0, len(metric_list), 4)]

for row in rows:
    cols = st.columns(len(row))
    card_html = '<div class="kpi-container">'
    for m in row:
        base  = base_values[m]
        proj  = projected[m]
        unit  = units[m]
        color = card_colors[m]
        lib   = lower_is_better[m]
        change = round(proj - base, 1)
        direction = '▼' if change < 0 else '▲'
        good = (change < 0 and lib) or (change > 0 and not lib)
        sentiment = '✅' if good else '⚠️'
        card_html += f"""
        <div class="kpi-card {color}">
            <div class="kpi-icon">{sentiment}</div>
            <div class="kpi-label">{m}</div>
            <div class="kpi-value">{proj} <span style="font-size:16px">{unit}</span></div>
            <div class="kpi-sub">2025 baseline: {base} {unit} · {direction} {abs(change)} projected change</div>
        </div>"""
    card_html += '</div>'
    st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")

# ---- PROJECTION CHARTS ----
projection_years = list(range(2025, target_year + 1))

for metric in selected_metrics:
    if metric not in base_values:
        continue

    st.markdown(f'<div class="section-title">{metric} — Projection to {target_year}</div>', unsafe_allow_html=True)

    base  = base_values[metric]
    rate  = config['rates'][metric]
    unit  = units[metric]
    color = config['color']

    # Build all three scenario projections
    opt_vals  = [project(base, scenarios["🟢 Optimistic"]['rates'][metric], i) for i in range(len(projection_years))]
    mod_vals  = [project(base, scenarios["🟡 Moderate"]['rates'][metric], i) for i in range(len(projection_years))]
    pes_vals  = [project(base, scenarios["🔴 Pessimistic"]['rates'][metric], i) for i in range(len(projection_years))]

    fig = go.Figure()

    # Shaded uncertainty band between optimistic and pessimistic
    fig.add_trace(go.Scatter(
        x=projection_years + projection_years[::-1],
        y=opt_vals + pes_vals[::-1],
        fill='toself',
        fillcolor='rgba(168,85,247,0.08)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Scenario Range',
        hoverinfo='skip',
        showlegend=True
    ))

    # Optimistic line
    fig.add_trace(go.Scatter(
        x=projection_years, y=opt_vals,
        mode='lines', name='Optimistic',
        line=dict(color='#38ef7d', width=2, dash='dash'),
        hovertemplate=f'<b>Optimistic</b><br>Year: %{{x}}<br>{metric}: %{{y:.1f}} {unit}<extra></extra>'
    ))

    # Pessimistic line
    fig.add_trace(go.Scatter(
        x=projection_years, y=pes_vals,
        mode='lines', name='Pessimistic',
        line=dict(color='#ff416c', width=2, dash='dash'),
        hovertemplate=f'<b>Pessimistic</b><br>Year: %{{x}}<br>{metric}: %{{y:.1f}} {unit}<extra></extra>'
    ))

    # Selected scenario (bold)
    fig.add_trace(go.Scatter(
        x=projection_years, y=mod_vals,
        mode='lines+markers', name=f'{scenario} (Selected)',
        line=dict(color=color, width=4),
        marker=dict(size=7),
        hovertemplate=f'<b>{scenario}</b><br>Year: %{{x}}<br>{metric}: %{{y:.1f}} {unit}<extra></extra>'
    ))

    # Ohio benchmark line
    if show_ohio and metric in ohio_values:
        ohio_val = ohio_values[metric]
        fig.add_hline(
            y=ohio_val,
            line_dash='dot',
            line_color='#4ECDC4',
            opacity=0.7,
            annotation_text=f'Ohio 2025: {ohio_val} {unit}',
            annotation_position='top left',
            annotation_font_color='#4ECDC4'
        )

    # 2025 baseline marker
    fig.add_vline(
        x=2025,
        line_dash='dot',
        line_color='rgba(255,255,255,0.3)',
        annotation_text='2025 Baseline',
        annotation_position='top right',
        annotation_font_color='rgba(255,255,255,0.5)'
    )

    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(tickformat='d', dtick=1, title='Year'),
        yaxis=dict(title=f'{metric} ({unit})'),
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

# ---- SUMMARY TABLE ----
st.markdown("---")
st.markdown('<div class="section-title">Projection Summary — All Metrics</div>', unsafe_allow_html=True)

summary_rows = []
for m in base_values:
    base = base_values[m]
    opt  = project(base, scenarios["🟢 Optimistic"]['rates'][m], years_ahead)
    mod  = project(base, scenarios["🟡 Moderate"]['rates'][m], years_ahead)
    pes  = project(base, scenarios["🔴 Pessimistic"]['rates'][m], years_ahead)
    unit = units[m]
    summary_rows.append({
        'Metric': m,
        'Unit': unit,
        f'2025 Baseline': base,
        f'Optimistic ({target_year})': opt,
        f'Moderate ({target_year})': mod,
        f'Pessimistic ({target_year})': pes,
        'Ohio 2025': ohio_values.get(m, 'N/A')
    })

summary_df = pd.DataFrame(summary_rows)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ---- DOWNLOAD ----
csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Forecast Data as CSV",
    data=csv,
    file_name=f"hancock_forecast_{scenario.replace(' ', '_')}_{target_year}.csv",
    mime="text/csv"
)

# ---- DISCLAIMER ----
st.markdown("---")
st.markdown("""
<div style="
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid rgba(168,85,247,0.5);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 10px;
">
    <p style="font-size:12px; color:rgba(255,255,255,0.5); margin:0 0 6px 0;
    font-weight:700; letter-spacing:1px; text-transform:uppercase;">
        📋 Forecast Disclaimer
    </p>
    <p style="font-size:12px; color:rgba(255,255,255,0.55); margin:0; line-height:1.7;">
        Projections are <strong>mathematical estimates only</strong> based on applying compound
        annual rates to 2025 baseline values from the
        <a href="https://www.countyhealthrankings.org/health-data/ohio"
        target="_blank" style="color:#a855f7;">County Health Rankings & Roadmaps</a> program.
        They are <strong>not official forecasts</strong> and should not be used for clinical,
        policy, or funding decisions without independent verification.
        Scenario rates are illustrative and aligned with the goals of the
        <a href="https://www.hancockph.com/health-assessment-project"
        target="_blank" style="color:#a855f7;">2026–2028 Hancock County CHIP</a>.
        Hancock County, Ohio · Population: 74,704.
    </p>
</div>
""", unsafe_allow_html=True)

# ---- SIDEBAR CHAT ----
render_sidebar_chat("Health Forecast & Scenario Analysis")