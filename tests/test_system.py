import os
import sys
import pytest
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.database import get_db_connection, init_db
from pipeline.simulator import MarketSimulator
from pipeline.processor import compute_rolling_metrics, save_latest_metrics
from app.alerts import trigger_alert, get_recent_alerts

def test_database_initialization():
    init_db()
    conn = get_db_connection(read_only=True)
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    conn.close()
    assert "market_data" in tables
    assert "analytics_metrics" in tables
    assert "alerts" in tables

def test_market_simulator():
    sim = MarketSimulator()
    tick_btc = sim.generate_tick("BTC-USD")
    tick_eth = sim.generate_tick("ETH-USD")
    
    assert tick_btc["symbol"] == "BTC-USD"
    assert tick_btc["price"] > 0
    assert tick_btc["volume"] > 0
    assert tick_eth["symbol"] == "ETH-USD"
    assert tick_eth["price"] > 0

def test_processor_metrics():
    # Insert some dummy rows to test processor
    sim = MarketSimulator()
    conn = get_db_connection(read_only=False)
    for _ in range(15):
        t = sim.generate_tick("BTC-USD")
        conn.execute("INSERT INTO market_data (timestamp, symbol, price, volume) VALUES (?, ?, ?, ?)",
                     (t["timestamp"], t["symbol"], t["price"], t["volume"]))
    conn.close()
    
    df = compute_rolling_metrics("BTC-USD", window=10)
    assert df is not None
    assert not df.empty
    assert "sma_14" in df.columns
    assert "volatility" in df.columns
    assert "z_score" in df.columns
    assert "bb_upper" in df.columns
    assert "bb_lower" in df.columns

def test_alerts_engine():
    res = trigger_alert("BTC-USD", "TEST_ALERT", "Unit test alert message", "INFO")
    assert res is True
    
    df_alerts = get_recent_alerts(limit=5)
    assert not df_alerts.empty
