"""Drift monitoring CLI runner, automated drift audit, and report generator."""

from pathlib import Path
import numpy as np
import pandas as pd

from foresight.config.constants import MODELS_DIR, PROCESSED_DATA_DIR, REPORTS_DIR
from foresight.forecasting.base import BaseForecaster
from foresight.mlops.drift_detector import DriftDetector
from foresight.mlops.mlflow_tracker import MLflowExperimentTracker
from foresight.mlops.schema import DriftAuditReport
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def run_drift_monitoring_audit(
    features_path: Path | str | None = None,
    model_path: Path | str | None = None,
    reports_dir: Path | str = REPORTS_DIR,
    baseline_split_pct: float = 0.80,
) -> DriftAuditReport:
    """Execute automated statistical data drift and concept drift monitoring."""
    f_path = Path(features_path or (PROCESSED_DATA_DIR / "features_engineered.parquet"))
    m_path = Path(model_path or (MODELS_DIR / "champion_forecaster.pkl"))
    rep_dir = Path(reports_dir)
    rep_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data and Model
    logger.info(f"Loading features from {f_path}...")
    df = pd.read_parquet(f_path).sort_values("date").reset_index(drop=True)
    logger.info(f"Loading champion forecaster from {m_path}...")
    champion = BaseForecaster.load(m_path)
    features = champion.feature_names_ or []

    # 2. Chronological Split into Reference and Production Windows
    split_idx = int(len(df) * baseline_split_pct)
    ref_df = df.iloc[:split_idx]
    prod_df = df.iloc[split_idx:]
    logger.info(f"Reference window: {len(ref_df):,} rows | Production window: {len(prod_df):,} rows")

    # 3. Evaluate Feature Distribution Drift (KS & PSI)
    detector = DriftDetector()
    feature_drift_results = []
    drifted_count = 0

    for feat in features:
        if feat in ref_df.columns and feat in prod_df.columns:
            res = detector.evaluate_feature_drift(
                ref_series=ref_df[feat],
                prod_series=prod_df[feat],
                feature_name=feat,
            )
            feature_drift_results.append(res)
            if res.is_drifted:
                drifted_count += 1

    # 4. Evaluate Concept Drift (Rolling Production WAPE)
    prod_X = prod_df[features].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y_true = prod_df["quantity"].values
    y_pred = champion.predict(prod_X)

    concept_drift_res = detector.evaluate_concept_drift(
        y_true=y_true,
        y_pred=y_pred,
        baseline_wape=0.1894,  # Champion benchmark WAPE from Phase 06
    )

    # 5. Compile Audit Report
    report = DriftAuditReport(
        model_name=champion.name,
        reference_sample_size=len(ref_df),
        production_sample_size=len(prod_df),
        total_features_monitored=len(feature_drift_results),
        drifted_features_count=drifted_count,
        feature_drift_results=feature_drift_results,
        concept_drift=concept_drift_res,
    )

    # 6. Save Reports
    json_path = rep_dir / "drift_monitoring_report.json"
    md_path = rep_dir / "drift_monitoring_report.md"

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report.to_markdown())

    logger.info(f"Saved drift monitoring report JSON to {json_path}")
    logger.info(f"Saved drift monitoring report Markdown to {md_path}")

    # 7. Log to MLflow
    tracker = MLflowExperimentTracker()
    tracker.log_drift_monitoring_run(report)

    return report


if __name__ == "__main__":
    run_drift_monitoring_audit()
