import os
import sys
import json
import time
from datetime import datetime
import websocket

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.database import get_db_connection, init_db

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def parse_iso_timestamp(time_str):
    """Safely parses ISO timestamps with variable fractional second precision."""
    if not time_str:
        return datetime.now()
    try:
        # Standard ISO 8601 replacement of Z with +00:00
        clean_str = time_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str).replace(tzinfo=None)
    except Exception:
        try:
            return datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return datetime.now()

def on_message(ws, message):
    """Triggered automatically whenever a trade match event arrives from the exchange."""
    try:
        payload = json.loads(message)
    except Exception:
        return
    
    # Isolate matched trade execution events
    if payload.get("type") == "match":
        symbol = payload.get("product_id")
        try:
            price = float(payload.get("price", 0.0))
            volume = float(payload.get("size", 0.0))
        except (ValueError, TypeError):
            return
            
        timestamp = parse_iso_timestamp(payload.get("time"))
        
        try:
            conn = get_db_connection(read_only=False)
            conn.execute("""
                INSERT INTO market_data (timestamp, symbol, price, volume)
                VALUES (?, ?, ?, ?)
            """, (timestamp, symbol, price, volume))
            conn.close()
            print(f"[INGEST] {symbol} | Price: ${price:,.2f} | Volume: {volume:.4f} | Time: {timestamp.strftime('%H:%M:%S')}")
        except Exception as e:
            # Handle transient file-access contention gracefully
            pass

def on_error(ws, error):
    print(f"[STREAM ERROR] WebSocket encounter: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[DISCONNECT] Market stream pipeline closed (code={close_status_code}).")

def on_open(ws):
    print("[CONNECTED] Connected to Coinbase Exchange! Subscribing to BTC-USD and ETH-USD tick feeds...")
    subscribe_msg = {
        "type": "subscribe",
        "product_ids": ["BTC-USD", "ETH-USD"],
        "channels": ["matches"]
    }
    ws.send(json.dumps(subscribe_msg))

def start_pipeline():
    """Initializes schema and runs the resilient streaming loop with auto-reconnect."""
    init_db()
    ws_url = "wss://ws-feed.exchange.coinbase.com"
    
    while True:
        try:
            print("[PIPELINE] Initializing WebSocket client...")
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as err:
            print(f"[RETRY] Stream error ({err}). Reconnecting in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    start_pipeline()