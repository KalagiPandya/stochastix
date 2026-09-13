import os
import sys
from datetime import datetime
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.database import get_db_connection, init_db

# Ensure UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def trigger_alert(symbol, alert_type, message, severity="WARNING"):
    """Records an anomaly or risk event into the alerts table."""
    init_db()
    timestamp = datetime.now()
    try:
        conn = get_db_connection(read_only=False)
        conn.execute("""
            INSERT INTO alerts (timestamp, symbol, alert_type, message, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, symbol, alert_type, message, severity))
        conn.close()
        return True
    except Exception:
        return False

def get_recent_alerts(limit=20):
    """Fetches recent risk alerts from DuckDB."""
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
