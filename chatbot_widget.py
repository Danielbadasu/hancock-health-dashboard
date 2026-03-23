import os
import streamlit as st
from groq import Groq

HANCOCK_CONTEXT = """
You are a public health data analyst embedded inside the Hancock County Public Health Dashboard
for Findlay, Ohio. You have deep expertise in:

- The 2026-2028 Hancock County Community Health Improvement Plan (CHIP)
- CHIP Priority 1: Behavioral Health & Substance Use
- CHIP Priority 2: Social Determinants & Built Environment  
- CHIP Priority 3: Chronic Disease & Healthy Lifestyle
- County Health Rankings data and methodology
- Hancock County demographics (population: 74,704)
- How Hancock County compares to Ohio state averages

Key Hancock County facts you know:
- Life expectancy: 76.1 years (Ohio: 75.2)
- Drug overdose death rate: 33.8 per 100k (Ohio: 44.7) — better than state
- Mental health providers: 232 per 100k (Ohio: 349) — 33% fewer than state
- Primary care physicians: 52 per 100k (Ohio: 75) — 30% fewer than state
- Children in poverty: 10.8% (Ohio: 17.5%) — much better than state
- Adult obesity: 37% (Ohio: 38.4%)
- Frequent mental distress: 18.5% (Ohio: 19.4%)
- Access to exercise opportunities: 77% (Ohio: 84%) — below state
- Median household income: $72,065 (Ohio: $67,873)

Be concise, data-driven, and always relate answers back to Hancock County
and the CHIP priorities where relevant.
"""

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
    dragmode=False,
)

GLOBAL_CSS = """
<style>
.js-plotly-plot .plotly .cursor-crosshair { cursor: pointer !important; }
.js-plotly-plot .plotly .cursor-ew-resize,
.js-plotly-plot .plotly .cursor-ns-resize,
.js-plotly-plot .plotly .cursor-move { cursor: pointer !important; }
.js-plotly-plot { cursor: pointer !important; }
div[data-testid="stSidebarContent"] textarea:focus::placeholder { color: transparent !important; }
div[data-testid="stSidebarContent"] textarea::placeholder {
    color: rgba(255,255,255,0.25) !important; font-style: italic;
}
div[data-testid="stSidebarContent"] textarea { min-height: 80px !important; resize: vertical !important; }
</style>
"""


def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", None)
    return Groq(api_key=api_key)


def render_ai_banner(page_context: str):
    st.markdown(f"""
    <style>
    .ai-banner-wrapper {{
        display: flex; gap: 0px; margin-bottom: 28px; height: 72px;
        animation: glowpulse 3s ease-in-out infinite;
        border-radius: 14px; overflow: hidden;
    }}
    @keyframes glowpulse {{
        0%   {{ box-shadow: 0 0 20px rgba(78, 205, 196, 0.15); }}
        50%  {{ box-shadow: 0 0 40px rgba(78, 205, 196, 0.35); }}
        100% {{ box-shadow: 0 0 20px rgba(78, 205, 196, 0.15); }}
    }}
    .ai-banner-left {{
        flex: 1;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(78, 205, 196, 0.4);
        border-left: 4px solid #4ECDC4; border-right: none;
        border-radius: 14px 0 0 14px; padding: 0 24px;
        display: flex; flex-direction: column; justify-content: center; gap: 4px;
    }}
    .ai-banner-right {{
        flex: 1;
        background: linear-gradient(135deg, #0f3443, #0d4f5c);
        border: 1px solid rgba(78, 205, 196, 0.4); border-left: none;
        border-radius: 0 14px 14px 0;
        display: flex; align-items: center; justify-content: center;
        cursor: pointer; text-decoration: none !important;
        transition: background 0.2s ease;
    }}
    .ai-banner-right:hover {{ background: linear-gradient(135deg, #1a5276, #1a7a8a); }}
    .ai-banner-title {{ font-size: 14px; font-weight: 700; color: #ffffff; letter-spacing: 0.3px; }}
    .ai-banner-sub {{ font-size: 12px; color: rgba(255,255,255,0.7); }}
    .ai-banner-cta {{ font-size: 14px; font-weight: 700; color: #4ECDC4 !important; letter-spacing: 0.3px; text-decoration: none !important; }}
    </style>
    <div class="ai-banner-wrapper">
        <div class="ai-banner-left">
            <div class="ai-banner-title">Want deeper insights on {page_context}?</div>
            <div class="ai-banner-sub">Ask our Hancock County Health AI — trained on local CHIP data.</div>
        </div>
        <a class="ai-banner-right" href="/AI_Assistant" target="_self">
            <span class="ai-banner-cta">💬 Ask AI Assistant →</span>
        </a>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer(page_context: str = ""):
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
    border-left:4px solid rgba(78,205,196,0.5);border-radius:10px;padding:16px 20px;margin-top:10px;">
        <p style="font-size:12px;color:rgba(255,255,255,0.5);margin:0 0 6px 0;
        font-weight:700;letter-spacing:1px;text-transform:uppercase;">📋 Data Sources & Disclaimer</p>
        <p style="font-size:12px;color:rgba(255,255,255,0.55);margin:0;line-height:1.7;">
            Data sourced from the
            <a href="https://www.countyhealthrankings.org/health-data/ohio"
            target="_blank" style="color:#4ECDC4;">County Health Rankings & Roadmaps</a> program,
            a collaboration between the Robert Wood Johnson Foundation and the University of
            Wisconsin Population Health Institute · 2025 Annual Data Release.
            Health priorities align with the
            <a href="https://www.hancockph.com/health-assessment-project"
            target="_blank" style="color:#4ECDC4;">2026–2028 Hancock County Community Health Improvement Plan (CHIP)</a>.
            This dashboard is intended for <strong>informational purposes only</strong>
            and does not constitute medical or public health advice.
            Hancock County, Ohio · Population: 74,704.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_chat(page_context: str):
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Quick AI Chat")
    st.sidebar.markdown(f"*Ask anything about {page_context}*")

    chat_key = f"sidebar_messages_{page_context}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    if st.session_state[chat_key]:
        msgs = st.session_state[chat_key]
        exchanges = []
        i = 0
        while i < len(msgs):
            user_msg = msgs[i]['content'] if msgs[i]['role'] == 'user' else None
            ai_msg = (
                msgs[i + 1]['content']
                if (i + 1 < len(msgs) and msgs[i + 1]['role'] == 'assistant')
                else None
            )
            if user_msg:
                exchanges.append((user_msg, ai_msg))
            i += 2

        for idx, (user_msg, ai_msg) in enumerate(exchanges):
            label = f"🗨️ {user_msg[:35]}{'...' if len(user_msg) > 35 else ''}"
            with st.sidebar.expander(label, expanded=(idx == len(exchanges) - 1)):
                st.markdown(f"**You:** {user_msg}")
                if ai_msg:
                    st.markdown(f"**🏥 Health AI:** {ai_msg}")

    with st.sidebar.form(key=f"chat_form_{page_context}", clear_on_submit=True):
        st.markdown(
            "<p style='font-size:11px;color:rgba(255,255,255,0.35);margin:0 0 4px 0;'>"
            "Ctrl+Enter to send</p>",
            unsafe_allow_html=True
        )
        user_input = st.text_area(
            "message", label_visibility="collapsed",
            placeholder="Type your question here...", height=100,
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            send = st.form_submit_button("Send ➤", use_container_width=True)
        with col2:
            clear = st.form_submit_button("Clear", use_container_width=True)

    if clear:
        st.session_state[chat_key] = []
        st.rerun()

    if send and user_input.strip():
        st.session_state[chat_key].append({"role": "user", "content": user_input})
        client = get_groq_client()
        with st.sidebar:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                HANCOCK_CONTEXT
                                + f"\nThe user is currently viewing the {page_context} page. "
                                "Give concise answers — 2-3 sentences max for sidebar chat."
                            )
                        }
                    ] + [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state[chat_key]
                    ]
                )
        reply = response.choices[0].message.content
        st.session_state[chat_key].append({"role": "assistant", "content": reply})
        st.rerun()