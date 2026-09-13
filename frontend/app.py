import os
import sys
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import init_db

init_db()

st.set_page_config(
    page_title="Stochastix Control Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFCC 0%, #0077FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>STOCHASTIX QUANTITATIVE PLATFORM</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>High-Frequency Ingestion • Vectorized Statistical Analysis • Anomaly Flagging</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #00FFCC;'>📈 1. Real-Time Dashboard</h3>
        <p style='color: #94A3B8; font-size: 0.9rem;'>Live asset execution rates, streaming Simple Moving Averages, and chronological tick charts.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #A855F7;'>⚡ 2. Volatility Analysis</h3>
        <p style='color: #94A3B8; font-size: 0.9rem;'>Rolling variance curves, standard deviation metrics, and asset comparison.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #F43F5E;'>⚠️ 3. Anomaly Detection Log</h3>
        <p style='color: #94A3B8; font-size: 0.9rem;'>Dynamic Z-score anomaly tracking and automated alert event triggers.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.info("👈 **Select a page from the sidebar navigation** to view live streaming metrics.")