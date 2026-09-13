import os
import sys
import numpy as np
import pandas as pd

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.processor import compute_rolling_metrics, save_latest_metrics

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def calculate_stochastic_metrics(symbol, window_size=20):
    """
    Reads recent raw ticks from DuckDB in read-only mode, applies vectorized 
    statistical calculations, and isolates anomalies using dynamic Z-Scores.
    """
    df = compute_rolling_metrics(symbol, window=window_size)
    if df is not None and not df.empty:
        return df.tail(1)
    return None

def process_latest_analytics():
    """Loops through our assets, runs calculations, and logs anomalies."""
    for symbol in ["BTC-USD", "ETH-USD"]:
        latest_metric = calculate_stochastic_metrics(symbol)
        
        if latest_metric is not None:
            row = latest_metric.iloc[0]
            if row['is_anomaly']:
                print(f"[ANOMALY ALERT] Extreme price movement on {symbol}! Price: ${row['price']:,.2f} | Z-Score: {row['z_score']:+.2f} | Volatility: {row['volatility']:.4f}")
            else:
                print(f"[METRICS] {symbol} | Price: ${row['price']:,.2f} | SMA: ${row['sma_14']:,.2f} | Vol: {row['volatility']:.4f} | Z-Score: {row['z_score']:+.2f}")

if __name__ == "__main__":
    print("[ANALYTICS ENGINE] Running statistical calculations on active streams...")
    process_latest_analytics()