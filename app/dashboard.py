import os
import sys
import time
import streamlit as st
import plotly.graph_objects as go

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection, init_db
from pipeline.processor import compute_rolling_metrics

init_db()

st.set_page_config(page_title="Stochastix Engine", page_icon="📊", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00FFCC;'>STOCHASTIX // FINANCIAL ECOSYSTEM</h1>", unsafe_allow_html=True)
st.divider()

# Sidebar asset picker
selected_symbol = st.sidebar.selectbox("Choose Asset", ["BTC-USD", "ETH-USD"])

df = compute_rolling_metrics(selected_symbol, window=30)

if df is None or df.empty:
    st.warning("Stream buffer is warming up... Run `python run.py --simulate` or activate Coinbase pipeline!")
else:
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"Current {selected_symbol} Price", value=f"${latest['price']:,.2f}")
    with col2:
        st.metric(label="Rolling SMA-14", value=f"${latest['sma_14']:,.2f}")
    with col3:
        st.metric(label="Volatility Score (σ)", value=f"{latest['volatility']:.4f}")
    with col4:
        st.metric(label="Anomaly Status", value="⚠️ ANOMALY" if latest['is_anomaly'] else "🟢 STABLE")
        
    st.divider()

    # Interactive Chart using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['price'], 
        mode='lines+markers', 
        name='Live Ticks', 
        line=dict(color='#00FFCC', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['sma_14'], 
        mode='lines', 
        name='SMA 14', 
        line=dict(color='#F59E0B', width=1.5, dash='dash')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Price ($)",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 View Live Database Log Rows"):
        st.dataframe(df.tail(10), use_container_width=True)

time.sleep(2)
st.rerun()