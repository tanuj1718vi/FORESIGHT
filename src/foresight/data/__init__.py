"""Data ingestion, generation, loading, processing, quality auditing, and EDA module for Project FORESIGHT."""

from foresight.data.eda import (
    ABCXYZSegmentation,
    DemandProfile,
    EDAEngine,
    EDASummaryReport,
    InventoryHealthProfile,
    SKUPerformanceItem,
)
from foresight.data.generator import (
    generate_benchmark_dataset,
    generate_product_catalog,
    save_raw_datasets,
)
from foresight.data.loader import (
    load_csv_data,
    load_parquet_data,
    load_processed_sales,
    load_raw_inventory,
    load_raw_products,
    load_raw_sales,
)
from foresight.data.processor import (
    align_calendar_grid,
    process_and_save_data,
    process_sales_and_inventory,
    validate_raw_frames,
)
from foresight.data.quality import (
    DataQualityEngine,
    DataQualityReport,
    QualityCheckResult,
    QualitySeverity,
    QualityStatus,
)
from foresight.data.run_eda import run_eda_pipeline
from foresight.data.run_quality_audit import run_data_quality_audit
from foresight.data.schema import (
    InventorySnapshotRecord,
    ProcessedTimeSeriesRecord,
    ProductMasterRecord,
    RawSalesRecord,
)

__all__ = [
    "RawSalesRecord",
    "ProductMasterRecord",
    "InventorySnapshotRecord",
    "ProcessedTimeSeriesRecord",
    "generate_benchmark_dataset",
    "generate_product_catalog",
    "save_raw_datasets",
    "load_csv_data",
    "load_parquet_data",
    "load_raw_sales",
    "load_raw_products",
    "load_raw_inventory",
    "load_processed_sales",
    "validate_raw_frames",
    "align_calendar_grid",
    "process_sales_and_inventory",
    "process_and_save_data",
    "QualitySeverity",
    "QualityStatus",
    "QualityCheckResult",
    "DataQualityReport",
    "DataQualityEngine",
    "run_data_quality_audit",
    "DemandProfile",
    "SKUPerformanceItem",
    "ABCXYZSegmentation",
    "InventoryHealthProfile",
    "EDASummaryReport",
    "EDAEngine",
    "run_eda_pipeline",
]
