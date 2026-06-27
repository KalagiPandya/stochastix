<div align="center">

<!--  ╔══════════════════════════════════════════════════════════╗
      ║              STOCHASTIX  —  HERO HEADER                 ║
      ╚══════════════════════════════════════════════════════════╝  -->

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:0d0221,30:1a0533,60:2d1b69,85:4c1d95,100:7c3aed&height=260&section=header&text=STOCHASTIX&fontSize=72&fontColor=e9d5ff&fontAlignY=42&desc=Real-Time%20Financial%20Analytics%20%E2%80%94%20Crypto%20Streams%20%C2%B7%20ML%20Anomaly%20Detection%20%C2%B7%20Cloud%20Native&descAlignY=65&descSize=15&fontStyle=bold&animation=twinkling" width="100%"/>

<br/>

<!-- ── Core Stack Badges ── -->
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit_1.35-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-Local_Dev-FFC832?style=flat-square&logo=duckdb&logoColor=black)](https://duckdb.org)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Production-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.timescale.com)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![Redis](https://img.shields.io/badge/Redis_Streams-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)

<!-- ── Quality & Deployment Badges ── -->
[![Tests](https://img.shields.io/badge/Tests-56_Passing-6d28d9?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![Docker](https://img.shields.io/badge/Docker_Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS_Fargate-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](deploy/aws)
[![GCP](https://img.shields.io/badge/GCP_Cloud_Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](deploy/gcp)
[![Azure](https://img.shields.io/badge/Azure_Container_Apps-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)](deploy/azure)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-7c3aed?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows)

<br/>

> **Stochastix** streams live crypto ticks from Binance, runs a statistical + ML anomaly detection ensemble on every event, persists everything to a time-series database, and surfaces it all on a multi-page Streamlit dashboard — structured the way a real production data pipeline would be.

<br/>

</div>

---

## ⚡ Quick Start

```bash
git clone https://github.com/<you>/Stochastix.git
cd Stochastix

python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-core.txt              # lean build — no Prophet / LSTM

streamlit run app.py
# → http://localhost:8501   |   No .env needed   |   Runs on DuckDB out of the box
```

For the full ML stack (Prophet + LSTM Autoencoder):
```bash
pip install -r requirements.txt
```

---

## 🏗️ Architecture

```
Binance WebSocket  ──►  services/stream.py            ← live tick ingestion + ring buffer
                              │
               ┌──────────────┼───────────────────────┐
               ▼              ▼                       ▼
    services/analytics.py   services/ml_anomaly.py   services/streaming_backbone.py
    SMA · EMA · Bollinger    Isolation Forest          Kafka  or  Redis Streams
    Z-score · ROC            Prophet · LSTM            (every tick published to topics)
               │
               ▼
          pipeline/                                   ← DuckDB  or  PostgreSQL/TimescaleDB
               │
               └──►  auth/security.py                ← JWT + bcrypt + RBAC
```

---

## ✨ Feature Highlights

| Category | What's Inside |
|---|---|
| 📡 **Live Ingestion** | Binance `@trade` WebSocket with REST fallback and auto-reconnect |
| 📊 **Statistics** | Rolling SMA, EMA, Bollinger Bands, Z-score, Rate-of-Change |
| 🤖 **ML Ensemble** | Isolation Forest + Prophet forecast bands + LSTM Autoencoder — majority-vote verdict |
| 🗄️ **Dual Database** | DuckDB for zero-config local dev; PostgreSQL + TimescaleDB for production (single env var to switch) |
| 🔀 **Message Streaming** | Apache Kafka or Redis Streams backbone; ticks, metrics and anomaly events each get their own topic |
| 🔐 **Auth** | JWT access tokens, bcrypt password hashing, `admin / analyst / viewer` role gates on every page |
| 📈 **Dashboard** | OHLC candlestick candles, normalised multi-asset comparison, anomaly alert banner, CSV export |
| 🐳 **Docker** | Multi-stage build; Compose profiles for Postgres, Redis, and Kafka |
| ☁️ **Cloud** | AWS ECS Fargate (+ Terraform), GCP Cloud Run, Azure Container Apps — same image, same env vars |
| 🧪 **Tests** | 56 pytest tests across analytics, ML, streaming, and auth |

---

## ⚙️ Configuration

Copy `.env.example` → `.env`. Everything is optional — unset values fall back to sensible defaults.

**Switch to PostgreSQL / TimescaleDB**
```bash
DB_BACKEND=postgres
POSTGRES_HOST=localhost
POSTGRES_DB=stochastix
POSTGRES_USER=stochastix
POSTGRES_PASSWORD=change-me
```

**Enable Kafka or Redis Streams**
```bash
STREAM_BACKEND=kafka          # or redis
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379/0
```

**Enable authentication**
```bash
JWT_SECRET_KEY=your-random-secret-here
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=change-me
```

---

## 🐳 Docker

```bash
# Default — DuckDB, no extras
docker compose up --build

# With TimescaleDB + Redis
docker compose --profile postgres --profile redis up --build

# With TimescaleDB + Kafka
docker compose --profile postgres --profile kafka up --build
```

---

## ☁️ Cloud Deployment

| Cloud | Service | IaC |
|---|---|---|
| **AWS** | ECS Fargate + ALB + RDS + ElastiCache | Terraform included — [`deploy/aws`](deploy/aws/README.md) |
| **GCP** | Cloud Run + Cloud SQL + Memorystore | Step-by-step guide — [`deploy/gcp`](deploy/gcp/README.md) |
| **Azure** | Container Apps + Azure DB for PostgreSQL + Azure Cache | Step-by-step guide — [`deploy/azure`](deploy/azure/README.md) |

The same Docker image and the same environment variables work across all three providers.

---

## 📊 Dashboard Pages

| Page | Role | What You See |
|---|---|---|
| 🏠 **Home** | everyone | Live ticker tape, SMA/EMA price overlay, anomaly alert banner |
| 📉 **Volatility** | everyone | Bollinger Bands, rolling volatility, market-regime label |
| 🚨 **Anomaly** | everyone | Z-score chart, threshold bands, event log |
| 📊 **Comparison** | everyone | Normalised % performance across BTC/ETH/SOL, OHLC candlesticks |
| 🗄️ **Data Explorer** | everyone | Browse and export ticks, metrics, and candles as CSV |
| 🤖 **ML Anomaly** | analyst + admin | Isolation Forest, Prophet, and LSTM scores with ensemble vote |
| 🔐 **Login** | public | Sign in, register, view JWT token, inspect role matrix |

---

## 🧠 Algorithms

| Algorithm | How It Works |
|---|---|
| **SMA / EMA** | Simple and exponential moving averages over configurable windows |
| **Bollinger Bands** | SMA ± 2 standard deviations — squeeze/expansion regime detection |
| **Rolling Z-score** | Statistical distance from the rolling mean — configurable threshold |
| **Isolation Forest** | Unsupervised outlier detection on price, return, and volatility features |
| **Prophet** | Forecast-band anomaly — flags prices outside the expected trend range |
| **LSTM Autoencoder** | Reconstruction error on 20-tick sliding windows — high error signals anomaly |
| **Majority-Vote Ensemble** | Final label is the majority verdict across all three ML models |

---

## 🗄️ Database Schema

Four tables — schema is identical across DuckDB and TimescaleDB:

| Table | Contents |
|---|---|
| `market_data` | Raw ticks: symbol, price, volume, timestamp |
| `analytics_metrics` | SMA, EMA, Z-score, anomaly flag, and ML score per tick |
| `ohlc_candles` | 1-minute aggregated OHLC + volume |
| `users` | Username, bcrypt hash, role, active flag |

On TimescaleDB, `market_data`, `analytics_metrics`, and `ohlc_candles` are promoted to hypertables with automatic compression after one day and a configurable data-retention policy.

---

## 🧪 Tests

```bash
pytest tests/ -v
```

```
tests/test_analytics.py             30 passed
tests/test_auth.py                   9 passed
tests/test_ml_anomaly.py            12 passed
tests/test_streaming_backbone.py     5 passed
──────────────────────────────────────────────
56 passed in total
```

---

## 🗂️ Project Structure

```
Stochastix/
├── app.py                          ← main dashboard page (Home)
├── pages/
│   ├── 1_Volatility.py
│   ├── 2_Anomaly.py
│   ├── 3_Comparison.py
│   ├── 4_Data_Explorer.py
│   ├── 5_Login.py
│   └── 6_ML_Anomaly.py
├── services/
│   ├── analytics.py                ← SMA, EMA, Z-score, Bollinger, ROC
│   ├── stream.py                   ← Binance WebSocket + ring buffer
│   ├── streaming_backbone.py       ← Kafka / Redis Streams publisher
│   └── ml_anomaly.py              ← Isolation Forest, Prophet, LSTM
├── pipeline/
│   ├── __init__.py                 ← selects DuckDB or Postgres at startup
│   ├── database.py                 ← DuckDB backend
│   └── postgres_db.py             ← PostgreSQL + TimescaleDB backend
├── auth/
│   └── security.py                ← JWT, bcrypt, role decorator
├── deploy/
│   ├── aws/                        ← ECS Fargate + Terraform
│   ├── gcp/                        ← Cloud Run guide
│   └── azure/                      ← Container Apps guide
├── tests/                          ← 56 pytest tests
├── .github/workflows/ci-cd.yml    ← lint → test → build → publish → deploy
├── docker-compose.yml             ← profiles: postgres · redis · kafka
├── Dockerfile
├── requirements.txt               ← full (includes Prophet + torch)
├── requirements-core.txt          ← lean (sklearn only)
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Dashboard | Streamlit + Plotly |
| Data Ingest | Binance WebSocket (`websocket-client`) + REST fallback |
| Message Streaming | Apache Kafka · Redis Streams |
| Database | DuckDB · PostgreSQL + TimescaleDB |
| Analytics | NumPy · Pandas |
| ML | scikit-learn · Prophet · PyTorch |
| Auth | PyJWT · bcrypt |
| Tests | pytest |
| Containers | Docker + Docker Compose |
| Cloud | AWS · GCP · Azure |
| CI/CD | GitHub Actions → GHCR |

---

## 🔮 Roadmap

- [ ] Slack / email alert webhooks on anomaly events
- [ ] Backtesting mode — replay historical ticks through the full pipeline
- [ ] Grafana dashboard wired directly to TimescaleDB
- [ ] Kubernetes Helm chart

---

<div align="center">

<!--  ╔══════════════════════════════════════════════════════════╗
      ║              STOCHASTIX  —  HERO FOOTER                 ║
      ╚══════════════════════════════════════════════════════════╝  -->

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:7c3aed,30:4c1d95,60:2d1b69,85:1a0533,100:0d0221&height=160&section=footer&animation=twinkling" width="100%"/>

</div>

