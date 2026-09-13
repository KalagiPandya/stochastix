import os
import sys
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection
from pipeline.processor import compute_rolling_metrics

st.set_page_config(
    page_title="Volatility Tracking | Stochastix", 
    page_icon="⚡", 
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
    .vol-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        text-align: center;
    }
    .vol-lbl {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.25rem;
    }
    .vol-num {
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
st.markdown("<div class='page-title'>⚡ Market Volatility & Variance Tracking</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Comparative rolling standard deviation metrics and Dynamic Z-Score distribution models.</div>", unsafe_allow_html=True)

# Fetch metrics for both BTC and ETH
dfs = []
for sym in ["BTC-USD", "ETH-USD"]:
    d = compute_rolling_metrics(sym, window=40)
    if d is not None and not d.empty:
        dfs.append(d)

if not dfs:
    st.info("⏳ Calculating standard deviation curves... Buffer is actively loading.")
else:
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Calculate stats
    btc_sub = combined_df[combined_df['symbol'] == 'BTC-USD']
    eth_sub = combined_df[combined_df['symbol'] == 'ETH-USD']
    
    btc_latest_vol = btc_sub['volatility'].iloc[-1] if not btc_sub.empty else 0.0
    eth_latest_vol = eth_sub['volatility'].iloc[-1] if not eth_sub.empty else 0.0
    
    # Top stats
    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown(f"""
        <div class="vol-card">
            <div class="vol-lbl">Bitcoin Volatility (σ)</div>
            <div class="vol-num" style="color: #38BDF8;">{btc_latest_vol:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    with v2:
        st.markdown(f"""
        <div class="vol-card">
            <div class="vol-lbl">Ethereum Volatility (σ)</div>
            <div class="vol-num" style="color: #A855F7;">{eth_latest_vol:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    with v3:
        st.markdown(f"""
        <div class="vol-card">
            <div class="vol-lbl">Volatility Regime</div>
            <div class="vol-num" style="color: #10B981;">STABLE</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Chart 1: Volatility Curves
    fig_vol = px.line(
        combined_df, 
        x='timestamp', 
        y='volatility', 
        color='symbol', 
        title="Rolling Price Volatility (σ)",
        template="plotly_dark",
        color_discrete_map={"BTC-USD": "#38BDF8", "ETH-USD": "#A855F7"}
    )
    fig_vol.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=11)),
        xaxis=dict(showgrid=True, gridcolor="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#1E293B")
    )
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Chart 2: Dynamic Z-Score
    fig_z = px.line(
        combined_df,
        x='timestamp',
        y='z_score',
        color='symbol',
        title="Dynamic Z-Score Distribution Curve",
        template="plotly_dark",
        color_discrete_map={"BTC-USD": "#06B6D4", "ETH-USD": "#EC4899"}
    )
    fig_z.add_hline(y=2.2, line_dash="dash", line_color="#EF4444", annotation_text="+2.2σ Threshold", annotation_font=dict(color="#EF4444", family="JetBrains Mono"))
    fig_z.add_hline(y=-2.2, line_dash="dash", line_color="#EF4444", annotation_text="-2.2σ Threshold", annotation_font=dict(color="#EF4444", family="JetBrains Mono"))
    
    fig_z.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=11)),
        xaxis=dict(showgrid=True, gridcolor="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#1E293B")
    )
    st.plotly_chart(fig_z, use_container_width=True)

time.sleep(3)
st.rerun()