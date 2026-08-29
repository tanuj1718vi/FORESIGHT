"""Model training orchestration, champion selection, and artifact serialization."""

from datetime import datetime
import json
from pathlib import Path
import pandas as pd

from foresight.config.constants import MODELS_DIR, ROOT_DIR
from foresight.features.pipeline import FeatureEngineeringPipeline
from foresight.forecasting.base import BaseForecaster
from foresight.forecasting.ml_models import QuantileGradientBoostingForecaster, XGBoostForecaster
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def train_and_register_champion(
    features_path: Path | str | None = None,
    models_dir: Path | str = MODELS_DIR,
    reports_dir: Path | str | None = None,
    n_splits: int = 3,
    horizon_days: int = 30,
) -> tuple[BaseForecaster, BaseForecaster]:
    """Execute model benchmark, select champion, fit on full history, and persist artifacts.

    Returns:
        Tuple of (Champion Point Forecaster, Probabilistic Quantile Forecaster).
    """
    from foresight.evaluation.benchmark import ModelBenchmarkRunner
    target_models_dir = Path(models_dir)
    target_models_dir.mkdir(parents=True, exist_ok=True)
    target_reports_dir = Path(reports_dir or (ROOT_DIR / "reports"))
    target_reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Features
    f_path = Path(features_path or (ROOT_DIR / "data" / "processed" / "features_engineered.parquet"))
    logger.info(f"Loading feature matrix from {f_path}...")
    df = pd.read_parquet(f_path)

    # 2. Run Benchmark
    benchmark_runner = ModelBenchmarkRunner(
        n_splits=n_splits,
        horizon_days=horizon_days,
        primary_metric="wape",
    )
    report = benchmark_runner.run(df)

    json_report = target_reports_dir / "model_comparison_report.json"
    md_report = target_reports_dir / "model_comparison_report.md"
    report.save(json_report, md_report)

    logger.info(f"Champion Model Selected: '{report.champion_model_name}' (Mean WAPE: {report.champion_mean_wape:.4f})")

    # 3. Train Champion Model on Full Dataset
    pipeline = FeatureEngineeringPipeline()
    feature_names = pipeline.get_feature_names(df)
    X_full = df[feature_names]
    y_full = df["quantity"].values

    # Champion Point Forecaster (XGBoost)
    logger.info("Training production Champion Forecaster (XGBoost) on full dataset...")
    champion = XGBoostForecaster(n_estimators=150, max_depth=6, learning_rate=0.08)
    champion.fit(X_full, y_full)

    # Calibrated Probabilistic Quantile Forecaster (P10, P50, P90)
    logger.info("Training production Probabilistic Forecaster (P10/P50/P90)...")
    quantile_forecaster = QuantileGradientBoostingForecaster(
        quantiles=[0.10, 0.50, 0.90],
        max_iter=100,
        max_depth=6,
    )
    quantile_forecaster.fit(X_full, y_full)

    # 4. Serialize Models
    champ_path = target_models_dir / "champion_forecaster.pkl"
    quantile_path = target_models_dir / "quantile_forecaster.pkl"
    champion.save(champ_path)
    quantile_forecaster.save(quantile_path)
    logger.info(f"Serialized champion model to {champ_path}")
    logger.info(f"Serialized quantile model to {quantile_path}")

    # 5. Save Metadata
    from foresight.forecasting.base import get_current_environment_metadata
    meta = {
        "champion_model_name": champion.name,
        "model_name": champion.name,
        "trained_at": datetime.now().isoformat(),
        "total_training_records": len(df),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "champion_mean_wape": report.champion_mean_wape,
        "metrics": {"mean_wape": report.champion_mean_wape},
        "supported_quantiles": [0.10, 0.50, 0.90],
        "feature_importances": champion.get_feature_importances(),
        "environment": get_current_environment_metadata(),
    }
    meta_path = target_models_dir / "champion_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    logger.info(f"Saved model metadata to {meta_path}")

    return champion, quantile_forecaster


if __name__ == "__main__":
    train_and_register_champion()
