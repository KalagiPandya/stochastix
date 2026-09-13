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
        margin-bottom: 1.5rem;
    }

    /* Spacious Metric Box Grid */
    .metric-box {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 1.25rem 1rem;
        text-align: center;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.2s ease;
    }
    .metric-box:hover {
        border-color: #38BDF8;
    }
    .metric-lbl {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.35rem;
        white-space: nowrap;
    }
    .metric-num {
        font-size: clamp(1.15rem, 1.6vw, 1.65rem);
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        white-space: nowrap;
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
        <p style='font-size: 0.75rem; color: #64748B; font-family: "JetBrains Mono"; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px;'>Stream Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# Header
st.markdown("<div class='page-title'>📈 Real-Time Asset Stream Flow</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Live tick feed execution with dynamic Bollinger Bands (±2σ) and rolling indicators.</div>", unsafe_allow_html=True)

# Asset Selector
col_sel, col_space = st.columns([1.5, 3.5])
with col_sel:
    asset = st.selectbox("Select Target Asset Stream", ["BTC-USD", "ETH-USD"])

df = compute_rolling_metrics(asset, window=35)

if df is None or df.empty:
    st.info("⏳ Awaiting stream synchronization... Buffer is actively loading.")
else:
    latest = df.iloc[-1]
    
    # 4 Spacious Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Live {asset} Price</div>
            <div class="metric-num" style="color: #38BDF8;">${latest['price']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">SMA (14-Period)</div>
            <div class="metric-num" style="color: #F8FAFC;">${latest['sma_14']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Rolling Volatility (σ)</div>
            <div class="metric-num" style="color: #A855F7;">{latest['volatility']:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        is_anom = latest['is_anomaly']
        bg_color = "rgba(244, 63, 94, 0.15)" if is_anom else "rgba(16, 185, 129, 0.15)"
        border_color = "rgba(244, 63, 94, 0.4)" if is_anom else "rgba(16, 185, 129, 0.4)"
        text_color = "#F43F5E" if is_anom else "#34D399"
        status_label = "⚠️ ANOMALY" if is_anom else "🟢 NOMINAL"
        
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Risk & Variance</div>
            <div class="status-pill" style="background: {bg_color}; border: 1px solid {border_color}; color: {text_color}; margin-top: 0.2rem;">
                {status_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Clean, Beautiful Plotly Chart
    fig = go.Figure()
    
    # Price
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['price'], 
        mode='lines+markers', name='Execution Price',
        line=dict(color='#00FFCC', width=2.5),
        marker=dict(size=4)
    ))
    
    # SMA
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['sma_14'], 
        mode='lines', name='SMA 14',
        line=dict(color='#F59E0B', width=1.5, dash='dash')
    ))
    
    # Upper Band
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_upper'], 
        mode='lines', name='Upper Band (+2σ)',
        line=dict(color='#EF4444', width=1.2, dash='dot')
    ))
    
    # Lower Band
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['bb_lower'], 
        mode='lines', name='Lower Band (-2σ)',
        line=dict(color='#10B981', width=1.2, dash='dot')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="left", 
            x=0,
            font=dict(family="JetBrains Mono", size=11)
        ),
        xaxis=dict(showgrid=True, gridcolor="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#1E293B", side="right")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("📋 View Live Database Buffer Records"):
        st.dataframe(
            df.tail(15)[['timestamp', 'symbol', 'price', 'volume', 'sma_14', 'volatility', 'z_score', 'is_anomaly']], 
            use_container_width=True
        )

time.sleep(3)
st.rerun()