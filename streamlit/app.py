"""
StoryLens — Streamlit Frontend
Calls the FastAPI backend at /api/analyze for script analysis.
"""

import streamlit as st
import plotly.graph_objects as go
import requests
import sys
import os

# Add project root to path so config can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import settings

# ─── Config ───
API_BASE = settings.API_BASE_URL

st.set_page_config(
    page_title="StoryLens • AI Script Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, .stApp { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(145deg, #07071a 0%, #0d0d2b 50%, #0a0a1a 100%); }
#MainMenu, footer, header { visibility: hidden; }

.hero-title {
    font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #6366f1 40%, #06b6d4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0; letter-spacing: -1px;
}
.hero-sub {
    text-align: center; color: #94a3b8; font-size: 1.1rem;
    margin-top: 4px; margin-bottom: 2rem; font-weight: 300;
}
.glass-card {
    background: rgba(21, 21, 48, 0.6); backdrop-filter: blur(16px);
    border: 1px solid rgba(167, 139, 250, 0.15); border-radius: 16px;
    padding: 1.5rem; margin-bottom: 1rem; transition: border-color 0.3s ease;
}
.glass-card:hover { border-color: rgba(167, 139, 250, 0.35); }
.card-title {
    font-size: 0.85rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.5px; color: #a78bfa; margin-bottom: 0.75rem;
}
.card-body { color: #e2e8f0; font-size: 0.95rem; line-height: 1.7; }
.score-container { display: flex; align-items: center; justify-content: center; flex-direction: column; }
.score-big {
    font-size: 3.5rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.score-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; margin-top: -4px; }
.emotion-tag {
    display: inline-block; padding: 6px 16px; border-radius: 999px;
    font-size: 0.8rem; font-weight: 600; margin: 4px;
    border: 1px solid rgba(167, 139, 250, 0.3); background: rgba(167, 139, 250, 0.1); color: #c4b5fd;
}
.priority-high { color: #f87171; border-left: 3px solid #f87171; padding-left: 12px; }
.priority-medium { color: #fbbf24; border-left: 3px solid #fbbf24; padding-left: 12px; }
.priority-low { color: #34d399; border-left: 3px solid #34d399; padding-left: 12px; }
.suggestion-card {
    background: rgba(15, 15, 40, 0.5); border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.suggestion-category { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #818cf8; }
.cliffhanger-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(6, 182, 212, 0.1));
    border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 1.5rem;
}
.cliffhanger-quote {
    font-size: 1.2rem; font-style: italic; color: #c4b5fd;
    border-left: 3px solid #a78bfa; padding-left: 1rem; margin: 0.75rem 0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07071a 0%, #0d0d2b 100%);
    border-right: 1px solid rgba(167, 139, 250, 0.1);
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 0.6rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important;
    transition: all 0.3s ease !important; width: 100%;
}
.stButton > button:hover { box-shadow: 0 8px 25px rgba(99, 102, 241, 0.35) !important; }
.stTextArea textarea {
    background: rgba(15, 15, 40, 0.6) !important;
    border: 1px solid rgba(167, 139, 250, 0.2) !important;
    border-radius: 12px !important; color: #e2e8f0 !important;
    font-family: 'Inter', monospace !important; font-size: 0.9rem !important;
}
.stTextArea textarea:focus { border-color: #a78bfa !important; box-shadow: 0 0 20px rgba(167, 139, 250, 0.15) !important; }
.purple-divider { height: 2px; background: linear-gradient(90deg, transparent, #6366f1, transparent); border: none; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ───
def get_score_color(score: float) -> str:
    if score >= 75: return "#34d399"
    elif score >= 50: return "#fbbf24"
    else: return "#f87171"


def render_emotion_arc(analysis: dict):
    arc = analysis["emotion_analysis"]["emotional_arc"]
    moments = [b["moment"] for b in arc]
    intensities = [b["intensity"] for b in arc]
    emotions = [b["emotion"] for b in arc]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(arc))), y=intensities,
        mode='lines+markers+text', text=emotions,
        textposition='top center',
        textfont=dict(color='#c4b5fd', size=11, family='Inter'),
        line=dict(color='#8b5cf6', width=3, shape='spline'),
        marker=dict(size=12, color=intensities,
                    colorscale=[[0, '#6366f1'], [0.5, '#a78bfa'], [1, '#06b6d4']],
                    line=dict(width=2, color='#1e1b4b')),
        hovertemplate='<b>%{customdata[0]}</b><br>Emotion: %{customdata[1]}<br>Intensity: %{y:.0%}<extra></extra>',
        customdata=list(zip(moments, emotions)),
        fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.08)',
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickmode='array', tickvals=list(range(len(arc))),
                   ticktext=[f"Beat {i+1}" for i in range(len(arc))],
                   showgrid=False, color='#64748b', tickfont=dict(family='Inter', size=11)),
        yaxis=dict(title='Intensity', range=[0, 1.15], showgrid=True,
                   gridcolor='rgba(100,116,139,0.1)', color='#64748b',
                   tickformat='.0%', tickfont=dict(family='Inter', size=11),
                   title_font=dict(family='Inter', size=12, color='#64748b')),
        margin=dict(l=50, r=20, t=20, b=40), height=320, font=dict(family='Inter'),
    )
    return fig


def render_engagement_factors(analysis: dict):
    factors = analysis["engagement"]["factors"]
    names = [f["name"] for f in factors]
    scores = [f["score"] for f in factors]
    colors = [get_score_color(s) for s in scores]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names, x=scores, orientation='h',
        marker=dict(color=colors, line=dict(width=0), cornerradius=6),
        text=[f"{s:.0f}" for s in scores], textposition='inside',
        textfont=dict(color='white', size=13, family='Inter', weight=700),
        hovertemplate='<b>%{y}</b>: %{x:.0f}/100<extra></extra>',
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 105], showgrid=False, color='#64748b',
                   tickfont=dict(family='Inter', size=11)),
        yaxis=dict(color='#e2e8f0', tickfont=dict(family='Inter', size=12), autorange='reversed'),
        margin=dict(l=10, r=20, t=10, b=20), height=250, font=dict(family='Inter'), bargap=0.35,
    )
    return fig


def call_api(title: str, script_text: str) -> dict:
    """Call the FastAPI backend /api/analyze endpoint."""
    resp = requests.post(
        f"{API_BASE}/api/analyze",
        json={"title": title, "script_text": script_text},
        timeout=120,
    )
    if resp.status_code != 200:
        detail = resp.json().get("detail", resp.text)
        raise Exception(f"API error ({resp.status_code}): {detail}")
    return resp.json()




def render_results(analysis: dict):
    """Render the full analysis dashboard."""
    st.markdown('<div class="purple-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#64748b;font-size:0.85rem;letter-spacing:3px;'
                'text-transform:uppercase;margin-bottom:2rem;">Analysis Results</p>', unsafe_allow_html=True)

    # Row 1: Summary + Score
    col1, col2 = st.columns([2.5, 1])
    with col1:
        st.markdown(f'''<div class="glass-card">
            <div class="card-title">📖 Story Summary</div>
            <div class="card-body">{analysis["summary"]}</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        score = analysis["engagement"]["overall_score"]
        st.markdown(f'''<div class="glass-card">
            <div class="score-container">
                <div class="score-big">{score:.0f}</div>
                <div class="score-label">Engagement Score</div>
            </div>
            <p style="text-align:center;color:#94a3b8;font-size:0.82rem;margin-top:12px;">
                {analysis["engagement"]["verdict"]}</p>
        </div>''', unsafe_allow_html=True)

    # Row 2: Emotions
    emotions_html = "".join(f'<span class="emotion-tag">{e}</span>'
                            for e in analysis["emotion_analysis"]["dominant_emotions"])
    st.markdown(f'''<div class="glass-card">
        <div class="card-title">🎭 Emotional Tone Analysis</div>
        <div style="margin-bottom:12px;">{emotions_html}</div>
        <p style="color:#94a3b8;font-size:0.85rem;margin-bottom:8px;">
            <strong style="color:#c4b5fd;">Arc:</strong> {analysis["emotion_analysis"]["arc_description"]}</p>
    </div>''', unsafe_allow_html=True)
    st.plotly_chart(render_emotion_arc(analysis), use_container_width=True, config={'displayModeBar': False})

    # Row 3: Engagement Factors
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown('<div class="glass-card"><div class="card-title">📊 Engagement Factors</div></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(render_engagement_factors(analysis), use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.markdown('<div class="glass-card"><div class="card-title">📋 Factor Details</div>', unsafe_allow_html=True)
        for f in analysis["engagement"]["factors"]:
            color = get_score_color(f["score"])
            st.markdown(f'''<div style="margin-bottom:10px;">
                <span style="color:{color};font-weight:700;font-size:0.9rem;">{f["name"]}</span>
                <span style="color:#64748b;font-size:0.8rem;"> — {f["score"]:.0f}/100</span>
                <p style="color:#94a3b8;font-size:0.8rem;margin:2px 0 0 0;">{f["explanation"]}</p>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 4: Suggestions
    st.markdown('<div class="glass-card"><div class="card-title">💡 Improvement Suggestions</div></div>',
                unsafe_allow_html=True)
    cols = st.columns(2)
    for i, s in enumerate(analysis["suggestions"]):
        priority_class = f"priority-{s['priority'].lower()}"
        example_html = (f'<p style="color:#64748b;font-size:0.78rem;margin-top:6px;">💬 <em>{s["example"]}</em></p>'
                        if s.get("example") else '')
        with cols[i % 2]:
            st.markdown(f'''<div class="suggestion-card">
                <div class="suggestion-category">{s["category"]}</div>
                <div class="{priority_class}" style="margin-top:6px;">
                    <span style="font-size:0.85rem;color:#e2e8f0;">{s["suggestion"]}</span>
                </div>
                <span style="font-size:0.7rem;color:#64748b;">Priority: {s["priority"]}</span>
                {example_html}
            </div>''', unsafe_allow_html=True)

    # Row 5: Cliffhanger
    ch = analysis["cliffhanger"]
    st.markdown(f'''<div class="cliffhanger-box">
        <div class="card-title">⚡ Peak Suspense Moment</div>
        <div class="cliffhanger-quote">"{ch["moment_text"]}"</div>
        <p style="color:#e2e8f0;font-size:0.9rem;margin-top:12px;">{ch["explanation"]}</p>
        <p style="color:#818cf8;font-size:0.8rem;margin-top:8px;">
            <strong>Technique:</strong> {ch["storytelling_technique"]}</p>
    </div>''', unsafe_allow_html=True)

    # Raw JSON
    with st.expander("🔍 View Raw JSON Response"):
        st.json(analysis)


# ─── Sidebar ───
with st.sidebar:
    st.markdown('<p style="color:#a78bfa;font-weight:700;font-size:1.1rem;margin-bottom:4px;">🎬 StoryLens</p>',
                unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;font-size:0.8rem;margin-bottom:1.5rem;">AI-Powered Script Intelligence</p>',
                unsafe_allow_html=True)

    st.markdown('<div class="purple-divider"></div>', unsafe_allow_html=True)

    st.markdown(f'''<div style="color:#475569;font-size:0.75rem;line-height:1.8;">
        <strong style="color:#64748b;">Model</strong><br>
        <span style="color:#a78bfa;">✦ {settings.DEFAULT_MODEL}</span><br><br>
        <strong style="color:#64748b;">Provider</strong><br>
        <span style="color:#94a3b8;">Mistral AI</span><br><br>
        <strong style="color:#64748b;">API</strong><br>
        <span style="color:#94a3b8;">FastAPI · localhost:8000</span>
    </div>''', unsafe_allow_html=True)

    st.markdown('<div class="purple-divider"></div>', unsafe_allow_html=True)

    st.markdown('''<div style="color:#475569;font-size:0.7rem;line-height:1.5;">
        <strong style="color:#64748b;">How it works:</strong><br>
        1. Enter a script title<br>
        2. Paste your script text<br>
        3. Click "Analyze Script"<br>
        4. Get AI-powered insights
    </div>''', unsafe_allow_html=True)


# ─── Main Content ───
st.markdown('<h1 class="hero-title">StoryLens</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI-powered script analysis for storytelling intelligence</p>',
            unsafe_allow_html=True)

col_t, _ = st.columns([1, 1])
with col_t:
    title = st.text_input("📌 Script Title", placeholder="Enter your script title...")

script_text = st.text_area("✍️ Paste your script below", height=300,
                           placeholder="Scene: A dimly lit room...\n\nCharacter 1: Dialogue\nCharacter 2: Response...")

# Analyze button
if st.button("🔍  Analyze Script", use_container_width=True):
    if not script_text.strip():
        st.warning("📝 Please enter a script to analyze.")
    else:
        try:
            with st.spinner("🎬 Analyzing your script via the API... This may take 15-30 seconds."):
                analysis = call_api(title=title or "Untitled", script_text=script_text)
                st.session_state["analysis"] = analysis
        except requests.ConnectionError:
            st.error("❌ Cannot connect to the API. Make sure the FastAPI server is running:\n\n"
                     "```bash\nuvicorn backend.main:app --reload --port 8000\n```")
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")

# Render results
if "analysis" in st.session_state:
    render_results(st.session_state["analysis"])
