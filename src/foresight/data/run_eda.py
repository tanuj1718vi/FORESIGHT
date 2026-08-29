"""CLI runner for Exploratory Data Analysis (EDA) and Visualization generation."""

from pathlib import Path
from foresight.config.constants import ROOT_DIR
from foresight.data.eda import EDAEngine
from foresight.data.loader import load_processed_sales
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def run_eda_pipeline(
    reports_dir: Path | None = None,
    figures_dir: Path | None = None,
) -> None:
    """Execute complete EDA pipeline, saving statistical reports and Plotly figures."""
    target_reports_dir = reports_dir or (ROOT_DIR / "reports")
    target_figures_dir = figures_dir or (target_reports_dir / "figures")

    target_reports_dir.mkdir(parents=True, exist_ok=True)
    target_figures_dir.mkdir(parents=True, exist_ok=True)

    df = load_processed_sales()
    engine = EDAEngine()

    logger.info("Computing EDA statistical summary and ABC/XYZ segmentation...")
    report = engine.generate_full_report(df, dataset_name="sales_processed")

    json_path = target_reports_dir / "eda_summary_report.json"
    md_path = target_reports_dir / "eda_summary_report.md"
    report.save(json_path=json_path, md_path=md_path)

    # Generate and save interactive visualizations
    logger.info("Generating Plotly interactive visualizations...")

    fig_trend = engine.plot_demand_trend_and_seasonality(df)
    fig_trend.write_html(target_figures_dir / "demand_trend.html")

    fig_seasonality = engine.plot_day_of_week_seasonality(df)
    fig_seasonality.write_html(target_figures_dir / "seasonality_by_category.html")

    fig_abc_xyz = engine.plot_abc_xyz_matrix(df)
    fig_abc_xyz.write_html(target_figures_dir / "abc_xyz_matrix.html")

    # Sample top SKU inventory profile
    top_sku = report.segmentation.top_revenue_skus[0]
    fig_inv = engine.plot_sku_inventory_profile(df, sku_id=top_sku, store_id="STORE-001")
    fig_inv.write_html(target_figures_dir / "top_sku_inventory_dynamics.html")

    logger.info(f"EDA pipeline completed! Saved HTML figures to {target_figures_dir}")


if __name__ == "__main__":
    run_eda_pipeline()
