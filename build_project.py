import os

# 1. Complete Multi-Page Directory Trees
folders = [
    "backend/ingestion", "backend/streaming", "backend/analytics", 
    "backend/database", "backend/services", "backend/config",
    "frontend/pages", "frontend/components", "data/raw"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 2. Complete File Mappings with Production Code
files = {
    # DATABASE MANAGEMENT
    "backend/database/db.py": """import duckdb
import os

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
DB_PATH = os.path.join(DB_DIR, "stochastix.db")

def get_db_connection(read_only=False):
    os.makedirs(DB_DIR, exist_ok=True)
    return duckdb.connect(DB_PATH, config={'access_mode': 'READ_ONLY' if read_only else 'READ_WRITE'})

def init_db():
    conn = get_db_connection(read_only=False)
    conn.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS market_data (
            timestamp TIMESTAMP, symbol VARCHAR, price DOUBLE, volume DOUBLE
        )
    \"\"\")
    conn.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS analytics_metrics (
            timestamp TIMESTAMP, symbol VARCHAR, sma_14 DOUBLE, volatility DOUBLE, z_score DOUBLE, is_anomaly BOOLEAN
        )
    \"\"\")
    conn.close()
""",

    # LIVE INGESTION
    "backend/ingestion/websocket_client.py": """import json
import websocket
from datetime import datetime
from backend.database.db import get_db_connection

def on_message(ws, message):
    payload = json.loads(message)
    if payload.get("type") == "match":
        symbol = payload.get("product_id")
        price = float(payload.get("price"))
        volume = float(payload.get("size"))
        raw_time = payload.get("time").replace("Z", "")
        timestamp = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%S.%f")
        
        try:
            conn = get_db_connection(read_only=False)
            conn.execute(\"\"\"
                INSERT INTO market_data (timestamp, symbol, price, volume) VALUES (?, ?, ?, ?)
            \"\"\", (timestamp, symbol, price, volume))
            conn.close()
        except Exception:
            pass
            
def start_stream():
    ws_url = "wss://ws-feed.exchange.coinbase.com"
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=lambda ws: ws.send(json.dumps({"type": "subscribe", "product_ids": ["BTC-USD", "ETH-USD"], "channels": ["matches"]})),
        on_message=on_message
    )
    ws.run_forever()
""",

    # STATISTICAL ANALYTICS ENGINE
    "backend/analytics/anomaly_detection.py": """import pandas as pd
from backend.database.db import get_db_connection

def compute_rolling_metrics(symbol):
    try:
        conn = get_db_connection(read_only=True)
        query = f"SELECT * FROM market_data WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT 100"
        df = conn.execute(query).df()
        conn.close()
    except Exception:
        return None

    if len(df) < 20:
        return None
        
    df = df.iloc[::-1].reset_index(drop=True)
    df['sma_14'] = df['price'].rolling(window=14).mean()
    df['volatility'] = df['price'].rolling(window=14).std()
    
    mean = df['price'].rolling(window=20).mean()
    std = df['price'].rolling(window=20).std()
    df['z_score'] = (df['price'] - mean) / std
    df['is_anomaly'] = df['z_score'].abs() > 2.2
    
    return df.dropna().tail(1)

def run_analytics_loop():
    try:
        conn = get_db_connection(read_only=False)
        for symbol in ["BTC-USD", "ETH-USD"]:
            res = compute_rolling_metrics(symbol)
            if res is not None and not res.empty:
                row = res.iloc[0]
                conn.execute(\"\"\"
                    INSERT INTO analytics_metrics (timestamp, symbol, sma_14, volatility, z_score, is_anomaly)
                    VALUES (?, ?, ?, ?, ?, ?)
                \"\"\", (row['timestamp'], row['symbol'], float(row['sma_14']), float(row['volatility']), float(row['z_score']), bool(row['is_anomaly'])))
        conn.close()
    except Exception:
        pass
""",

    # CORE SYSTEM ENGINE ENTRYPOINT
    "backend/main.py": """import time
import sys
import os
from threading import Thread

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.db import init_db
from backend.ingestion.websocket_client import start_stream
from backend.analytics.anomaly_detection import run_analytics_loop

if __name__ == "__main__":
    print("Starting the STOCHASTIX Processing Node...")
    init_db()
    
    stream_thread = Thread(target=start_stream, daemon=True)
    stream_thread.start()
    
    print("Warming up database buffers...")
    time.sleep(3)
    
    try:
        while True:
            run_analytics_loop()
            time.sleep(1)
    except KeyboardInterrupt:
        print("System Offline.")
""",

    # FRONTEND ENTRYPOINT
    "frontend/app.py": """import streamlit as st

st.set_page_config(page_title="Stochastix Console", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00FFCC;'>STOCHASTIX CONTROL CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888;'>Select an analysis perspective from the left sidebar navigation menu.</p>", unsafe_allow_html=True)
st.info("Use the sidebar navigation menu to view your metrics pages.")
""",

    # FRONTEND PAGE: MAIN DASHBOARD
    "frontend/pages/1_Dashboard.py": """import streamlit as st
import plotly.graph_objects as go
from backend.database.db import get_db_connection

st.title("Real-Time Asset Stream Flow")
asset = st.selectbox("Select Core Feed", ["BTC-USD", "ETH-USD"])

try:
    conn = get_db_connection(read_only=True)
    df = conn.execute(f"SELECT timestamp, price, volume FROM market_data WHERE symbol='{asset}' ORDER BY timestamp DESC LIMIT 50").df()
    conn.close()
except Exception:
    df = None

if df is None or df.empty:
    st.warning("Awaiting system data synchronization...")
else:
    df = df.iloc[::-1]
    st.metric(label="Current Rate", value=f"${df['price'].iloc[-1]:,.2f}")
    
    fig = go.Figure(go.Scatter(x=df['timestamp'], y=df['price'], mode='lines+markers', line=dict(color='#00FFCC')))
    fig.update_layout(template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.tail(5), use_container_width=True)

import time
time.sleep(2)
st.rerun()
""",

    # FRONTEND PAGE: VOLATILITY
    "frontend/pages/2_Volatility_Analysis.py": """import streamlit as st
import plotly.express as px
from backend.database.db import get_db_connection

st.title("Market Volatility Tracking")

try:
    conn = get_db_connection(read_only=True)
    df = conn.execute("SELECT timestamp, symbol, volatility FROM analytics_metrics ORDER BY timestamp DESC LIMIT 100").df()
    conn.close()
except Exception:
    df = None

if df is None or df.empty:
    st.warning("Calculating standard deviation curves...")
else:
    fig = px.line(df, x='timestamp', y='volatility', color='symbol', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
import time
time.sleep(2)
st.rerun()
""",

    # FRONTEND PAGE: ANOMALIES
    "frontend/pages/3_Anomaly_Log.py": """import streamlit as st
from backend.database.db import get_db_connection

st.title("Statistical Anomaly Logs")

try:
    conn = get_db_connection(read_only=True)
    df = conn.execute("SELECT * FROM analytics_metrics WHERE is_anomaly=True ORDER BY timestamp DESC LIMIT 20").df()
    conn.close()
except Exception:
    df = None

if df is None or df.empty:
    st.success("Risk parameters nominal. No anomalies flagged inside current volatility windows.")
else:
    st.error("System alert log triggered for the following high-impact block entries:")
    st.dataframe(df, use_container_width=True)

import time
time.sleep(2)
st.rerun()
"""
}

print("Seeding project architecture files...")
for file_path, content in files.items():
    # FIX: Explicitly enforce UTF-8 encoding so emojis never crash Windows filesystems
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
print("Production layout fully generated.")