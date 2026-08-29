"""Full End-to-End Pipeline Runner for Project FORESIGHT.

Run directly via:
    python run_pipeline.py
"""

import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure src/ is on python path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from foresight.data.generator import generate_benchmark_dataset, save_raw_datasets
from foresight.data.loader import load_processed_sales
from foresight.data.processor import process_and_save_data
from foresight.data.quality import DataQualityEngine
from foresight.database.seeder import seed_database
from foresight.database.session import init_db
from foresight.explainability.run_explainability import run_explainability_audit
from foresight.features.pipeline import FeatureEngineeringPipeline
from foresight.forecasting.trainer import train_and_register_champion
from foresight.inventory.portfolio_optimizer import optimize_portfolio_inventory
from foresight.mlops.run_monitoring import run_drift_monitoring_audit
from foresight.risk.run_risk_audit import run_portfolio_risk_audit


def run_all():
    start = time.time()
    print("=" * 75)
    print("PROJECT FORESIGHT - Executing Complete End-to-End Intelligence Pipeline")
    print("=" * 75)

    # Step 1: Generate & Process Benchmark Data
    print("\n[Step 1/9] Generating & standardizing benchmark dataset (182,500 rows)...")
    raw_data = generate_benchmark_dataset(num_skus=50, num_days=730, seed=42)
    save_raw_datasets(raw_data)
    sales_clean = process_and_save_data()
    print(f"  [OK] Clean processed sales dataset ready ({len(sales_clean):,} rows).")

    # Step 2: Quality Engine
    print("\n[Step 2/9] Running 11-point data quality & integrity battery...")
    dq_rep = DataQualityEngine().evaluate(sales_clean)
    print(f"  [OK] Data quality score: {dq_rep.quality_score:.1f}% ({dq_rep.overall_status.value})")

    # Step 3: Feature Engineering
    print("\n[Step 3/9] Building 60 causal predictive features (lags, rolling stats, calendar encodings)...")
    pipe = FeatureEngineeringPipeline()
    feat_df = pipe.fit_transform(sales_clean)
    feat_path = Path("data/processed/features_engineered.parquet")
    feat_path.parent.mkdir(parents=True, exist_ok=True)
    feat_df.to_parquet(feat_path, index=False)
    print(f"  [OK] Engineered feature matrix: {len(feat_df):,} rows, {len(feat_df.columns)} columns.")

    # Step 4: Model Training & Cross-Validation
    print("\n[Step 4/9] Training champion forecaster (XGBoost + Monotonic Quantile GBM)...")
    champ, quant = train_and_register_champion(features_path=feat_path)
    print(f"  [OK] Champion model '{champ.name}' registered.")

    # Step 5: Inventory Optimization
    print("\n[Step 5/9] Optimizing multi-echelon inventory policies across 250 portfolio nodes...")
    inv_df, inv_rep = optimize_portfolio_inventory(features_path=feat_path)
    print(f"  [OK] Total Committed Working Capital: ${inv_rep.total_working_capital_committed:,.2f}")

    # Step 6: Risk Audit & Prescriptive Actions
    print("\n[Step 6/9] Quantifying financial exposure & generating prescriptive work orders...")
    risk_df, recs_df, risk_rep = run_portfolio_risk_audit()
    print(f"  [OK] Total Exposure: ${risk_rep.total_financial_exposure:,.2f} | Orders: {risk_rep.action_distribution}")

    # Step 7: TreeSHAP Explainability
    print("\n[Step 7/9] Computing TreeSHAP global feature attributions & executive narratives...")
    exp_rep = run_explainability_audit(features_path=feat_path)
    print(f"  [OK] Top Predictive Feature: {exp_rep.global_feature_importances[0].feature_name} ({exp_rep.global_feature_importances[0].relative_importance_pct:.1f}%)")

    # Step 8: MLOps Drift Monitoring
    print("\n[Step 8/9] Performing statistical data drift (KS/PSI) & concept drift evaluation...")
    drift_rep = run_drift_monitoring_audit(features_path=feat_path)
    print(f"  [OK] Live Rolling WAPE: {drift_rep.concept_drift.current_rolling_wape:.2%} -> Action: {drift_rep.concept_drift.retraining_action.value}")

    # Step 9: Database Synchronization
    print("\n[Step 9/9] Synchronizing SQLAlchemy database with updated pipeline state...")
    init_db()
    seed_counts = seed_database()
    print(f"  [OK] Database synchronized: {seed_counts}")

    elapsed = time.time() - start
    print("\n" + "=" * 75)
    print(f"PIPELINE EXECUTION COMPLETE ({elapsed:.2f}s) - All Models & Artifacts Updated!")
    print("=" * 75)


if __name__ == "__main__":
    run_all()
