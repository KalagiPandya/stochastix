import os
import sys
import time
import streamlit as st
import plotly.graph_objects as go

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection
from pipeline.processor import compute_rolling_metrics

st.set_page_config(page_title="Live Stream Flow | Stochastix", page_icon="📈", layout="wide")

st.title("Real-Time Asset Stream Flow")
asset = st.selectbox("Select Core Feed", ["BTC-USD", "ETH-USD"])

df = compute_rolling_metrics(asset, window=30)

if df is None or df.empty:
    st.warning("Awaiting system data synchronization... Run `python run.py --simulate` or activate Coinbase streamer.")
else:
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Current Rate", value=f"${latest['price']:,.2f}")
    with col2:
        st.metric(label="SMA (14-Period)", value=f"${latest['sma_14']:,.2f}")
    with col3:
        st.metric(label="Rolling Volatility", value=f"{latest['volatility']:.4f}")
    with col4:
        anomaly_status = "⚠️ Flagged Anomaly" if latest['is_anomaly'] else "🟢 Normal Variance"
        st.metric(label="Risk Status", value=anomaly_status)
    
    # Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['price'], 
        mode='lines+markers', name='Execution Price',
        line=dict(color='#00FFCC', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['sma_14'], 
        mode='lines', name='SMA 14',
        line=dict(color='#F59E0B', width=1.5, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_upper'], 
        mode='lines', name='Upper Bollinger Band',
        line=dict(color='#EF4444', width=1, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_lower'], 
        mode='lines', name='Lower Bollinger Band',
        line=dict(color='#10B981', width=1, dash='dot')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🔍 View Recent Database Records"):
        st.dataframe(df.tail(10)[['timestamp', 'symbol', 'price', 'volume', 'sma_14', 'volatility', 'z_score', 'is_anomaly']], use_container_width=True)

time.sleep(2)
st.rerun()