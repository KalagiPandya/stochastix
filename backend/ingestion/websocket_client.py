import os
import sys

# Route WebSocket streaming logic to the central pipeline ingest module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pipeline.ingest import start_pipeline as start_stream, on_message

__all__ = ["start_stream", "on_message"]

if __name__ == "__main__":
    start_stream()