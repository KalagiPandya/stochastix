import os
import sys
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection
from pipeline.processor import compute_rolling_metrics

st.set_page_config(page_title="Volatility Tracking | Stochastix", page_icon="⚡", layout="wide")

st.title("Market Volatility & Variance Tracking")

# Pull rolling metrics for both BTC and ETH
dfs = []
for sym in ["BTC-USD", "ETH-USD"]:
    d = compute_rolling_metrics(sym, window=50)
    if d is not None and not d.empty:
        dfs.append(d)

if not dfs:
    st.warning("Calculating standard deviation curves... Awaiting stream data.")
else:
    import pandas as pd
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Volatility comparison chart
    fig = px.line(
        combined_df, 
        x='timestamp', 
        y='volatility', 
        color='symbol', 
        title="Rolling Price Volatility (σ)",
        template="plotly_dark",
        color_discrete_map={"BTC-USD": "#00FFCC", "ETH-USD": "#A855F7"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Z-Score comparison
    fig_z = px.line(
        combined_df,
        x='timestamp',
        y='z_score',
        color='symbol',
        title="Dynamic Z-Score Distribution",
        template="plotly_dark",
        color_discrete_map={"BTC-USD": "#38BDF8", "ETH-USD": "#EC4899"}
    )
    # Add anomaly boundary lines
    fig_z.add_hline(y=2.2, line_dash="dash", line_color="#EF4444", annotation_text="+2.2σ Anomaly")
    fig_z.add_hline(y=-2.2, line_dash="dash", line_color="#EF4444", annotation_text="-2.2σ Anomaly")
    st.plotly_chart(fig_z, use_container_width=True)

time.sleep(2)
st.rerun()