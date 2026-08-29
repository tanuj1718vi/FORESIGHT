# FORESIGHT — Target System Architecture

Project FORESIGHT is an end-to-end intelligence system that transforms raw point-of-sale (POS) and multi-echelon inventory records into predictive demand curves and automated inventory decisions.

---

## 1. System Topology

```text
                        ┌───────────────────────────────┐
                        │         Data Sources          │
                        │  (POS, ERP, Catalog, Promos)  │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │      Data Quality Engine      │
                        │  - Schema Contracts (Pydantic)│
                        │  - Anomaly & Outlier Audits   │
                        │  - Missing Timestamp Imputation│
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Feature Engineering Engine  │
                        │  - Leakage-Safe Lag Operators │
                        │  - Rolling Demand & Volatility│
                        │  - Calendar & Promo Signals   │
                        └───────────────┬───────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
    ┌───────────────────────────────┐       ┌───────────────────────────────┐
    │       Forecasting Engine      │       │     Inventory Optimization    │
    │  - Classical Time Series      │       │  - Dynamic Safety Stock       │
    │  - Gradient Boosted Trees     │       │  - Lead-Time Demand ROP       │
    │  - Probabilistic (P10/50/90)  │       │  - Days of Supply & EOQ       │
    └───────────────┬───────────────┘       └───────────────┬───────────────┘
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │       Risk & Alert Engine     │
                        │  - Stockout Risk Classifier   │
                        │  - Overstock Capital Tie-up   │
                        │  - Velocity / Drift Triggers  │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │     Recommendation Engine     │
                        │  - Prescriptions: ORDER/HOLD  │
                        │  - Exact Reorder Quantities   │
                        │  - Urgency Triage (P0 -> P3)  │
                        └───────────────┬───────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
    ┌───────────────────────────────┐       ┌───────────────────────────────┐
    │     FastAPI Microservice      │       │  Streamlit Command Dashboard  │
    │  - REST Endpoints for ERP     │       │  - Executive Overview         │
    │  - Simulation / What-If Engine│       │  - Interactive SKU Explorer   │
    │  - Pydantic Payloads & Docs   │       │  - Scenario Simulation Studio │
    └───────────────────────────────┘       └───────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Configuration Layer (`foresight.config`)
- **Pydantic BaseSettings**: Strongly typed system parameters.
- **Hierarchical Overrides**: `base.yaml` $\rightarrow$ `environments/{env}.yaml` $\rightarrow$ `.env` $\rightarrow$ OS environment variables.
- **Runtime Enums**: Deterministic state representations (`RiskLevel`, `RecommendationAction`, `Environment`).

### 2.2 Logging & Observability (`foresight.utils.logger`)
- Structured JSON outputs formatted for log ingestors (DataDog, CloudWatch, ELK).
- Rotating file handler with strict byte-capping and rotation count.
- Thread-safe root logger isolation.

### 2.3 Data & Quality Engine (`foresight.data`)
- Machine-readable validation reports verifying schema compliance, zero-leakage constraints, and time-continuity.

### 2.4 Feature Engineering (`foresight.features`)
- Strictly causal feature transforms ensuring no future information reaches training sets.

### 2.5 Forecasting Engine (`foresight.forecasting`)
- Rolling-origin validation protocols.
- Probabilistic quantiles ($P_{10}, P_{50}, P_{90}$).

### 2.6 Inventory & Risk Engine (`foresight.inventory`, `foresight.risk`)
- Dynamic service-level calculations under stochastic lead times and demand distributions.
