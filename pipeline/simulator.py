import os
import sys
import time
import random
import math
from datetime import datetime

# Ensure project path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.database import get_db_connection, init_db

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

class MarketSimulator:
    """
    Simulates high-frequency crypto trade executions using Geometric Brownian Motion (GBM)
    with Merton Jump-Diffusion to model realistic price volatility and occasional market anomalies.
    """
    def __init__(self):
        self.assets = {
            "BTC-USD": {
                "price": 64500.0,
                "mu": 0.0001,       # Drift
                "sigma": 0.002,     # Normal volatility
                "jump_prob": 0.03,  # Probability of a jump anomaly per tick
                "jump_mag": 0.025,  # Jump magnitude
                "min_vol": 0.01,
                "max_vol": 2.5
            },
            "ETH-USD": {
                "price": 3450.0,
                "mu": 0.0001,
                "sigma": 0.003,
                "jump_prob": 0.03,
                "jump_mag": 0.035,
                "min_vol": 0.1,
                "max_vol": 15.0
            }
        }

    def generate_tick(self, symbol):
        cfg = self.assets[symbol]
        dt = 1.0 / 60.0 # Time step in minutes
        
        # Standard Geometric Brownian Motion component
        z = random.gauss(0, 1)
        drift = (cfg["mu"] - 0.5 * (cfg["sigma"] ** 2)) * dt
        diffusion = cfg["sigma"] * math.sqrt(dt) * z
        ret = drift + diffusion
        
        # Check for Jump-Diffusion anomaly injection
        if random.random() < cfg["jump_prob"]:
            jump_dir = 1 if random.random() > 0.5 else -1
            jump = jump_dir * cfg["jump_mag"] * random.uniform(1.5, 3.5)
            ret += jump
            print(f"[SIMULATOR ALERT] Injected market volatility spike on {symbol} (Jump={jump*100:+.2f}%)")
            
        new_price = max(1.0, cfg["price"] * math.exp(ret))
        cfg["price"] = new_price
        
        # Generate stochastic trade volume
        base_vol = random.uniform(cfg["min_vol"], cfg["max_vol"])
        volume = base_vol * (3.0 if abs(ret) > 0.01 else 1.0)
        
        return {
            "timestamp": datetime.now(),
            "symbol": symbol,
            "price": round(new_price, 2),
            "volume": round(volume, 6)
        }

    def run(self, interval_sec=0.5, total_ticks=None):
        """Runs the simulation stream and persists ticks to the database."""
        init_db()
        print(f"[SIMULATOR] Starting market simulation engine (Tick Interval: {interval_sec}s)...")
        
        tick_count = 0
        try:
            while total_ticks is None or tick_count < total_ticks:
                for symbol in ["BTC-USD", "ETH-USD"]:
                    tick = self.generate_tick(symbol)
                    
                    try:
                        conn = get_db_connection(read_only=False)
                        conn.execute("""
                            INSERT INTO market_data (timestamp, symbol, price, volume)
                            VALUES (?, ?, ?, ?)
                        """, (tick["timestamp"], tick["symbol"], tick["price"], tick["volume"]))
                        conn.close()
                        
                        print(f"[SIMULATE] {tick['symbol']} | Price: ${tick['price']:,.2f} | Vol: {tick['volume']:.4f} | Time: {tick['timestamp'].strftime('%H:%M:%S')}")
                    except Exception as e:
                        pass
                        
                    tick_count += 1
                time.sleep(interval_sec)
        except KeyboardInterrupt:
            print("\n[SIMULATOR] Simulation paused by user.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stochastix Synthetic Market Data Simulator")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between tick batches")
    parser.add_argument("--ticks", type=int, default=None, help="Total tick count to generate (or infinite if omitted)")
    args = parser.parse_args()
    
    sim = MarketSimulator()
    sim.run(interval_sec=args.interval, total_ticks=args.ticks)
