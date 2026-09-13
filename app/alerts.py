import os
import sys

# Route to pipeline alerts module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.alerts import trigger_alert, get_recent_alerts

__all__ = ["trigger_alert", "get_recent_alerts"]
