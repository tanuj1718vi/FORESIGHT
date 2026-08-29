"""Pydantic schemas and data contracts for MLOps and Drift Monitoring."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class DriftSeverity(str, Enum):
    """Data drift severity classification."""
    NO_DRIFT = "NO_DRIFT"              # PSI < 0.10, KS p >= 0.05
    MODERATE_DRIFT = "MODERATE_DRIFT"  # 0.10 <= PSI < 0.20 or KS p < 0.05
    SIGNIFICANT_DRIFT = "SIGNIFICANT_DRIFT"  # PSI >= 0.20 and KS p < 0.01


class RetrainingAction(str, Enum):
    """Prescriptive model retraining action decision."""
    NO_ACTION = "NO_ACTION"
    MONITOR = "MONITOR"
    RETRAIN_RECOMMENDED = "RETRAIN_RECOMMENDED"
    RETRAIN_IMMEDIATELY = "RETRAIN_IMMEDIATELY"


class FeatureDriftResult(BaseModel):
    """Statistical drift test result for an individual continuous feature."""
    feature_name: str
    ks_statistic: float = Field(..., ge=0.0, le=1.0, description="Kolmogorov-Smirnov maximum divergence")
    ks_p_value: float = Field(..., ge=0.0, le=1.0, description="KS test p-value")
    psi_score: float = Field(..., ge=0.0, description="Population Stability Index")
    is_drifted: bool
    drift_severity: DriftSeverity


class ConceptDriftResult(BaseModel):
    """Model performance degradation and concept drift evaluation."""
    baseline_wape: float
    current_rolling_wape: float
    wape_degradation_pct: float
    is_concept_drifted: bool
    retraining_action: RetrainingAction
    justification: str


class DriftAuditReport(BaseModel):
    """Comprehensive data drift, concept drift, and model health report."""
    audit_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    model_name: str
    reference_sample_size: int
    production_sample_size: int
    total_features_monitored: int
    drifted_features_count: int
    feature_drift_results: list[FeatureDriftResult]
    concept_drift: ConceptDriftResult

    def to_markdown(self) -> str:
        """Render drift audit report as clean GitHub Flavored Markdown."""
        lines = [
            "# FORESIGHT — Enterprise MLOps & Drift Monitoring Report",
            "",
            f"**Audit Timestamp:** `{self.audit_date}`  ",
            f"**Production Champion Model:** `{self.model_name}`  ",
            f"**Reference Baseline Window:** `{self.reference_sample_size:,}` samples  ",
            f"**Production Evaluation Window:** `{self.production_sample_size:,}` samples  ",
            "",
            "---",
            "",
            "## 1. Executive Concept Drift & Retraining Decision",
            "",
            f"| Metric | Value | Operational Status |",
            f"| :--- | :---: | :--- |",
            f"| **Baseline Validation WAPE** | `{self.concept_drift.baseline_wape:.2%}` | Reference benchmark |",
            f"| **Current Production Rolling WAPE** | **`{self.concept_drift.current_rolling_wape:.2%}`** | Live performance |",
            f"| **Performance Degradation Delta** | `{self.concept_drift.wape_degradation_pct:+.1f}%` | Threshold: +25% |",
            f"| **Prescriptive Retraining Directive** | **`{self.concept_drift.retraining_action.value}`** | Automated governance rule |",
            "",
            f"> **Audit Justification:** *{self.concept_drift.justification}*",
            "",
            "---",
            "",
            "## 2. Feature Distribution Shift (KS Test & Population Stability Index)",
            "",
            f"- **Total Monitored Predictors:** `{self.total_features_monitored}`",
            f"- **Drifted Features Detected:** **`{self.drifted_features_count}`** / `{self.total_features_monitored}`",
            "",
            "| Feature Name | KS Statistic (D) | KS p-value | PSI Score | Drift Severity | Status |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        for f in self.feature_drift_results:
            status_icon = "🟢 STABLE" if not f.is_drifted else ("🟡 SHIFT" if f.drift_severity == DriftSeverity.MODERATE_DRIFT else "🔴 DRIFT")
            lines.append(
                f"| `{f.feature_name}` | `{f.ks_statistic:.4f}` | `{f.ks_p_value:.4f}` | `{f.psi_score:.4f}` | `{f.drift_severity.value}` | **{status_icon}** |"
            )

        return "\n".join(lines)
