import os
import sys

# Ensure UTF-8 output on Windows consoles if possible
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Route database access to the centralized pipeline database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pipeline.database import get_db_connection, init_db, DB_PATH

__all__ = ["get_db_connection", "init_db", "DB_PATH"]

if __name__ == "__main__":
    init_db()