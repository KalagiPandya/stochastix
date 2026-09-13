import os
import sys
from datetime import datetime
import pandas as pd

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.database import get_db_connection, init_db

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def trigger_alert(symbol, alert_type, message, severity="WARNING"):
    """Inserts a structured risk/anomaly alert into the alerts database."""
    init_db()
    timestamp = datetime.now()
    try:
        conn = get_db_connection(read_only=False)
        conn.execute("""
            INSERT INTO alerts (timestamp, symbol, alert_type, message, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, symbol, alert_type, message, severity))
        conn.close()
        print(f"[ALERT - {severity}] {symbol}: {message} ({timestamp.strftime('%H:%M:%S')})")
        return True
    except Exception as e:
        print(f"[ALERT ERROR] Failed to record alert: {e}")
        return False

def get_recent_alerts(limit=20):
    """Fetches the latest risk alert entries from the database."""
    try:
        conn = get_db_connection(read_only=True)
        query = f"""
            SELECT timestamp, symbol, alert_type, message, severity 
            FROM alerts 
            ORDER BY timestamp DESC 
            LIMIT {limit}
        """
        df = conn.execute(query).df()
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def scan_and_generate_alerts():
    """Scans latest metrics to trigger alerts for high volatility or anomalous Z-Scores."""
    try:
        conn = get_db_connection(read_only=True)
        query = """
            SELECT * FROM analytics_metrics 
            WHERE is_anomaly = true 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        df = conn.execute(query).df()
        conn.close()
        
        if not df.empty:
            for _, row in df.iterrows():
                msg = f"Statistical Anomaly: Price shifted to ${row['price']:,.2f} with Z-Score={row['z_score']:.2f}"
                trigger_alert(row['symbol'], "ANOMALY_FLAG", msg, "HIGH")
    except Exception:
        pass

if __name__ == "__main__":
    print("[ALERTS ENGINE] Running risk alert scanner...")
    # Test triggering a sample alert
    trigger_alert("BTC-USD", "SYSTEM_HEALTH", "Alerts service initialized and monitoring data stream.", "INFO")
    scan_and_generate_alerts()
    print("Recent Alerts:")
    print(get_recent_alerts(5))
