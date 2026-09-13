# STOCHASTIX // Real-Time Quantitative Streaming & Anomaly Detection Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-Columnar%20OLAP-FFF000.svg)](https://duckdb.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Stochastix** is a high-frequency cryptocurrency streaming, quantitative time-series analytics, and statistical anomaly detection engine. It connects directly to the Coinbase WebSocket exchange feed (`BTC-USD`, `ETH-USD`), writes high-throughput tick matches into an embedded **DuckDB** columnar store, computes rolling statistical indicators in real-time, and surfaces them through both a **Modern React Trading Terminal** and a **Multi-Page Streamlit Analytics Console**.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Data Ingestion Layer
        A[Coinbase Pro WebSocket\nwss://ws-feed.exchange.coinbase.com] -->|Live Trade Ticks| B[pipeline/ingest.py]
        S[pipeline/simulator.py\nGBM + Jump-Diffusion] -.->|Synthetic Ticks / Offline| B
    end

    subgraph Storage & Time-Series Engine
        B -->|High-Throughput Write| C[(DuckDB Columnar DB\nstochastix.db)]
        D[pipeline/processor.py] <-->|Vectorized SQL & Pandas| C
    end

    subgraph Quantitative Analytics
        D --> E[Rolling SMA-14 & EMA-12]
        D --> F[Rolling Volatility \u03c3]
        D --> G[Bollinger Bands \u00b12\u03c3]
        D --> H[Dynamic Z-Scores & Anomaly Flags]
    end

    subgraph Delivery & Presentation Layer
        C --> I[FastAPI Backend\nrun.py :8000]
        I --> J[React + Tailwind Trading Terminal\n/dashboard]
        I --> K[REST & OAuth2 API Endpoints\n/api/market/{symbol}]
        C --> L[Streamlit Multi-Page Portal\nfrontend/app.py :8501]
    end
```

---

## ✨ Key Features

1. **Sub-Millisecond Ingestion**: Connects to the Coinbase WebSocket feed with automatic reconnection, heartbeat ping/pong, and resilient ISO-8601 timestamp normalization.
2. **Embedded Columnar Storage**: Leverages **DuckDB** for zero-latency in-memory and on-disk columnar analytical queries without requiring standalone database servers.
3. **Quantitative Metrics Engine**:
   - **Simple Moving Averages (SMA-14)** and **Exponential Moving Averages (EMA-12)**.
   - **Rolling Standard Deviation & Volatility ($\sigma$)**.
   - **Bollinger Bands ($\mu \pm 2\sigma$)**.
   - **Dynamic Z-Score ($Z = \frac{P_t - \mu}{\sigma}$)** with statistical threshold anomaly flagging ($|Z| > 2.2$).
   - **Volume Weighted Average Price (VWAP)**.
4. **Realistic Market Simulator**: Built-in Geometric Brownian Motion (GBM) with Merton Jump-Diffusion to inject realistic price trends, volatility clusters, and flash moves for offline testing and demos.
5. **Dual User Interfaces**:
   - **FastAPI + React Dashboard**: High-impact, dark-mode terminal with OAuth2 authentication, interactive Recharts graphs, Bollinger Band envelopes, and operational risk alerts.
   - **Streamlit Multi-Page Portal**: Comprehensive exploratory data analysis dashboard with volatility distribution curves and anomaly inspection logs.

---

## 📁 Repository Structure

```
Stochastix/
├── app/
│   ├── alerts.py               # Operational risk alert engine & DuckDB alert logger
│   ├── analytics.py            # Statistical calculation routines
│   └── dashboard.py            # Streamlit single-page console
├── backend/
│   ├── analytics/              # Analytical wrappers for multi-node setups
│   ├── database/               # Centralized database connectors
│   ├── ingestion/              # WebSocket ingestion workers
│   └── main.py                 # Backend processing node entrypoint
├── data/                       # Local database storage directory
├── frontend/
│   ├── app.py                  # Streamlit multi-page application home
│   └── pages/
│       ├── 1_Dashboard.py      # Real-time streaming price flow
│       ├── 2_Volatility_Analysis.py  # Volatility & Z-score distribution
│       └── 3_Anomaly_Log.py    # Anomaly alerts and flagged events
├── pipeline/
│   ├── database.py             # DuckDB schema initialization & connection manager
│   ├── ingest.py               # Coinbase WebSocket trade ingestion client
│   ├── processor.py            # Vectorized rolling metrics & Z-score processor
│   └── simulator.py            # Synthetic GBM + Jump-Diffusion market simulator
├── dashboard.html              # Standalone & FastAPI-served React trading terminal
├── run.py                      # Master FastAPI server + WebSocket launcher
├── Dockerfile                  # Containerized deployment blueprint
├── docker-compose.yml          # Multi-service container orchestrator
├── render.yaml                 # 1-Click Render cloud deployment blueprint
├── Procfile                    # Cloud process declaration
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/KalagiPandya/stochastix.git
cd stochastix

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Install required packages
pip install -r requirements.txt
```

---

### 2. Running the Application

#### Option A: FastAPI + React Trading Terminal (Recommended)

Launch the complete full-stack platform (API + background live streamer + web dashboard):

```bash
python run.py
```

- **Interactive Dashboard**: Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard) (or [http://localhost:8000](http://localhost:8000))
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Default Credentials**: `admin` / `securepass123`

#### Option B: Offline / Synthetic Simulator Mode

Run without an active internet connection or to demo instant volatility anomalies:

```bash
python run.py --simulate
```

#### Option C: Streamlit Multi-Page Analytics Portal

Launch the multi-page exploratory analytics portal:

```bash
streamlit run frontend/app.py
```

- Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` or `/dashboard` | Serves the React Trading Terminal | No |
| `GET` | `/health` | Service health and database check | No |
| `POST` | `/token` | Authenticates user & returns Bearer token | Form Data |
| `GET` | `/api/market/{symbol}` | Returns rolling metrics, bands, and tick array | Bearer Token |
| `GET` | `/api/alerts` | Returns recent volatility and anomaly alerts | Bearer Token |

### Sample Response (`GET /api/market/BTC-USD`):

```json
{
  "symbol": "BTC-USD",
  "data": [
    {
      "time": "15:02:46",
      "price": 64492.25,
      "volume": 0.3565,
      "sma": 64501.10,
      "bb_upper": 64580.20,
      "bb_lower": 64422.00
    }
  ],
  "metrics": {
    "price": 64492.25,
    "sma": 64501.10,
    "ema": 64498.40,
    "volatility": 39.55,
    "z_score": -0.22,
    "bb_upper": 64580.20,
    "bb_lower": 64422.00,
    "vwap": 64495.30,
    "anomaly": false
  }
}
```

---

## 🐳 Container & Cloud Deployment

### Deploy with Docker Compose

```bash
docker compose up --build
```
- React Trading Terminal: `http://localhost:8000`
- Streamlit Analytics Portal: `http://localhost:8501`

### Deploy to Render

1. Connect your GitHub repository `KalagiPandya/stochastix` to [Render](https://render.com).
2. Render will automatically detect `render.yaml` and configure the service.
3. Your live API and Dashboard will be accessible at `https://stochastix-quant-terminal.onrender.com`.

### Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Select your repository `KalagiPandya/stochastix`.
3. Set **Main file path** to `frontend/app.py`.
4. Click **Deploy**.

---

## 📄 License

This project is licensed under the MIT License.
