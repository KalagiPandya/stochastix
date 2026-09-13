import os
import sys
import time
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection
from app.alerts import get_recent_alerts

st.set_page_config(page_title="Anomaly Log | Stochastix", page_icon="⚠️", layout="wide")

st.title("Statistical Anomaly & Alert Logs")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚠️ High-Impact Statistical Anomalies")
    try:
        conn = get_db_connection(read_only=True)
        df_anomalies = conn.execute("""
            SELECT timestamp, symbol, sma_14, volatility, z_score 
            FROM analytics_metrics 
            WHERE is_anomaly = true 
            ORDER BY timestamp DESC 
            LIMIT 20
        """).df()
        conn.close()
    except Exception:
        df_anomalies = None

    if df_anomalies is None or df_anomalies.empty:
        st.success("Risk parameters nominal. No anomalies flagged inside current volatility windows.")
    else:
        st.error("System alert triggered for the following flagged tick blocks:")
        st.dataframe(df_anomalies, use_container_width=True)

with col2:
    st.subheader("⚡ Operational Risk Alerts")
    df_alerts = get_recent_alerts(limit=20)
    if df_alerts.empty:
        st.info("No active operational alerts logged.")
    else:
        st.dataframe(df_alerts, use_container_width=True)

time.sleep(2)
st.rerun()