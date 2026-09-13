import os
import sys
import time
import pandas as pd
import numpy as np

# Ensure project path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.database import get_db_connection, init_db

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def compute_rolling_metrics(symbol, window=20, anomaly_z_thresh=2.2):
    """
    Reads the latest tick stream window from DuckDB, computes quantitative indicators,
    and returns a clean DataFrame with metrics.
    """
    try:
        conn = get_db_connection(read_only=True)
        query = f"""
            SELECT timestamp, symbol, price, volume 
            FROM market_data 
            WHERE symbol = '{symbol}' 
            ORDER BY timestamp DESC 
            LIMIT 100
        """
        df = conn.execute(query).df()
        conn.close()
    except Exception as err:
        return None

    if df.empty or len(df) < 5:
        return None

    # Chronological sort (oldest to newest)
    df = df.iloc[::-1].reset_index(drop=True)

    # 1. Rolling Moving Averages
    eff_window = min(window, len(df))
    sma_col = min(14, len(df))
    df['sma_14'] = df['price'].rolling(window=sma_col, min_periods=1).mean()
    df['ema_12'] = df['price'].ewm(span=min(12, len(df)), adjust=False).mean()

    # 2. Rolling Volatility (Standard Deviation)
    df['volatility'] = df['price'].rolling(window=eff_window, min_periods=2).std().fillna(0.0)

    # 3. Dynamic Z-Scores & Statistical Anomaly Flag
    rolling_mean = df['price'].rolling(window=eff_window, min_periods=2).mean()
    rolling_std = df['price'].rolling(window=eff_window, min_periods=2).std()
    
    # Avoid division by zero
    df['z_score'] = np.where(rolling_std > 0, (df['price'] - rolling_mean) / rolling_std, 0.0)
    df['is_anomaly'] = df['z_score'].abs() > anomaly_z_thresh

    # 4. Bollinger Bands
    df['bb_upper'] = rolling_mean + (2 * rolling_std)
    df['bb_lower'] = rolling_mean - (2 * rolling_std)

    # 5. Cumulative VWAP
    cum_vol = df['volume'].cumsum()
    cum_vol_price = (df['price'] * df['volume']).cumsum()
    df['vwap'] = np.where(cum_vol > 0, cum_vol_price / cum_vol, df['price'])

    return df

def save_latest_metrics(symbol="BTC-USD"):
    """Computes and saves latest analytics metrics to analytics_metrics table."""
    df = compute_rolling_metrics(symbol)
    if df is not None and not df.empty:
        latest = df.iloc[-1]
        try:
            conn = get_db_connection(read_only=False)
            conn.execute("""
                INSERT INTO analytics_metrics (timestamp, symbol, sma_14, volatility, z_score, is_anomaly)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                latest['timestamp'], 
                latest['symbol'], 
                float(latest['sma_14']), 
                float(latest['volatility']), 
                float(latest['z_score']), 
                bool(latest['is_anomaly'])
            ))
            conn.close()
            return latest
        except Exception:
            pass
    return None

def run_processor_loop(symbols=["BTC-USD", "ETH-USD"], interval_sec=1.0):
    """Runs a continuous analytical evaluation loop."""
    init_db()
    print(f"[PROCESSOR] Starting quantitative processing engine for {symbols}...")
    try:
        while True:
            for sym in symbols:
                res = save_latest_metrics(sym)
                if res is not None:
                    status_flag = "[ANOMALY!]" if res['is_anomaly'] else "[OK]"
                    print(f"[ANALYTICS] {status_flag} {sym} | Price: ${res['price']:,.2f} | SMA: ${res['sma_14']:,.2f} | Vol: {res['volatility']:.4f} | Z-Score: {res['z_score']:+.2f}")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\n[PROCESSOR] Analytics loop paused.")

if __name__ == "__main__":
    run_processor_loop()
