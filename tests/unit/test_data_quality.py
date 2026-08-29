"""Unit tests for Data Quality Engine, individual integrity audits, and reporting."""

from pathlib import Path
import pandas as pd
import pytest

from foresight.data.quality import (
    DataQualityEngine,
    DataQualityReport,
    QualitySeverity,
    QualityStatus,
)


@pytest.fixture
def clean_sample_df() -> pd.DataFrame:
    """Provide a valid, clean synthetic dataset for quality baseline tests."""
    dates = pd.date_range("2024-01-01", "2024-01-10", freq="D")
    records = []
    for d in dates:
        records.append({
            "date": d,
            "sku_id": "SKU-1001",
            "store_id": "STORE-001",
            "category": "Electronics",
            "quantity": 15,
            "price": 29.99,
            "inventory_level": 100,
        })
    return pd.DataFrame(records)


@pytest.mark.unit
def test_check_null_values_pass(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_null_values passes on complete clean data."""
    engine = DataQualityEngine()
    res = engine.check_null_values(clean_sample_df)
    assert res.status == QualityStatus.PASS
    assert res.violated_count == 0


@pytest.mark.unit
def test_check_null_values_failure(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_null_values flags missing values."""
    corrupt = clean_sample_df.copy()
    corrupt.loc[0, "price"] = None
    corrupt.loc[2, "quantity"] = None

    engine = DataQualityEngine()
    res = engine.check_null_values(corrupt)
    assert res.status in [QualityStatus.WARN, QualityStatus.FAIL]
    assert res.violated_count == 2
    assert "price" in res.details["null_counts_by_column"]


@pytest.mark.unit
def test_check_duplicates_detection(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_duplicates flags duplicate rows."""
    dupe_df = pd.concat([clean_sample_df, clean_sample_df.iloc[[0]]], ignore_index=True)
    engine = DataQualityEngine()

    res = engine.check_duplicates(dupe_df)
    assert res.status == QualityStatus.FAIL
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_duplicate_series_keys(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_duplicate_keys flags duplicate (date, sku_id, store_id) keys."""
    dupe_keys = pd.concat([clean_sample_df, clean_sample_df.iloc[[0]]], ignore_index=True)
    engine = DataQualityEngine()

    res = engine.check_duplicate_keys(dupe_keys)
    assert res.status == QualityStatus.FAIL
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_negative_sales(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_non_negative_sales flags negative quantities."""
    corrupt = clean_sample_df.copy()
    corrupt.loc[1, "quantity"] = -10
    engine = DataQualityEngine()

    res = engine.check_non_negative_sales(corrupt)
    assert res.status == QualityStatus.FAIL
    assert res.severity == QualitySeverity.CRITICAL
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_impossible_inventory(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_inventory_validity flags negative inventory counts."""
    corrupt = clean_sample_df.copy()
    corrupt.loc[3, "inventory_level"] = -5
    engine = DataQualityEngine()

    res = engine.check_inventory_validity(corrupt)
    assert res.status == QualityStatus.FAIL
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_sku_identifiers(clean_sample_df: pd.DataFrame) -> None:
    """Verify check_sku_identifiers flags non-compliant SKU formats."""
    corrupt = clean_sample_df.copy()
    corrupt.loc[0, "sku_id"] = "INVALID_SKU_NAME"
    engine = DataQualityEngine()

    res = engine.check_sku_identifiers(corrupt)
    assert res.status == QualityStatus.WARN
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_category_consistency() -> None:
    """Verify check_category_consistency flags SKUs mapped to multiple categories."""
    inconsistent_df = pd.DataFrame({
        "sku_id": ["SKU-1001", "SKU-1001"],
        "category": ["Electronics", "Apparel"],
    })
    engine = DataQualityEngine()

    res = engine.check_category_consistency(inconsistent_df)
    assert res.status == QualityStatus.FAIL
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_time_continuity_gap() -> None:
    """Verify check_time_continuity detects missing calendar gaps."""
    gap_df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-05"]),
        "sku_id": ["SKU-1001", "SKU-1001"],
        "store_id": ["STORE-001", "STORE-001"],
    })
    engine = DataQualityEngine()

    res = engine.check_time_continuity(gap_df)
    assert res.status == QualityStatus.WARN
    assert res.violated_count == 1


@pytest.mark.unit
def test_check_leakage_indicators() -> None:
    """Verify check_leakage_indicators flags suspicious future lookahead columns."""
    leaking_df = pd.DataFrame({
        "date": ["2024-01-01"],
        "quantity": [10],
        "future_sales_t1": [15],
    })
    engine = DataQualityEngine()

    res = engine.check_leakage_indicators(leaking_df)
    assert res.status == QualityStatus.FAIL
    assert res.violated_count == 1


@pytest.mark.unit
def test_data_quality_report_evaluation_and_saving(clean_sample_df: pd.DataFrame, tmp_path: Path) -> None:
    """Verify evaluate produces a valid 100% score report that renders Markdown and JSON."""
    engine = DataQualityEngine()
    report = engine.evaluate(clean_sample_df, dataset_name="unit_test_dataset")

    assert isinstance(report, DataQualityReport)
    assert report.overall_status == QualityStatus.PASS
    assert report.quality_score == 100.0
    assert len(report.checks) == 11

    # Test Markdown rendering
    md_text = report.to_markdown()
    assert "# FORESIGHT — Data Quality Audit Report" in md_text
    assert "100.0%" in md_text

    # Test File Persistence
    json_target = tmp_path / "report.json"
    md_target = tmp_path / "report.md"
    report.save(json_path=json_target, md_path=md_target)

    assert json_target.exists()
    assert md_target.exists()
