"""Model explainability CLI runner and SHAP report generator."""

from datetime import datetime
import json
from pathlib import Path
import pandas as pd

from foresight.config.constants import MODELS_DIR, PROCESSED_DATA_DIR, REPORTS_DIR
from foresight.explainability.schema import ExplainabilityReport
from foresight.explainability.shap_explainer import ForecastExplainer
from foresight.forecasting.base import BaseForecaster
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def run_explainability_audit(
    features_path: Path | str | None = None,
    model_path: Path | str | None = None,
    reports_dir: Path | str = REPORTS_DIR,
    sample_size: int = 2000,
) -> ExplainabilityReport:
    """Execute TreeSHAP analysis, render attribution figures, and serialize audit reports."""
    f_path = Path(features_path or (PROCESSED_DATA_DIR / "features_engineered.parquet"))
    m_path = Path(model_path or (MODELS_DIR / "champion_forecaster.pkl"))
    rep_dir = Path(reports_dir)
    fig_dir = rep_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data and Champion Model
    logger.info(f"Loading features from {f_path}...")
    df = pd.read_parquet(f_path)
    logger.info(f"Loading champion forecaster from {m_path}...")
    champion = BaseForecaster.load(m_path)

    explainer = ForecastExplainer(champion)

    # 2. Global Feature Importance
    logger.info(f"Sampling {sample_size:,} observations for global TreeSHAP evaluation...")
    sample_df = df.sample(min(sample_size, len(df)), random_state=42).reset_index(drop=True)
    global_importances = explainer.compute_global_importance(sample_df)

    # Category importance aggregation
    cat_breakdown: dict[str, float] = {}
    for g in global_importances:
        cat_breakdown[g.category.value] = round(cat_breakdown.get(g.category.value, 0.0) + g.relative_importance_pct, 2)

    # Save Global Bar Figure
    bar_path = fig_dir / "shap_global_summary.html"
    explainer.plot_global_importance_bar(global_importances, output_path=bar_path)

    # 3. Local Explanations
    # Select 3 interesting sample rows
    promo_rows = df[df["is_promoted"] == True]
    sample_rows = [
        promo_rows.iloc[0] if len(promo_rows) > 0 else df.iloc[100],
        df.iloc[500],
        df.iloc[1500],
    ]

    local_explanations = []
    for row in sample_rows:
        exp = explainer.explain_observation(
            row_features=row,
            sku_id=str(row.get("sku_id", "SKU-1001")),
            store_id=str(row.get("store_id", "STORE-001")),
            date=str(row.get("date", "2024-06-15")),
        )
        local_explanations.append(exp)

    # Save Waterfall Figure for the first (promotional) sample
    waterfall_path = fig_dir / "shap_waterfall_sample.html"
    explainer.plot_waterfall_explanation(local_explanations[0], output_path=waterfall_path)

    # 4. Compile Audit Report
    report = ExplainabilityReport(
        model_name=champion.name,
        sample_records_evaluated=len(sample_df),
        global_feature_importances=global_importances,
        category_importance_breakdown=cat_breakdown,
        sample_explanations=local_explanations,
    )

    json_path = rep_dir / "explainability_report.json"
    md_path = rep_dir / "explainability_report.md"

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report.to_markdown())

    logger.info(f"Saved explainability report JSON to {json_path}")
    logger.info(f"Saved explainability report Markdown to {md_path}")

    return report


if __name__ == "__main__":
    run_explainability_audit()
