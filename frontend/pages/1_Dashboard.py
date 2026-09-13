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

st.set_page_config(
    page_title="Stream Flow | Stochastix", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .font-mono {
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 0.5rem 0 1rem 0;'>
        <div style='display: inline-flex; justify-content: center; align-items: center; width: 42px; height: 42px; border-radius: 10px; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.3); color: #38BDF8; font-family: "JetBrains Mono"; font-weight: 800; font-size: 1.3rem; margin-bottom: 0.35rem;'>
            Σ
        </div>
        <h3 style='font-size: 1.1rem; font-weight: 800; color: #F8FAFC; margin: 0;'>STOCHASTIX</h3>
        <p style='font-size: 0.7rem; color: #64748B; font-family: "JetBrains Mono"; text-transform: uppercase;'>Stream Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

st.title("📈 Real-Time Asset Stream Flow")
st.caption("Live high-frequency tick stream with dynamic Bollinger Bands and rolling moving averages.")

asset = st.selectbox("Select Target Market Asset", ["BTC-USD", "ETH-USD"])

df = compute_rolling_metrics(asset, window=35)

if df is None or df.empty:
    st.warning("Awaiting system data synchronization... Live data stream is initializing.")
else:
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"Current {asset} Rate", value=f"${latest['price']:,.2f}")
    with col2:
        st.metric(label="SMA (14-Period)", value=f"${latest['sma_14']:,.2f}")
    with col3:
        st.metric(label="Rolling Volatility (σ)", value=f"{latest['volatility']:.4f}")
    with col4:
        anomaly_status = "⚠️ Flagged Anomaly" if latest['is_anomaly'] else "🟢 Normal Variance"
        st.metric(label="Risk Status", value=anomaly_status)
    
    # Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['price'], 
        mode='lines+markers', name='Execution Price',
        line=dict(color='#00FFCC', width=2.5),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['sma_14'], 
        mode='lines', name='SMA 14',
        line=dict(color='#F59E0B', width=1.5, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_upper'], 
        mode='lines', name='Upper Bollinger Band (+2σ)',
        line=dict(color='#EF4444', width=1, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_lower'], 
        mode='lines', name='Lower Bollinger Band (-2σ)',
        line=dict(color='#10B981', width=1, dash='dot')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=11)),
        xaxis=dict(showgrid=True, gridcolor="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#1E293B", side="right")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🔍 View Live Database Log Rows (Last 15 Ticks)"):
        st.dataframe(df.tail(15)[['timestamp', 'symbol', 'price', 'volume', 'sma_14', 'volatility', 'z_score', 'is_anomaly']], use_container_width=True)

time.sleep(2)
st.rerun()