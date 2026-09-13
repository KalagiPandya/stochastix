import os
import sys
import pandas as pd
import numpy as np

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pipeline.processor import compute_rolling_metrics as _proc_compute, save_latest_metrics, run_processor_loop

def compute_rolling_metrics(symbol):
    """Calculates rolling statistical metrics and anomaly indicators for a symbol."""
    df = _proc_compute(symbol)
    if df is not None and not df.empty:
        return df.tail(1)
    return None

def run_analytics_loop():
    """Runs a single pass analytics calculation for all monitored symbols."""
    for symbol in ["BTC-USD", "ETH-USD"]:
        save_latest_metrics(symbol)

if __name__ == "__main__":
    run_processor_loop()