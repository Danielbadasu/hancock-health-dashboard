import pandas as pd
import streamlit as st
import os
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

COUNTY = 'Hancock'
STATE = 'Ohio'
POPULATION = 74704
CHIP_YEAR = '2026-2028'


@st.cache_data
def load_year(year: int):
    pattern = os.path.join(DATA_DIR, f"{year} County Health Rankings Ohio*.xlsx")
    files = glob.glob(pattern)
    if not files:
        return None
    path = files[0]

    # Select/Ranked sheet names changed in 2024
    select_candidates = [
        "Select Measure Data",
        "Ranked Measure Data",
    ]
    additional_candidates = [
        "Additional Measure Data",
    ]

    select = None
    for name in select_candidates:
        try:
            select = pd.read_excel(path, sheet_name=name, header=1)
            break
        except Exception:
            continue

    additional = None
    for name in additional_candidates:
        try:
            additional = pd.read_excel(path, sheet_name=name, header=1)
            break
        except Exception:
            continue

    if select is None or additional is None:
        return None

    select['year'] = year
    additional['year'] = year
    return {'select': select, 'additional': additional}


@st.cache_data
def load_latest():
    return load_year(2025)


@st.cache_data
def load_all_years():
    all_select = []
    all_additional = []
    for year in range(2020, 2026):
        data = load_year(year)
        if data:
            all_select.append(data['select'])
            all_additional.append(data['additional'])
    return {
        'select': pd.concat(all_select, ignore_index=True) if all_select else pd.DataFrame(),
        'additional': pd.concat(all_additional, ignore_index=True) if all_additional else pd.DataFrame()
    }


def get_hancock(df):
    row = df[df['County'] == COUNTY]
    return row.iloc[0] if not row.empty else None


def get_ohio(df):
    row = df[(df['County'].isna()) & (df['State'] == STATE)]
    return row.iloc[0] if not row.empty else None


def get_all_counties(df):
    return df[df['County'].notna() & (df['State'] == STATE)]


def get_trend(df, column):
    if column not in df.columns:
        return pd.DataFrame()
    hancock = df[df['County'] == COUNTY][['year', column]].dropna()
    ohio = df[(df['County'].isna()) & (df['State'] == STATE)][['year', column]].dropna()
    hancock['geography'] = 'Hancock County'
    ohio['geography'] = 'Ohio'
    return pd.concat([hancock, ohio], ignore_index=True)


def find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def delta_label(hancock_val, ohio_val, lower_is_better=True):
    diff = hancock_val - ohio_val
    if lower_is_better:
        better = diff < 0
    else:
        better = diff > 0
    arrow = "▼" if diff < 0 else "▲"
    color = "good" if better else "bad"
    return arrow, abs(diff), color