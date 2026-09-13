import time
import sys
import os
import argparse
from threading import Thread

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.db import init_db
from backend.ingestion.websocket_client import start_stream
from backend.analytics.anomaly_detection import run_analytics_loop
from pipeline.simulator import MarketSimulator

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def start_worker(simulate=False):
    if simulate:
        print("[BACKEND] Running synthetic market simulator...")
        sim = MarketSimulator()
        sim.run(interval_sec=0.5)
    else:
        print("[BACKEND] Connecting to live Coinbase WebSocket feed...")
        start_stream()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stochastix Processing Node")
    parser.add_argument("--simulate", action="store_true", help="Run with simulated market data stream")
    args = parser.parse_args()

    print("[NODE] Starting the STOCHASTIX Processing Node...")
    init_db()
    
    stream_thread = Thread(target=start_worker, args=(args.simulate,), daemon=True)
    stream_thread.start()
    
    print("[NODE] Warming up database buffers...")
    time.sleep(2)
    
    try:
        while True:
            run_analytics_loop()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[NODE] System Offline.")