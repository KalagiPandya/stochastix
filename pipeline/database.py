import os
import sys
import duckdb

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Default database path in the project root or configurable via env
DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stochastix.db"))
DB_PATH = os.getenv("STOCHASTIX_DB_PATH", DEFAULT_DB_PATH)

def get_db_connection(read_only=False):
    """
    Establishes a connection to DuckDB.
    Uses READ_ONLY when querying to prevent database locking conflicts across processes.
    """
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    access_mode = 'READ_ONLY' if read_only else 'READ_WRITE'
    return duckdb.connect(DB_PATH, config={'access_mode': access_mode})

def init_db():
    """Initializes the optimized columnar tables for market data, metrics, and alerts."""
    conn = get_db_connection(read_only=False)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            timestamp TIMESTAMP,
            symbol VARCHAR,
            price DOUBLE,
            volume DOUBLE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics_metrics (
            timestamp TIMESTAMP,
            symbol VARCHAR,
            sma_14 DOUBLE,
            volatility DOUBLE,
            z_score DOUBLE,
            is_anomaly BOOLEAN
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TIMESTAMP,
            symbol VARCHAR,
            alert_type VARCHAR,
            message VARCHAR,
            severity VARCHAR
        )
    """)
    
    conn.close()
    print(f"[DB] Initialized Stochastix database tables at: {DB_PATH}")

if __name__ == "__main__":
    init_db()