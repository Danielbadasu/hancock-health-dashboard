import streamlit as st
from utils.data_loader import load_latest, get_hancock, get_ohio
from chatbot_widget import render_disclaimer, render_sidebar_chat

st.set_page_config(
    page_title="Hancock County Health Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
.kpi-container {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
}
.kpi-card {
    flex: 1;
    padding: 24px 28px;
    border-radius: 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.teal {
    background: linear-gradient(135deg, #0f9b8e, #4ECDC4);
}
.kpi-card.green {
    background: linear-gradient(135deg, #11998e, #38ef7d);
}
.kpi-card.red {
    background: linear-gradient(135deg, #ff416c, #ff4b2b);
}
.kpi-card.purple {
    background: linear-gradient(135deg, #6a11cb, #a855f7);
}
.kpi-card.amber {
    background: linear-gradient(135deg, #f7971e, #ffd200);
}
.kpi-card.blue {
    background: linear-gradient(135deg, #1a6dff, #4facfe);
}
.kpi-label {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.75);
    margin-bottom: 10px;
    font-weight: 600;
}
.kpi-value {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 6px;
    color: #ffffff;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.kpi-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.65);
}
.kpi-icon {
    position: absolute;
    top: 18px; right: 20px;
    font-size: 42px;
    opacity: 0.25;
}
.chip-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
    margin-bottom: 16px;
    letter-spacing: 0.5px;
}
.chip-badge.p1 { background: rgba(168,85,247,0.2); color: #a855f7; border: 1px solid rgba(168,85,247,0.4); }
.chip-badge.p2 { background: rgba(78,205,196,0.2); color: #4ECDC4; border: 1px solid rgba(78,205,196,0.4); }
.chip-badge.p3 { background: rgba(247,151,30,0.2); color: #ffd200; border: 1px solid rgba(247,151,30,0.4); }
.headline-insight {
    background: linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05));
    border: 1px solid rgba(78,205,196,0.3);
    border-left: 4px solid #4ECDC4;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 28px;
    font-size: 15px;
    color: rgba(255,255,255,0.9);
    line-height: 1.6;
}
.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 16px;
    margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
data = load_latest()
select_df = data['select']
additional_df = data['additional']

hancock_s = get_hancock(select_df)
ohio_s = get_ohio(select_df)
hancock_a = get_hancock(additional_df)
ohio_a = get_ohio(additional_df)

# ---- HEADER ----
st.markdown("# 🏥 Hancock County Public Health Dashboard")
st.markdown("**Findlay, Ohio** · 2025 County Health Rankings · Aligned with the 2026–2028 CHIP")

st.markdown("""
<div style="margin: 8px 0 24px 0;">
    <span class="chip-badge p1">🧠 Priority 1: Behavioral Health</span>
    <span class="chip-badge p2">🌍 Priority 2: Social Determinants</span>
    <span class="chip-badge p3">💊 Priority 3: Chronic Disease</span>
</div>
""", unsafe_allow_html=True)

# ---- HEADLINE INSIGHT ----
life_exp_h = round(hancock_a['Life Expectancy'], 1)
life_exp_o = round(ohio_a['Life Expectancy'], 1)
overdose_h = round(hancock_a['Drug Overdose Mortality Rate'], 1)
overdose_o = round(ohio_a['Drug Overdose Mortality Rate'], 1)
mh_providers_h = round(hancock_s['Mental Health Provider Rate'])
mh_providers_o = round(ohio_s['Mental Health Provider Rate'])
pcp_h = round(hancock_s['Primary Care Physicians Rate'])
pcp_o = round(ohio_s['Primary Care Physicians Rate'])

st.markdown(f"""
<div class="headline-insight">
    💡 <strong>Hancock County at a Glance:</strong> The county outperforms Ohio on key outcomes —
    life expectancy is <strong>{life_exp_h} years</strong> vs the state average of {life_exp_o},
    and drug overdose deaths are <strong>{overdose_h} per 100k</strong> vs {overdose_o} statewide.
    However, access gaps remain: Hancock has only <strong>{mh_providers_h} mental health providers</strong>
    and <strong>{pcp_h} primary care physicians</strong> per 100k residents —
    compared to {mh_providers_o} and {pcp_o} for Ohio overall.
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 1: OUTCOMES ----
st.markdown('<div class="section-title">Health Outcomes</div>', unsafe_allow_html=True)

poverty_h = round(hancock_s['% Children in Poverty'], 1)
poverty_o = round(ohio_s['% Children in Poverty'], 1)
poor_health_h = round(hancock_s['% Fair or Poor Health'], 1)
poor_health_o = round(ohio_s['% Fair or Poor Health'], 1)

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card teal">
        <div class="kpi-icon">❤️</div>
        <div class="kpi-label">Life Expectancy</div>
        <div class="kpi-value">{life_exp_h} yrs</div>
        <div class="kpi-sub">Ohio avg: {life_exp_o} yrs · +{round(life_exp_h - life_exp_o,1)} above state</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">💊</div>
        <div class="kpi-label">Drug Overdose Rate</div>
        <div class="kpi-value">{overdose_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {overdose_o} · {round(overdose_o - overdose_h, 1)} better than state</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-icon">😔</div>
        <div class="kpi-label">Fair or Poor Health</div>
        <div class="kpi-value">{poor_health_h}%</div>
        <div class="kpi-sub">Ohio avg: {poor_health_o}% · {round(poor_health_o - poor_health_h, 1)}% better than state</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">👶</div>
        <div class="kpi-label">Children in Poverty</div>
        <div class="kpi-value">{poverty_h}%</div>
        <div class="kpi-sub">Ohio avg: {poverty_o}% · {round(poverty_o - poverty_h, 1)}% better than state</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- KPI ROW 2: ACCESS ----
st.markdown('<div class="section-title">Healthcare Access</div>', unsafe_allow_html=True)

uninsured_h = round(hancock_s['% Uninsured'], 1)
uninsured_o = round(ohio_s['% Uninsured'], 1)
exercise_h = round(hancock_s['% With Access to Exercise Opportunities'], 1)
exercise_o = round(ohio_s['% With Access to Exercise Opportunities'], 1)

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card red">
        <div class="kpi-icon">🧠</div>
        <div class="kpi-label">Mental Health Providers</div>
        <div class="kpi-value">{mh_providers_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {mh_providers_o} · {mh_providers_o - mh_providers_h} fewer than state</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-icon">🩺</div>
        <div class="kpi-label">Primary Care Physicians</div>
        <div class="kpi-value">{pcp_h}</div>
        <div class="kpi-sub">Per 100k · Ohio: {pcp_o} · {pcp_o - pcp_h} fewer than state</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">🏃</div>
        <div class="kpi-label">Exercise Access</div>
        <div class="kpi-value">{exercise_h}%</div>
        <div class="kpi-sub">Ohio avg: {exercise_o}% · {round(exercise_o - exercise_h, 1)}% below state</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">🏥</div>
        <div class="kpi-label">Uninsured Rate</div>
        <div class="kpi-value">{uninsured_h}%</div>
        <div class="kpi-sub">Ohio avg: {uninsured_o}% · {round(uninsured_o - uninsured_h, 1)}% better than state</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- CHIP NAVIGATION ----
st.markdown("---")
st.markdown('<div class="section-title">Explore by CHIP Priority Area</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.3);
    border-radius: 14px; padding: 20px; text-align: center;">
        <div style="font-size: 32px; margin-bottom: 10px;">🧠</div>
        <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">Behavioral Health</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.6);">
        Mental health · Substance use · Suicide · Overdose trends</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(78,205,196,0.1); border: 1px solid rgba(78,205,196,0.3);
    border-radius: 14px; padding: 20px; text-align: center;">
        <div style="font-size: 32px; margin-bottom: 10px;">🌍</div>
        <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">Social Determinants</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.6);">
        Income · Housing · Education · Food security · Transportation</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(247,151,30,0.1); border: 1px solid rgba(247,151,30,0.3);
    border-radius: 14px; padding: 20px; text-align: center;">
        <div style="font-size: 32px; margin-bottom: 10px;">💊</div>
        <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">Chronic Disease</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.6);">
        Obesity · Diabetes · Physical inactivity · Smoking</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---- DISCLAIMER ----
render_disclaimer("Hancock County Health Overview")

# ---- SIDEBAR ----
st.sidebar.markdown("## 🏥 Hancock County")
st.sidebar.markdown("**Findlay, Ohio** · Pop. 74,704")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 CHIP Priorities")
st.sidebar.markdown("🧠 **Priority 1:** Behavioral Health")
st.sidebar.markdown("🌍 **Priority 2:** Social Determinants")
st.sidebar.markdown("💊 **Priority 3:** Chronic Disease")

render_sidebar_chat("Hancock County Health Overview")