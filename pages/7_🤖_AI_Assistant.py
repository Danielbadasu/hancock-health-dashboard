import streamlit as st
from chatbot_widget import render_disclaimer, render_sidebar_chat, HANCOCK_CONTEXT, get_groq_client

st.set_page_config(page_title="🤖 AI Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.chat-container { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
.chat-bubble { padding: 16px 20px; border-radius: 16px; max-width: 80%; line-height: 1.6; font-size: 15px; }
.user-bubble {
    background: linear-gradient(135deg, #0f9b8e, #4ECDC4);
    color: white; margin-left: auto; border-bottom-right-radius: 4px;
}
.assistant-bubble {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: rgba(255,255,255,0.9);
    border: 1px solid rgba(78,205,196,0.2); border-bottom-left-radius: 4px;
}
.assistant-name {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: #4ECDC4; margin-bottom: 8px; font-weight: 700;
}
.user-name {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,0.6); margin-bottom: 8px; font-weight: 700; text-align: right;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.markdown("# 🤖 Hancock County Health AI Assistant")
st.markdown("Ask me anything about Hancock County public health data, the CHIP priorities, or how we compare to Ohio.")
st.markdown("---")

# ---- SIDEBAR ----
st.sidebar.header("🎯 Topic Filter")
selected_topic = st.sidebar.radio(
    "Select Topic",
    options=["All Topics", "🧠 Behavioral Health", "🌍 Social Determinants",
             "💊 Chronic Disease", "📊 Health Outcomes"],
    index=0
)
st.sidebar.markdown("---")
st.sidebar.markdown("**💬 Conversation**")
st.sidebar.markdown(f"Messages: **{len(st.session_state.get('ai_page_messages', []))}**")

# ---- SUGGESTED QUESTIONS ----
questions = {
    "🧠 Behavioral Health": [
        ("🧠 Mental health providers gap?", "Why does Hancock County have fewer mental health providers than the Ohio average and what impact does that have?"),
        ("💊 Overdose trends?", "How has the drug overdose death rate trended in Hancock County vs Ohio over recent years?"),
        ("😔 Mental distress rate?", "What does frequent mental distress mean and how does Hancock County compare to Ohio?"),
    ],
    "🌍 Social Determinants": [
        ("🏠 Housing situation?", "What is the housing and poverty situation in Hancock County?"),
        ("🎓 Education & health link?", "How do education levels in Hancock County affect health outcomes?"),
        ("🍎 Food security?", "What is the food insecurity situation in Hancock County compared to Ohio?"),
    ],
    "💊 Chronic Disease": [
        ("⚖️ Obesity rates?", "How does Hancock County's obesity rate compare to Ohio and what are the health implications?"),
        ("🩺 Diabetes prevalence?", "What is the diabetes prevalence in Hancock County vs Ohio?"),
        ("🚬 Smoking rates?", "How does adult smoking in Hancock County compare to the state average?"),
    ],
    "📊 Health Outcomes": [
        ("❤️ Life expectancy?", "Why is Hancock County's life expectancy higher than the Ohio average?"),
        ("👶 Child health?", "How are children faring in Hancock County compared to Ohio?"),
        ("🏥 Healthcare access gaps?", "What are the biggest healthcare access gaps in Hancock County?"),
    ],
}

if selected_topic == "All Topics":
    filtered_questions = [q for qs in questions.values() for q in qs]
else:
    filtered_questions = questions.get(selected_topic, [])

st.markdown(f"**💡 Suggested questions — {selected_topic}:**")
cols = st.columns(3)
for i, (label, full_question) in enumerate(filtered_questions):
    with cols[i % 3]:
        if st.button(label, key=f"q_{i}"):
            st.session_state.suggested = full_question

st.markdown("---")

# ---- CHAT STATE ----
if "ai_page_messages" not in st.session_state:
    st.session_state.ai_page_messages = []
if "suggested" not in st.session_state:
    st.session_state.suggested = None

# ---- DISPLAY CHAT HISTORY ----
if st.session_state.ai_page_messages:
    chat_html = '<div class="chat-container">'
    for msg in st.session_state.ai_page_messages:
        if msg["role"] == "user":
            chat_html += f"""
            <div style="text-align:right">
                <div class="user-name">You</div>
                <div class="chat-bubble user-bubble">{msg['content']}</div>
            </div>"""
        else:
            chat_html += f"""
            <div>
                <div class="assistant-name">🏥 Hancock Health AI</div>
                <div class="chat-bubble assistant-bubble">{msg['content']}</div>
            </div>"""
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

# ---- CHAT INPUT ----
user_input = st.chat_input("Ask a public health question about Hancock County...")

if st.session_state.suggested:
    user_input = st.session_state.suggested
    st.session_state.suggested = None

# ---- SEND & RESPOND ----
if user_input:
    st.session_state.ai_page_messages.append({"role": "user", "content": user_input})
    client = get_groq_client()
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        HANCOCK_CONTEXT
                        + f"\nThe user is exploring the topic: {selected_topic}. "
                        "Tailor responses to be relevant to this topic. "
                        "Be insightful, data-driven, and reference CHIP priorities where relevant. "
                        "Keep responses clear and concise — under 150 words unless detail is needed."
                    )
                }
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.ai_page_messages
            ]
        )
    reply = response.choices[0].message.content
    st.session_state.ai_page_messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ---- CLEAR BUTTON ----
if st.session_state.ai_page_messages:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear conversation"):
            st.session_state.ai_page_messages = []
            st.rerun()

render_disclaimer("AI Health Assistant")
render_sidebar_chat("AI Health Assistant")
