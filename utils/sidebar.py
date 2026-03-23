import streamlit as st
import pandas as pd


def render_sidebar(page_name: str, all_data: dict, chart_options: list, default_charts: list = None):
    """
    Centralized sidebar renderer for all dashboard pages.
    Returns: (selected_year, compare_year, show_ohio, selected_charts)
    """
    st.sidebar.header("Filters")

    show_ohio = st.sidebar.toggle("Show Ohio Benchmark", value=True)

    all_years_list = sorted([
        int(y) for y in all_data['additional']['year'].dropna().unique()
    ], reverse=True)

    selected_year = st.sidebar.selectbox(
        "Select Year",
        options=all_years_list,
        index=0,
        help="Filters all scorecards and charts to this year"
    )

    compare_options = ["None"] + [str(y) for y in all_years_list if y != selected_year]
    compare_year_str = st.sidebar.selectbox(
        "Compare to Year",
        options=compare_options,
        index=0,
        help="Shows change vs a previous year on KPI cards"
    )
    compare_year = int(compare_year_str) if compare_year_str != "None" else None

    if default_charts is None:
        default_charts = chart_options

    selected_charts = st.sidebar.multiselect(
        "Charts to Display",
        options=chart_options,
        default=default_charts
    )

    st.sidebar.markdown("---")

    page_info = {
        "🧠 Behavioral Health": {
            "priority": "CHIP Priority 1",
            "desc": "Behavioral Health & Substance Use",
            "focus": ["Mental health access", "Substance use & overdose", "Suicide prevention"]
        },
        "🌍 Social Factors": {
            "priority": "CHIP Priority 2",
            "desc": "Social Determinants & Built Environment",
            "focus": ["Income & poverty", "Housing & food security", "Education & employment", "Built environment"]
        },
        "💊 Chronic Disease": {
            "priority": "CHIP Priority 3",
            "desc": "Chronic Disease & Healthy Lifestyle",
            "focus": ["Obesity & diabetes", "Smoking & inactivity", "Preventive care access"]
        },
        "📊 Health Outcomes": {
            "priority": "Cross-cutting — All CHIP Priorities",
            "desc": "Health Outcomes & Mortality",
            "focus": ["Life expectancy", "Premature mortality", "Birth outcomes", "Injury deaths"]
        },
        "👥 Demographics": {
            "priority": "Population Context — All CHIP Priorities",
            "desc": "Demographics & Population Profile",
            "focus": ["Age & gender", "Race & ethnicity", "Income by demographic", "Disability & language"]
        },
        "🔮 Forecast Analysis": {
            "priority": "CHIP Scenario Simulator",
            "desc": "Health Forecast & Projections",
            "focus": ["Optimistic scenario", "Moderate scenario", "Pessimistic scenario"]
        },
    }

    info = page_info.get(page_name, {})
    if info:
        st.sidebar.markdown(f"### 📋 {info['priority']}")
        st.sidebar.markdown(f"_{info['desc']}_")
        st.sidebar.markdown("**Focus areas:**")
        for item in info["focus"]:
            st.sidebar.markdown(f"- {item}")

    return selected_year, compare_year, show_ohio, selected_charts


def fetch_metric(all_data: dict, latest: dict, year: int, col: str, county: str = 'Hancock', sheet: str = 'additional'):
    """
    Centralized metric fetcher. Use this in all pages instead of local get_metric().
    """
    from utils.data_loader import get_hancock, get_ohio
    df = all_data[sheet]
    year_df = df[df['year'] == year]
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


def kpi_delta(current, compare, compare_year=None, unit="", lower_is_better=True):
    """
    Returns HTML delta badge — always white text on dark semi-transparent
    background so it's readable on any card color.
    """
    if compare is None or current is None:
        return ""
    change = round(current - compare, 1)
    year_label = f"vs {compare_year}" if compare_year else "vs compare year"
    if change == 0:
        return f"""<span style='
            background: rgba(0,0,0,0.25);
            color: rgba(255,255,255,0.8);
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 4px;
        '>→ No change {year_label}</span>"""
    direction = "▲" if change > 0 else "▼"
    improved = (change < 0 and lower_is_better) or (change > 0 and not lower_is_better)
    label = "improved ✅" if improved else "worsened ⚠️"
    return f"""<span style='
        background: rgba(0,0,0,0.25);
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 4px;
        letter-spacing: 0.2px;
    '>{direction} {abs(change)}{unit} {year_label} ({label})</span>"""


def arrow(h, o, lower_is_better=True):
    if h is None or o is None: return '–'
    return '▼' if (h < o) else '▲'


def diff(h, o):
    if h is None or o is None: return 0
    return round(abs(h - o), 1)