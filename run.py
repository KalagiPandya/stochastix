import os
import sys
import argparse
from threading import Thread
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import uvicorn

# Ensure UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.database import get_db_connection, init_db, DB_PATH
from pipeline.processor import compute_rolling_metrics
from app.alerts import get_recent_alerts

# Initialize FastAPI App
app = FastAPI(
    title="Stochastix Enterprise API",
    description="High-frequency quantitative streaming & market anomaly detection platform",
    version="1.0.0"
)

# Enable CORS for local dev and cross-origin clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION CONFIGURATION ---
ADMIN_USER = os.getenv("STOCHASTIX_USER", "admin")
ADMIN_PASS = os.getenv("STOCHASTIX_PASSWORD", "securepass123")
USER_DB = {ADMIN_USER: ADMIN_PASS}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Handles secure system authentication."""
    user_password = USER_DB.get(form_data.username)
    if not user_password or form_data.password != user_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": form_data.username, "token_type": "bearer"}

# --- STATIC DASHBOARD HOSTING ---
@app.get("/", response_class=FileResponse)
@app.get("/dashboard", response_class=FileResponse)
async def serve_dashboard():
    """Serves the interactive React/Tailwind trading console directly."""
    html_path = os.path.join(BASE_DIR, "dashboard.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h2>Stochastix API is running. dashboard.html not found.</h2>")

@app.get("/health")
async def health_check():
    """Service health probe for deployment monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": os.path.exists(DB_PATH)
    }

# --- DATA & ANALYTICS API ENDPOINTS ---
@app.get("/api/market/{symbol}")
async def get_market_analytics(symbol: str, token: str = Depends(oauth2_scheme)):
    """
    Queries DuckDB in read-only mode, computes quantitative rolling indicators,
    and returns formatted JSON payload for the front-end charts.
    """
    try:
        df = compute_rolling_metrics(symbol, window=20)
        
        if df is None or df.empty:
            return {
                "symbol": symbol,
                "data": [],
                "metrics": {
                    "price": 0.0,
                    "sma": 0.0,
                    "ema": 0.0,
                    "volatility": 0.0,
                    "z_score": 0.0,
                    "bb_upper": 0.0,
                    "bb_lower": 0.0,
                    "vwap": 0.0,
                    "anomaly": False
                }
            }
        
        latest = df.iloc[-1]
        
        # Take the most recent 30-50 points for chart rendering
        chart_df = df.tail(35)
        chart_data = []
        for _, row in chart_df.iterrows():
            ts_str = row['timestamp'].strftime("%H:%M:%S") if hasattr(row['timestamp'], 'strftime') else str(row['timestamp'])
            chart_data.append({
                "time": ts_str,
                "price": float(row['price']),
                "volume": float(row['volume']),
                "sma": float(row.get('sma_14', row['price'])),
                "bb_upper": float(row.get('bb_upper', row['price'])),
                "bb_lower": float(row.get('bb_lower', row['price']))
            })
            
        return {
            "symbol": symbol,
            "data": chart_data,
            "metrics": {
                "price": float(latest['price']),
                "sma": float(latest.get('sma_14', latest['price'])),
                "ema": float(latest.get('ema_12', latest['price'])),
                "volatility": float(latest.get('volatility', 0.0)),
                "z_score": float(latest.get('z_score', 0.0)),
                "bb_upper": float(latest.get('bb_upper', latest['price'])),
                "bb_lower": float(latest.get('bb_lower', latest['price'])),
                "vwap": float(latest.get('vwap', latest['price'])),
                "anomaly": bool(latest.get('is_anomaly', False))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts(limit: int = 15, token: str = Depends(oauth2_scheme)):
    """Returns the most recent system volatility and anomaly alerts."""
    try:
        df = get_recent_alerts(limit=limit)
        if df.empty:
            return {"alerts": []}
        records = []
        for _, row in df.iterrows():
            ts_str = row['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row['timestamp'], 'strftime') else str(row['timestamp'])
            records.append({
                "timestamp": ts_str,
                "symbol": row['symbol'],
                "alert_type": row['alert_type'],
                "message": row['message'],
                "severity": row['severity']
            })
        return {"alerts": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- BACKGROUND STREAM WORKER ---
def run_background_worker(simulate=False):
    """Launches the live Coinbase ingestion or offline simulator."""
    init_db()
    if simulate:
        print("[WORKER] Launching synthetic market data simulator...")
        from pipeline.simulator import MarketSimulator
        sim = MarketSimulator()
        sim.run(interval_sec=0.5)
    else:
        print("[WORKER] Launching live Coinbase WebSocket ingestion stream...")
        from pipeline.ingest import start_pipeline
        start_pipeline()

# --- MASTER ENTRYPOINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stochastix Server")
    parser.add_argument("--simulate", action="store_true", help="Run with simulated market data (offline demo)")
    parser.add_argument("--no-stream", action="store_true", help="Disable background market streamer")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Port (default: 8000)")
    args = parser.parse_args()

    init_db()

    # Launch background market streamer if not disabled
    if not args.no_stream:
        stream_thread = Thread(target=run_background_worker, args=(args.simulate,), daemon=True)
        stream_thread.start()
    
    print(f"[SERVER] Stochastix Enterprise Platform starting at http://localhost:{args.port}")
    print(f"[SERVER] Interactive Trading Console available at http://localhost:{args.port}/dashboard")
    print(f"[SERVER] REST API Docs available at http://localhost:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port)