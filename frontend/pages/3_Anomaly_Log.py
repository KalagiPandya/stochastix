import os
import sys
import time
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection
from pipeline.alerts import get_recent_alerts

st.set_page_config(
    page_title="Anomaly Log | Stochastix", 
    page_icon="⚠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Spacious Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Page Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }
    
    .page-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }
    .page-sub {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Summary Card */
    .anom-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        text-align: center;
    }
    .anom-lbl {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.25rem;
    }
    .anom-num {
        font-size: 1.75rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

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

# Header
st.markdown("<div class='page-title'>⚠️ Statistical Anomaly & Risk Logs</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Automated threshold violation detection, flash crash flags, and DuckDB analytical alert event logs.</div>", unsafe_allow_html=True)

# Fetch data
try:
    conn = get_db_connection(read_only=True)
    df_anomalies = conn.execute("""
        SELECT timestamp, symbol, sma_14, volatility, z_score 
        FROM analytics_metrics 
        WHERE is_anomaly = true 
        ORDER BY timestamp DESC 
        LIMIT 25
    """).df()
    conn.close()
except Exception:
    df_anomalies = None

df_alerts = get_recent_alerts(limit=25)

count_anom = len(df_anomalies) if df_anomalies is not None else 0
count_alerts = len(df_alerts) if df_alerts is not None else 0

# Top Stats
a1, a2, a3 = st.columns(3)
with a1:
    st.markdown(f"""
    <div class="anom-card">
        <div class="anom-lbl">Flagged Anomalies (|Z| &gt; 2.2)</div>
        <div class="anom-num" style="color: {'#F43F5E' if count_anom > 0 else '#34D399'};">{count_anom}</div>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown(f"""
    <div class="anom-card">
        <div class="anom-lbl">Active Risk Alerts</div>
        <div class="anom-num" style="color: #38BDF8;">{count_alerts}</div>
    </div>
    """, unsafe_allow_html=True)

with a3:
    st.markdown("""
    <div class="anom-card">
        <div class="anom-lbl">Detector Algorithm</div>
        <div class="anom-num" style="color: #A855F7; font-size: 1.25rem; margin-top: 0.4rem;">Dynamic Z-Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Tabbed Display
tab1, tab2 = st.tabs(["📊 Statistical Anomaly Records", "⚡ System Risk Alerts"])

with tab1:
    st.markdown("#### High-Impact Statistical Jump Entries")
    if df_anomalies is None or df_anomalies.empty:
        st.success("🟢 Risk parameters nominal. No anomalies flagged inside current volatility windows.")
    else:
        st.dataframe(df_anomalies, use_container_width=True)

with tab2:
    st.markdown("#### Operational Audit Trail")
    if df_alerts is None or df_alerts.empty:
        st.info("🟢 No operational risk alerts recorded.")
    else:
        st.dataframe(df_alerts, use_container_width=True)

time.sleep(3)
st.rerun()