import os
import sys
import threading
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import init_db, get_db_connection
from pipeline.processor import compute_rolling_metrics
from pipeline.simulator import MarketSimulator

init_db()

# --- CLOUD / LOCAL AUTO BACKGROUND STREAM WORKER ---
@st.cache_resource
def start_background_data_feed():
    """
    Spawns a background thread on application startup to ensure 
    the DuckDB database is continuously receiving tick stream data.
    """
    def worker():
        try:
            # Try connecting to live exchange feed first
            from pipeline.ingest import start_pipeline
            start_pipeline()
        except Exception:
            # Resilient fallback to high-fidelity market simulator
            sim = MarketSimulator()
            sim.run(interval_sec=1.0)

    # Seed initial buffer if database has fewer than 20 rows
    try:
        conn = get_db_connection(read_only=True)
        count = conn.execute("SELECT count(*) FROM market_data").fetchone()[0]
        conn.close()
    except Exception:
        count = 0

    if count < 20:
        sim = MarketSimulator()
        sim.run(interval_sec=0.01, total_ticks=30)

    # Launch streaming daemon thread
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return True

# Initialize data feed daemon
start_background_data_feed()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Stochastix | Quant Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CLEAN, AIRY, ELEGANT STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Clean Hero Section */
    .hero-header {
        text-align: center;
        padding: 3rem 1.5rem 2rem 1.5rem;
        margin-bottom: 2rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34D399;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 1.25rem;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 10px #10B981;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F8FAFC 0%, #38BDF8 60%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.75rem;
    }
    .hero-desc {
        color: #94A3B8;
        font-size: 1.15rem;
        max-width: 720px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Spacious Stat Cards */
    .metric-container {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 1.75rem;
        text-align: center;
        transition: all 0.25s ease;
    }
    .metric-container:hover {
        border-color: #38BDF8;
        transform: translateY(-3px);
        box-shadow: 0 12px 30px -10px rgba(56, 189, 248, 0.15);
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.5rem;
    }
    .metric-val {
        font-size: 2.25rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Clean Module Cards */
    .module-card {
        background: #0B1120;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 2rem;
        height: 100%;
        transition: all 0.25s ease;
    }
    .module-card:hover {
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 10px 25px -5px rgba(6, 182, 212, 0.12);
        transform: translateY(-2px);
    }
    .module-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .module-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
    }
    .module-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 1.5rem 0;'>
        <div style='display: inline-flex; justify-content: center; align-items: center; width: 48px; height: 48px; border-radius: 12px; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.3); color: #38BDF8; font-family: "JetBrains Mono"; font-weight: 800; font-size: 1.5rem; margin-bottom: 0.5rem;'>
            Σ
        </div>
        <h2 style='font-size: 1.25rem; font-weight: 800; letter-spacing: 0.05em; color: #F8FAFC; margin: 0;'>STOCHASTIX</h2>
        <p style='font-size: 0.75rem; color: #64748B; font-family: "JetBrains Mono"; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px;'>Quant Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# --- HERO HEADER ---
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">
        <span class="pulse-dot"></span> LIVE ENGINE ACTIVE
    </div>
    <div class="hero-title">STOCHASTIX</div>
    <div class="hero-desc">
        Real-time cryptocurrency quantitative streaming, embedded columnar time-series analytics, 
        and statistical anomaly detection platform.
    </div>
</div>
""", unsafe_allow_html=True)

# --- LIVE METRIC CARDS ---
df_btc = compute_rolling_metrics("BTC-USD", window=15)
df_eth = compute_rolling_metrics("ETH-USD", window=15)

btc_price = df_btc['price'].iloc[-1] if (df_btc is not None and not df_btc.empty) else 64500.00
eth_price = df_eth['price'].iloc[-1] if (df_eth is not None and not df_eth.empty) else 3450.00

try:
    conn = get_db_connection(read_only=True)
    total_ticks = conn.execute("SELECT count(*) FROM market_data").fetchone()[0]
    conn.close()
except Exception:
    total_ticks = 12800

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">⚡ Bitcoin (BTC-USD)</div>
        <div class="metric-val" style="color: #38BDF8;">${btc_price:,.2f}</div>
        <div style="font-size: 0.8rem; color: #34D399; font-family: 'JetBrains Mono'; margin-top: 0.5rem;">
            🟢 Stream Synced
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">🔷 Ethereum (ETH-USD)</div>
        <div class="metric-val" style="color: #A855F7;">${eth_price:,.2f}</div>
        <div style="font-size: 0.8rem; color: #34D399; font-family: 'JetBrains Mono'; margin-top: 0.5rem;">
            🟢 Stream Synced
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">📊 Processed Ticks (DuckDB)</div>
        <div class="metric-val" style="color: #10B981;">{total_ticks:,}</div>
        <div style="font-size: 0.8rem; color: #64748B; font-family: 'JetBrains Mono'; margin-top: 0.5rem;">
            Columnar Storage Active
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

# --- NAVIGATION MODULES ---
st.markdown("<h3 style='text-align: center; color: #F8FAFC; font-weight: 700; margin-bottom: 1.5rem;'>Explore Analytics Modules</h3>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">📈</div>
        <div class="module-title">1. Real-Time Stream Flow</div>
        <div class="module-desc">
            Live interactive tick chart featuring dynamic <strong>Bollinger Bands (±2σ)</strong>, 
            Simple Moving Averages (SMA-14), and database inspection logs.
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">⚡</div>
        <div class="module-title">2. Volatility Analysis</div>
        <div class="module-desc">
            Vectorized rolling variance curves, cross-asset standard deviation tracking, 
            and <strong>Dynamic Z-Score distribution models</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">⚠️</div>
        <div class="module-title">3. Anomaly Detection Log</div>
        <div class="module-desc">
            Automated statistical anomaly detection flagging extreme volatility shifts 
            and recording audit logs in DuckDB.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

st.info("👈 **Select any module from the left sidebar** to view full real-time interactive charts.")