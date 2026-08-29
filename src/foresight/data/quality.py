"""Automated Data Quality & Integrity Engine for Project FORESIGHT."""

from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class QualitySeverity(str, Enum):
    """Severity tier for a data quality finding."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class QualityStatus(str, Enum):
    """Evaluation status of an individual check."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class QualityCheckResult(BaseModel):
    """Outcome payload of a single data quality check."""
    check_name: str
    description: str
    status: QualityStatus
    severity: QualitySeverity
    violated_count: int = 0
    violated_percentage: float = 0.0
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class DataQualityReport(BaseModel):
    """Comprehensive data quality audit report."""
    dataset_name: str
    total_records: int
    total_columns: int
    evaluated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    overall_status: QualityStatus
    quality_score: float = Field(..., ge=0.0, le=100.0)
    checks: list[QualityCheckResult]

    def to_markdown(self) -> str:
        """Render report as a clean GitHub-Flavored Markdown document."""
        status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[self.overall_status.value]
        lines = [
            f"# FORESIGHT — Data Quality Audit Report",
            f"",
            f"**Dataset:** `{self.dataset_name}`  ",
            f"**Audit Timestamp:** `{self.evaluated_at}`  ",
            f"**Total Records:** `{self.total_records:,}` | **Total Columns:** `{self.total_columns}`  ",
            f"**Overall Health Status:** {status_emoji} **{self.overall_status.value}**  ",
            f"**Data Quality Score:** **{self.quality_score:.1f}%**",
            f"",
            f"---",
            f"",
            f"## Quality Check Summary",
            f"",
            f"| Check Name | Status | Severity | Violated Rows | Violated % | Description |",
            f"| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for c in self.checks:
            c_emoji = {"PASS": "✅ PASS", "WARN": "⚠️ WARN", "FAIL": "❌ FAIL"}[c.status.value]
            lines.append(
                f"| `{c.check_name}` | {c_emoji} | `{c.severity.value}` | {c.violated_count:,} | {c.violated_percentage:.2f}% | {c.message} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Detailed Findings & Diagnostic Context",
            f"",
        ])

        for c in self.checks:
            lines.append(f"### `{c.check_name}` ({c.status.value})")
            lines.append(f"- **Description:** {c.description}")
            lines.append(f"- **Finding:** {c.message}")
            if c.details:
                lines.append(f"- **Diagnostics:**")
                lines.append("```json")
                lines.append(json.dumps(c.details, indent=2))
                lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def save(self, json_path: Path | str, md_path: Path | str | None = None) -> None:
        """Save report in JSON and optionally Markdown formats."""
        j_path = Path(json_path)
        j_path.parent.mkdir(parents=True, exist_ok=True)
        with open(j_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        logger.info(f"Saved quality report JSON to {j_path}")

        if md_path:
            m_path = Path(md_path)
            m_path.parent.mkdir(parents=True, exist_ok=True)
            with open(m_path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown())
            logger.info(f"Saved quality report Markdown to {m_path}")


class DataQualityEngine:
    """Automated engine for evaluating dataset integrity, statistical bounds, and leakage."""

    def __init__(
        self,
        date_col: str = "date",
        sku_col: str = "sku_id",
        store_col: str = "store_id",
        quantity_col: str = "quantity",
        price_col: str = "price",
        inventory_col: str = "inventory_level",
        category_col: str = "category",
    ) -> None:
        self.date_col = date_col
        self.sku_col = sku_col
        self.store_col = store_col
        self.quantity_col = quantity_col
        self.price_col = price_col
        self.inventory_col = inventory_col
        self.category_col = category_col

    def check_null_values(self, df: pd.DataFrame) -> QualityCheckResult:
        """Check for missing/null values across all columns."""
        null_counts = df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0].to_dict()
        total_null_rows = int(df.isnull().any(axis=1).sum())
        total_rows = len(df)
        pct = (total_null_rows / total_rows * 100) if total_rows > 0 else 0.0

        if total_null_rows == 0:
            return QualityCheckResult(
                check_name="null_values_check",
                description="Verify zero missing or NaN values across all columns.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="No null or NaN values detected in any column.",
                details={"null_counts_by_column": {}},
            )
        severity = QualitySeverity.ERROR if pct > 1.0 else QualitySeverity.WARNING
        return QualityCheckResult(
            check_name="null_values_check",
            description="Verify zero missing or NaN values across all columns.",
            status=QualityStatus.FAIL if severity == QualitySeverity.ERROR else QualityStatus.WARN,
            severity=severity,
            violated_count=total_null_rows,
            violated_percentage=round(pct, 3),
            message=f"Found {total_null_rows:,} rows ({pct:.2f}%) with null values across {len(cols_with_nulls)} columns.",
            details={"null_counts_by_column": cols_with_nulls},
        )

    def check_duplicates(self, df: pd.DataFrame) -> QualityCheckResult:
        """Check for duplicate rows in the dataset."""
        dupes_count = int(df.duplicated().sum())
        total_rows = len(df)
        pct = (dupes_count / total_rows * 100) if total_rows > 0 else 0.0

        if dupes_count == 0:
            return QualityCheckResult(
                check_name="duplicate_rows_check",
                description="Verify absence of completely duplicate rows.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="Zero duplicate rows detected.",
            )
        return QualityCheckResult(
            check_name="duplicate_rows_check",
            description="Verify absence of completely duplicate rows.",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.ERROR,
            violated_count=dupes_count,
            violated_percentage=round(pct, 3),
            message=f"Found {dupes_count:,} duplicate rows ({pct:.2f}%).",
        )

    def check_duplicate_keys(self, df: pd.DataFrame) -> QualityCheckResult:
        """Check for duplicate primary key combinations (date, sku_id, store_id)."""
        key_cols = [c for c in [self.date_col, self.sku_col, self.store_col] if c in df.columns]
        if len(key_cols) < 2:
            return QualityCheckResult(
                check_name="duplicate_series_keys_check",
                description="Verify uniqueness of primary time-series index keys.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="Key columns not fully present for duplicate key check.",
            )

        dupe_mask = df.duplicated(subset=key_cols)
        dupe_count = int(dupe_mask.sum())
        total_rows = len(df)
        pct = (dupe_count / total_rows * 100) if total_rows > 0 else 0.0

        if dupe_count == 0:
            return QualityCheckResult(
                check_name="duplicate_series_keys_check",
                description="Verify uniqueness of primary (date, sku_id, store_id) keys.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"Primary keys {key_cols} are strictly unique.",
                details={"key_columns": key_cols},
            )
        return QualityCheckResult(
            check_name="duplicate_series_keys_check",
            description="Verify uniqueness of primary (date, sku_id, store_id) keys.",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.CRITICAL,
            violated_count=dupe_count,
            violated_percentage=round(pct, 3),
            message=f"Found {dupe_count:,} duplicate key combinations on {key_cols}.",
            details={"key_columns": key_cols},
        )

    def check_date_validity(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify validity and consistency of date column."""
        if self.date_col not in df.columns:
            return QualityCheckResult(
                check_name="date_validity_check",
                description="Verify presence and format of date column.",
                status=QualityStatus.FAIL,
                severity=QualitySeverity.CRITICAL,
                violated_count=len(df),
                violated_percentage=100.0,
                message=f"Date column '{self.date_col}' is missing.",
            )

        date_series = pd.to_datetime(df[self.date_col], errors="coerce")
        invalid_dates = int(date_series.isnull().sum())
        total_rows = len(df)

        if invalid_dates > 0:
            pct = (invalid_dates / total_rows * 100) if total_rows > 0 else 0.0
            return QualityCheckResult(
                check_name="date_validity_check",
                description="Verify all date values can be successfully parsed into valid timestamps.",
                status=QualityStatus.FAIL,
                severity=QualitySeverity.CRITICAL,
                violated_count=invalid_dates,
                violated_percentage=round(pct, 3),
                message=f"Found {invalid_dates:,} unparseable date values.",
            )

        min_date = date_series.min().strftime("%Y-%m-%d")
        max_date = date_series.max().strftime("%Y-%m-%d")
        return QualityCheckResult(
            check_name="date_validity_check",
            description="Verify all date values can be successfully parsed into valid timestamps.",
            status=QualityStatus.PASS,
            severity=QualitySeverity.INFO,
            violated_count=0,
            violated_percentage=0.0,
            message=f"All dates valid across range {min_date} to {max_date}.",
            details={"min_date": min_date, "max_date": max_date, "total_days": (date_series.max() - date_series.min()).days + 1},
        )

    def check_non_negative_sales(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify sales quantities are non-negative."""
        if self.quantity_col not in df.columns:
            return QualityCheckResult(
                check_name="non_negative_sales_check",
                description="Verify sales quantity is non-negative.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"Quantity column '{self.quantity_col}' not present.",
            )

        neg_mask = df[self.quantity_col] < 0
        neg_count = int(neg_mask.sum())
        total_rows = len(df)
        pct = (neg_count / total_rows * 100) if total_rows > 0 else 0.0

        if neg_count == 0:
            return QualityCheckResult(
                check_name="non_negative_sales_check",
                description="Verify sales quantities are non-negative (quantity >= 0).",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="All sales quantities are non-negative.",
            )
        return QualityCheckResult(
            check_name="non_negative_sales_check",
            description="Verify sales quantities are non-negative (quantity >= 0).",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.CRITICAL,
            violated_count=neg_count,
            violated_percentage=round(pct, 3),
            message=f"Detected {neg_count:,} rows with negative sales quantities.",
        )

    def check_inventory_validity(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify inventory levels and on-order quantities are non-negative and physically plausible."""
        if self.inventory_col not in df.columns:
            return QualityCheckResult(
                check_name="inventory_validity_check",
                description="Verify physical plausibility of inventory levels.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"Inventory column '{self.inventory_col}' not present in dataset.",
            )

        neg_mask = df[self.inventory_col] < 0
        neg_count = int(neg_mask.sum())
        total_rows = len(df)
        pct = (neg_count / total_rows * 100) if total_rows > 0 else 0.0

        if neg_count == 0:
            return QualityCheckResult(
                check_name="inventory_validity_check",
                description="Verify inventory counts are non-negative (inventory_level >= 0).",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="All inventory counts are valid and non-negative.",
            )
        return QualityCheckResult(
            check_name="inventory_validity_check",
            description="Verify inventory counts are non-negative (inventory_level >= 0).",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.CRITICAL,
            violated_count=neg_count,
            violated_percentage=round(pct, 3),
            message=f"Detected {neg_count:,} rows with impossible negative inventory levels.",
        )

    def check_sku_identifiers(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify SKU identifiers follow structured naming convention."""
        if self.sku_col not in df.columns:
            return QualityCheckResult(
                check_name="sku_identifier_format_check",
                description="Verify SKU format conventions.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"SKU column '{self.sku_col}' not present.",
            )

        sku_pattern = re.compile(r"^SKU-\d+$")
        invalid_skus = df[~df[self.sku_col].astype(str).str.match(sku_pattern)]
        invalid_count = len(invalid_skus)
        total_rows = len(df)
        pct = (invalid_count / total_rows * 100) if total_rows > 0 else 0.0

        if invalid_count == 0:
            return QualityCheckResult(
                check_name="sku_identifier_format_check",
                description="Verify all SKU IDs match standard pattern 'SKU-XXXX'.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"All {df[self.sku_col].nunique()} distinct SKU identifiers follow standard formatting.",
                details={"unique_skus": int(df[self.sku_col].nunique())},
            )
        return QualityCheckResult(
            check_name="sku_identifier_format_check",
            description="Verify all SKU IDs match standard pattern 'SKU-XXXX'.",
            status=QualityStatus.WARN,
            severity=QualitySeverity.WARNING,
            violated_count=invalid_count,
            violated_percentage=round(pct, 3),
            message=f"Found {invalid_count:,} rows with non-standard SKU identifier format.",
            details={"sample_invalid": invalid_skus[self.sku_col].unique()[:5].tolist()},
        )

    def check_category_consistency(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify each SKU is mapped to exactly one category."""
        if self.sku_col not in df.columns or self.category_col not in df.columns:
            return QualityCheckResult(
                check_name="category_consistency_check",
                description="Verify single-category consistency per SKU.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="SKU or Category columns not present for consistency check.",
            )

        sku_cat_map = df.groupby(self.sku_col)[self.category_col].nunique()
        inconsistent_skus = sku_cat_map[sku_cat_map > 1]
        inconsistent_count = len(inconsistent_skus)

        if inconsistent_count == 0:
            return QualityCheckResult(
                check_name="category_consistency_check",
                description="Verify each SKU belongs to exactly 1 category hierarchy.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="All SKUs maintain 100% consistent category mappings.",
                details={"categories_count": int(df[self.category_col].nunique())},
            )
        return QualityCheckResult(
            check_name="category_consistency_check",
            description="Verify each SKU belongs to exactly 1 category hierarchy.",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.ERROR,
            violated_count=inconsistent_count,
            violated_percentage=round(inconsistent_count / df[self.sku_col].nunique() * 100, 2),
            message=f"Detected {inconsistent_count} SKUs mapped to multiple contradictory categories.",
            details={"inconsistent_skus": inconsistent_skus.index.tolist()},
        )

    def check_time_continuity(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify continuous daily time-steps for each (SKU, Store) series without gaps."""
        if self.date_col not in df.columns or self.sku_col not in df.columns:
            return QualityCheckResult(
                check_name="time_continuity_check",
                description="Verify time-series continuity.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="Date or SKU columns not present.",
            )

        keys = [self.sku_col]
        if self.store_col in df.columns:
            keys.append(self.store_col)

        dates = pd.to_datetime(df[self.date_col])
        expected_days = (dates.max() - dates.min()).days + 1

        series_counts = df.groupby(keys)[self.date_col].nunique()
        incomplete_series = series_counts[series_counts < expected_days]
        incomplete_count = len(incomplete_series)
        total_series = len(series_counts)

        if incomplete_count == 0:
            return QualityCheckResult(
                check_name="time_continuity_check",
                description=f"Verify every time-series has complete {expected_days} daily steps without gaps.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message=f"All {total_series} time-series possess complete {expected_days} continuous daily steps.",
                details={"total_series": total_series, "expected_days_per_series": expected_days},
            )
        pct = (incomplete_count / total_series * 100) if total_series > 0 else 0.0
        return QualityCheckResult(
            check_name="time_continuity_check",
            description=f"Verify every time-series has complete {expected_days} daily steps without gaps.",
            status=QualityStatus.WARN,
            severity=QualitySeverity.WARNING,
            violated_count=incomplete_count,
            violated_percentage=round(pct, 2),
            message=f"{incomplete_count} of {total_series} series have missing calendar gaps.",
            details={"incomplete_series_count": incomplete_count, "expected_days": expected_days},
        )

    def check_extreme_outliers(self, df: pd.DataFrame) -> QualityCheckResult:
        """Detect extreme demand outliers using IQR method (3.0x threshold)."""
        if self.quantity_col not in df.columns:
            return QualityCheckResult(
                check_name="extreme_outliers_check",
                description="Detect extreme demand spikes.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="Quantity column not present.",
            )

        q25 = df[self.quantity_col].quantile(0.25)
        q75 = df[self.quantity_col].quantile(0.75)
        iqr = q75 - q25
        upper_bound = q75 + 3.0 * iqr

        outliers = df[df[self.quantity_col] > upper_bound]
        outliers_count = len(outliers)
        total_rows = len(df)
        pct = (outliers_count / total_rows * 100) if total_rows > 0 else 0.0

        # Outliers in retail demand are normal during promos, but flagged for visibility
        return QualityCheckResult(
            check_name="extreme_outliers_check",
            description="Audit extreme sales spikes exceeding 3.0x IQR above Q3.",
            status=QualityStatus.PASS if pct < 3.0 else QualityStatus.WARN,
            severity=QualitySeverity.INFO if pct < 3.0 else QualitySeverity.WARNING,
            violated_count=outliers_count,
            violated_percentage=round(pct, 3),
            message=f"Detected {outliers_count:,} extreme demand observations ({pct:.2f}%) above threshold {upper_bound:.1f} units.",
            details={
                "q25": float(q25),
                "q75": float(q75),
                "iqr": float(iqr),
                "upper_bound_3iqr": float(upper_bound),
                "max_value": float(df[self.quantity_col].max()),
            },
        )

    def check_leakage_indicators(self, df: pd.DataFrame) -> QualityCheckResult:
        """Verify no forward-looking target leakage columns exist in the dataset."""
        suspicious_patterns = ["next_day", "future_", "target_lead", "tomorrow_"]
        detected = [col for col in df.columns if any(p in col.lower() for p in suspicious_patterns)]

        if not detected:
            return QualityCheckResult(
                check_name="data_leakage_check",
                description="Verify absence of lookahead or future target leak columns.",
                status=QualityStatus.PASS,
                severity=QualitySeverity.INFO,
                violated_count=0,
                violated_percentage=0.0,
                message="No future lookahead or target leakage columns identified.",
            )
        return QualityCheckResult(
            check_name="data_leakage_check",
            description="Verify absence of lookahead or future target leak columns.",
            status=QualityStatus.FAIL,
            severity=QualitySeverity.CRITICAL,
            violated_count=len(detected),
            violated_percentage=round(len(detected) / len(df.columns) * 100, 2),
            message=f"Detected {len(detected)} suspicious future-leaking columns: {detected}",
            details={"leaking_columns": detected},
        )

    def evaluate(self, df: pd.DataFrame, dataset_name: str = "sales_processed") -> DataQualityReport:
        """Run full battery of quality checks and synthesize quality score."""
        logger.info(f"Running Data Quality Audit on '{dataset_name}' ({len(df):,} rows)...")

        checks = [
            self.check_null_values(df),
            self.check_duplicates(df),
            self.check_duplicate_keys(df),
            self.check_date_validity(df),
            self.check_non_negative_sales(df),
            self.check_inventory_validity(df),
            self.check_sku_identifiers(df),
            self.check_category_consistency(df),
            self.check_time_continuity(df),
            self.check_extreme_outliers(df),
            self.check_leakage_indicators(df),
        ]

        # Calculate quality score
        penalty = 0.0
        has_fail = False
        has_warn = False

        for c in checks:
            if c.status == QualityStatus.FAIL:
                has_fail = True
                if c.severity == QualitySeverity.CRITICAL:
                    penalty += 25.0
                else:
                    penalty += 15.0
            elif c.status == QualityStatus.WARN:
                has_warn = True
                penalty += 5.0

        quality_score = max(0.0, min(100.0, 100.0 - penalty))

        if has_fail:
            overall_status = QualityStatus.FAIL
        elif has_warn:
            overall_status = QualityStatus.WARN
        else:
            overall_status = QualityStatus.PASS

        report = DataQualityReport(
            dataset_name=dataset_name,
            total_records=len(df),
            total_columns=len(df.columns),
            overall_status=overall_status,
            quality_score=quality_score,
            checks=checks,
        )
        logger.info(
            f"Quality Audit complete: Overall Status={overall_status.value}, Score={quality_score:.1f}%"
        )
        return report
