"""Unit tests for MLflow experiment tracker."""

from pathlib import Path
import pytest

from foresight.mlops.mlflow_tracker import MLflowExperimentTracker
from foresight.mlops.schema import (
    ConceptDriftResult,
    DriftAuditReport,
    FeatureDriftResult,
    RetrainingAction,
)


@pytest.mark.mlops
def test_mlflow_tracker_logging(tmp_path: Path) -> None:
    """Verify MLflow tracker logs experiment runs and monitoring audits."""
    tracker = MLflowExperimentTracker(
        experiment_name="test_experiment",
        tracking_dir=tmp_path / "mlflow",
    )

    # 1. Log training run
    run_id = tracker.log_training_run(
        run_name="test_xgboost_run",
        parameters={"n_estimators": 100, "learning_rate": 0.05},
        metrics={"wape": 0.189, "rmse": 10.36, "r2": 0.863},
    )
    assert run_id is not None
    assert len(run_id) > 10

    # 2. Log drift monitoring run
    drift_rep = DriftAuditReport(
        model_name="XGBoost",
        reference_sample_size=1000,
        production_sample_size=500,
        total_features_monitored=5,
        drifted_features_count=0,
        feature_drift_results=[],
        concept_drift=ConceptDriftResult(
            baseline_wape=0.1894,
            current_rolling_wape=0.1910,
            wape_degradation_pct=0.84,
            is_concept_drifted=False,
            retraining_action=RetrainingAction.NO_ACTION,
            justification="Model is healthy",
        ),
    )
    audit_run_id = tracker.log_drift_monitoring_run(drift_rep)
    assert audit_run_id is not None
