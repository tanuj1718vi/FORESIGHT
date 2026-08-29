"""CLI runner and orchestrator for Data Quality Auditing."""

from pathlib import Path
from foresight.config.constants import ROOT_DIR
from foresight.data.loader import load_processed_sales
from foresight.data.quality import DataQualityEngine
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def run_data_quality_audit(
    reports_dir: Path | None = None,
) -> None:
    """Run data quality evaluation on processed dataset and persist JSON and Markdown reports."""
    target_reports_dir = reports_dir or (ROOT_DIR / "reports")
    target_reports_dir.mkdir(parents=True, exist_ok=True)

    df = load_processed_sales()
    engine = DataQualityEngine()

    report = engine.evaluate(df, dataset_name="sales_processed")

    json_path = target_reports_dir / "data_quality_report.json"
    md_path = target_reports_dir / "data_quality_report.md"

    report.save(json_path=json_path, md_path=md_path)
    logger.info(f"Quality audit completed successfully! Score: {report.quality_score:.1f}% ({report.overall_status.value})")


if __name__ == "__main__":
    run_data_quality_audit()
