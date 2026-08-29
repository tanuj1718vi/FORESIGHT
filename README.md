# 🔮 Project FORESIGHT
### Enterprise AI-Powered Demand Forecasting & Multi-Echelon Inventory Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat)](https://www.sqlalchemy.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1-EB4034?style=flat)](https://xgboost.readthedocs.io)
[![Tests](https://img.shields.io/badge/Tests-115%20Passed-10B981?style=flat)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ⚡ Quick Start (Easiest Way to Run)

You can run everything directly from the project root using simple 1-line commands:

### 1. 🖥️ Launch the Interactive Web Dashboard
```bash
streamlit run app.py
```
*Or simply:*
```bash
python run_dashboard.py
```
*On Windows, you can also just double-click:* `start_dashboard.bat`  
👉 Opens automatically in your browser at: **[http://localhost:8501](http://localhost:8501)**

---

### 2. 🚀 Launch the FastAPI REST Service
```bash
python run_api.py
```
*On Windows, you can also just double-click:* `start_api.bat`  
👉 Interactive Swagger Documentation: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

### 3. 🔄 Run the Complete End-to-End Pipeline
```bash
python run_pipeline.py
```
*On Windows, you can also just double-click:* `run_pipeline.bat`  
👉 Runs Data Generation ➔ 11-point Quality Audit ➔ Feature Engineering ➔ XGBoost Model Training ➔ Inventory Optimization ➔ Financial Risk Engine ➔ TreeSHAP Explainability ➔ MLOps Drift Monitoring in one pass!

---

### 4. 🎛️ Unified CLI Control (`main.py`)
```bash
python main.py dashboard    # Launch Web UI (port 8501)
python main.py api          # Launch FastAPI REST service (port 8000)
python main.py pipeline     # Re-run full pipeline
python main.py verify       # Run 15-point verification suite
python main.py test         # Run all 115 automated tests
```

---

## 📖 System Architecture & Core Capabilities

```mermaid
graph TD
    subgraph Ingestion & Persistence
        RAW[Raw Data Generator / CSVs] --> SEED[Database Seeder / Migrations]
        SEED --> SQL[(SQLAlchemy SQLite/Postgres DB)]
        RAW --> DQ[11-Point Quality Battery]
        DQ --> PROC[(Clean Sales Dataset)]
    end

    subgraph Feature Engineering
        PROC --> FE[Causal Feature Pipeline]
        FE --> Lags[Autoregressive Lags 1-56]
        FE --> Rolling[Shift-1 Rolling Stats 7-28]
        FE --> Cyclical[Sin/Cos Calendar Waves]
        FE --> FMAT[(Engineered Features Matrix)]
    end

    subgraph Forecasting Engine
        FMAT --> CV[Rolling Origin Walk-Forward CV]
        CV --> ML[Model Suite: Ridge, RF, HistGBM, XGBoost, Quantile]
        ML --> CHAMP[Champion Model: XGBoost WAPE=18.94%]
        ML --> QUANT[Quantile Forecaster: P10, P50, P90]
    end

    subgraph Inventory & Risk Engines
        CHAMP --> INV[Inventory Optimizer]
        QUANT --> INV
        INV --> SS[Safety Stock: Combined Uncertainty]
        INV --> ROP[Continuous Review ROP & Net Stock]
        INV --> EOQ[Wilson EOQ + MOQ Bounds]
        INV --> RISK[Risk Scorer: Unit Loss Integral L z]
        RISK --> REC[Prescriptive Engine: ORDER, EXPEDITE, HOLD, REDUCE, REBALANCE]
    end

    subgraph Explainability & MLOps
        CHAMP --> SHAP[TreeSHAP Global & Local Attribution]
        SHAP --> NARR[Natural Language Business Narratives]
        FMAT --> DRIFT[Drift Detector: KS-Test & PSI]
        DRIFT --> MLFLOW[MLflow / Local Fallback Registry]
    end

    subgraph Presentation & Serving Layer
        REC --> API[FastAPI REST Microservice :8000]
        REC --> DASH[Streamlit Decision Intelligence Dashboard :8501]
        SQL --> API
        SQL --> DASH
    end
```

---

## 🗄️ Database Architecture & Repositories

Project FORESIGHT includes a production-ready **SQLAlchemy 2.0** persistence layer with **Alembic** migration support:

### Core ORM Entities (`src/foresight/database/models/`)
- **`Product`**: SKU master attributes (`sku_id`, `category`, `unit_cost`, `unit_price`, `lead_time_days`, `min_order_qty`, etc.).
- **`SalesRecord`**: Daily sales transactions, pricing, and promotional flags.
- **`InventoryRecord`**: Daily on-hand, on-order, and backorder snapshots.
- **`ForecastRecord`**: Forward point forecasts and quantile intervals ($P_{10}, P_{90}$).
- **`RiskAssessmentRecord`**: Quantified financial exposure, stockout probabilities, and loss integrals.
- **`RecommendationRecord`**: Actionable work orders (`ORDER`, `EXPEDITE`, `REDUCE`, `HOLD`, `MONITOR`, `REBALANCE`).
- **`ModelRun`**: Serialized model hyperparameters, metrics, and artifact paths.

### Repository Pattern (`src/foresight/database/repositories/`)
- `ProductRepository`, `SalesRepository`, `InventoryRepository`, `ForecastRepository`, `RiskRepository`, `RecommendationRepository`, `ModelRepository`.

---

## 🌐 FastAPI REST Microservice Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Liveness & model pre-warm probe |
| `POST` | `/api/v1/forecast/predict` | Real-time point prediction + quantile bands |
| `POST` | `/api/v1/forecast/predict/batch` | Batch forecasting across SKU-store portfolio |
| `POST` | `/api/v1/inventory/optimize` | Continuous review policy (SS, ROP, EOQ, Health) |
| `POST` | `/api/v1/risk/assess` | Financial exposure & unit normal loss integrals |
| `POST` | `/api/v1/risk/prescribe` | Prescriptive work order generation |
| `POST` | `/api/v1/risk/simulate-scenario` | Macroeconomic stress & disruption simulation |
| `POST` | `/api/v1/explain/drivers` | Local TreeSHAP attributions & narratives |
| `GET` | `/api/v1/products` | Database product catalog query with pagination |
| `GET` | `/api/v1/inventory/{sku_id}` | Latest multi-store inventory snapshot |
| `GET` | `/api/v1/risk/{sku_id}` | Real-time financial risk assessment |
| `GET` | `/api/v1/recommendation/{sku_id}` | Active work orders for SKU |
| `GET` | `/api/v1/model-performance` | Walk-forward cross-validation leaderboard |
| `GET` | `/api/v1/data-quality` | Automated 11-point data quality scorecard |

---

## 🧪 Testing & Verification Battery

Run all **115 automated unit, integration, and API tests**:
```bash
python -m pytest -v
```

Run the automated **15-point master end-to-end verification battery**:
```bash
python scripts/e2e_verification.py
```

---

## 📄 License
MIT License. Built for Enterprise Demand Intelligence and Supply Chain Analytics.
