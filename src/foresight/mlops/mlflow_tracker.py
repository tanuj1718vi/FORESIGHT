"""MLflow experiment tracking, model registry, and audit logger with resilient JSON fallback."""

import json
from pathlib import Path
from typing import Any
import uuid

try:
    import mlflow
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

from foresight.config.constants import MODELS_DIR
from foresight.mlops.schema import DriftAuditReport
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class MLflowExperimentTracker:
    """Enterprise experiment tracker managing MLflow runs and artifact governance."""

    def __init__(
        self,
        experiment_name: str = "foresight_demand_forecasting",
        tracking_dir: Path | str | None = None,
    ) -> None:
        self.experiment_name = experiment_name
        self.tracking_dir = Path(tracking_dir or (MODELS_DIR / "mlflow_runs"))
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        self.has_mlflow = HAS_MLFLOW
        self.tracking_mode = "MLFLOW" if HAS_MLFLOW else "LOCAL_JSON_FALLBACK"

        if HAS_MLFLOW:
            mlflow.set_tracking_uri(f"file:///{self.tracking_dir.resolve().as_posix()}")
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"Initialized MLflow tracker [MODE: MLFLOW] at {self.tracking_dir} for experiment '{experiment_name}'")
        else:
            logger.info(f"MLflow not installed in environment; using local structured JSON run registry [MODE: LOCAL_JSON_FALLBACK] at {self.tracking_dir}")

    def get_tracking_status(self) -> dict[str, Any]:
        """Expose current MLOps tracking mode and backend status."""
        return {
            "tracking_mode": self.tracking_mode,
            "has_mlflow": self.has_mlflow,
            "experiment_name": self.experiment_name,
            "tracking_dir": str(self.tracking_dir),
        }

    def log_training_run(
        self,
        run_name: str,
        parameters: dict[str, Any],
        metrics: dict[str, float],
        tags: dict[str, str] | None = None,
        artifact_path: Path | str | None = None,
    ) -> str:
        """Log a model training experiment run to MLflow or fallback file store."""
        run_id = f"run-{uuid.uuid4().hex[:12]}"

        if HAS_MLFLOW:
            with mlflow.start_run(run_name=run_name) as run:
                clean_params = {k: str(v) for k, v in parameters.items()}
                mlflow.log_params(clean_params)
                mlflow.log_metrics(metrics)
                run_tags = {"project": "FORESIGHT", "stage": "production_candidate"}
                if tags:
                    run_tags.update(tags)
                mlflow.set_tags(run_tags)
                if artifact_path and Path(artifact_path).exists():
                    mlflow.log_artifact(str(artifact_path))
                run_id = str(run.info.run_id)
        else:
            # Local registry fallback
            run_payload = {
                "run_id": run_id,
                "run_name": run_name,
                "tracking_mode": self.tracking_mode,
                "parameters": parameters,
                "metrics": metrics,
                "tags": tags or {},
                "artifact_path": str(artifact_path) if artifact_path else None,
            }
            run_file = self.tracking_dir / f"{run_id}.json"
            with open(run_file, "w", encoding="utf-8") as f:
                json.dump(run_payload, f, indent=2)

        logger.info(f"Logged training run '{run_name}' via {self.tracking_mode} (Run ID: {run_id})")
        return run_id

    def log_drift_monitoring_run(self, report: DriftAuditReport) -> str:
        """Log drift monitoring audit metrics to MLflow or fallback file store."""
        run_id = f"audit-{uuid.uuid4().hex[:12]}"
        metrics = {
            "total_features_monitored": float(report.total_features_monitored),
            "drifted_features_count": float(report.drifted_features_count),
            "drifted_features_pct": (report.drifted_features_count / max(1, report.total_features_monitored)) * 100.0,
            "baseline_wape": float(report.concept_drift.baseline_wape),
            "current_rolling_wape": float(report.concept_drift.current_rolling_wape),
            "wape_degradation_pct": float(report.concept_drift.wape_degradation_pct),
        }

        if HAS_MLFLOW:
            with mlflow.start_run(run_name=f"drift_audit_{report.audit_date[:10]}") as run:
                mlflow.log_metrics(metrics)
                mlflow.set_tags({
                    "audit_type": "drift_monitoring",
                    "retraining_action": report.concept_drift.retraining_action.value,
                })
                run_id = str(run.info.run_id)
        else:
            audit_payload = {
                "run_id": run_id,
                "tracking_mode": self.tracking_mode,
                "audit_date": report.audit_date,
                "metrics": metrics,
                "retraining_action": report.concept_drift.retraining_action.value,
            }
            audit_file = self.tracking_dir / f"{run_id}.json"
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(audit_payload, f, indent=2)

        logger.info(f"Logged drift audit run via {self.tracking_mode} (Run ID: {run_id})")
        return run_id
