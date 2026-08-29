"""Data drift and concept drift statistical detection engine."""

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from foresight.evaluation.metrics import calculate_wape
from foresight.mlops.schema import (
    ConceptDriftResult,
    DriftSeverity,
    FeatureDriftResult,
    RetrainingAction,
)


def calculate_psi(
    expected: np.ndarray | pd.Series,
    actual: np.ndarray | pd.Series,
    num_buckets: int = 10,
) -> float:
    """Calculate Population Stability Index (PSI) between reference and production distributions.

    Formula: PSI = sum( (A_i - E_i) * ln(A_i / E_i) )
    """
    exp_clean = np.asarray(expected, dtype=float)
    act_clean = np.asarray(actual, dtype=float)

    # Filter out NaNs and infinities
    exp_clean = exp_clean[np.isfinite(exp_clean)]
    act_clean = act_clean[np.isfinite(act_clean)]

    if len(exp_clean) == 0 or len(act_clean) == 0:
        return 0.0

    # Calculate quantile bucket breakpoints from expected distribution
    percentiles = np.linspace(0, 100, num_buckets + 1)
    try:
        breakpoints = np.percentile(exp_clean, percentiles)
    except Exception:
        return 0.0

    # Ensure unique breakpoints
    breakpoints = np.unique(breakpoints)
    if len(breakpoints) < 2:
        return 0.0

    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    # Count occurrences in buckets
    exp_counts, _ = np.histogram(exp_clean, bins=breakpoints)
    act_counts, _ = np.histogram(act_clean, bins=breakpoints)

    # Convert to proportions with smoothing epsilon to prevent division by zero or ln(0)
    eps = 1e-4
    exp_pct = np.maximum(eps, exp_counts / max(1, len(exp_clean)))
    act_pct = np.maximum(eps, act_counts / max(1, len(act_clean)))

    # Re-normalize to sum to 1
    exp_pct /= np.sum(exp_pct)
    act_pct /= np.sum(act_pct)

    psi_values = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
    return round(float(np.sum(psi_values)), 4)


def calculate_ks_test(
    expected: np.ndarray | pd.Series,
    actual: np.ndarray | pd.Series,
) -> tuple[float, float]:
    """Calculate Kolmogorov-Smirnov two-sample test statistic and p-value."""
    exp_clean = np.asarray(expected, dtype=float)
    act_clean = np.asarray(actual, dtype=float)

    exp_clean = exp_clean[np.isfinite(exp_clean)]
    act_clean = act_clean[np.isfinite(act_clean)]

    if len(exp_clean) == 0 or len(act_clean) == 0:
        return 0.0, 1.0

    res = ks_2samp(exp_clean, act_clean)
    return round(float(res.statistic), 4), round(float(res.pvalue), 4)


class DriftDetector:
    """Enterprise statistical monitor evaluating feature and concept drift."""

    def evaluate_feature_drift(
        self,
        ref_series: pd.Series | np.ndarray,
        prod_series: pd.Series | np.ndarray,
        feature_name: str,
    ) -> FeatureDriftResult:
        """Perform KS-test and PSI on an individual continuous feature."""
        ks_stat, ks_pval = calculate_ks_test(ref_series, prod_series)
        psi = calculate_psi(ref_series, prod_series)

        # Drift severity logic
        if psi >= 0.20 and ks_pval < 0.01:
            severity = DriftSeverity.SIGNIFICANT_DRIFT
            is_drifted = True
        elif psi >= 0.10 or ks_pval < 0.05:
            severity = DriftSeverity.MODERATE_DRIFT
            is_drifted = True
        else:
            severity = DriftSeverity.NO_DRIFT
            is_drifted = False

        return FeatureDriftResult(
            feature_name=feature_name,
            ks_statistic=ks_stat,
            ks_p_value=ks_pval,
            psi_score=psi,
            is_drifted=is_drifted,
            drift_severity=severity,
        )

    def evaluate_concept_drift(
        self,
        y_true: pd.Series | np.ndarray,
        y_pred: pd.Series | np.ndarray,
        baseline_wape: float = 0.1894,
    ) -> ConceptDriftResult:
        """Evaluate model performance degradation against baseline benchmark."""
        current_wape = calculate_wape(y_true, y_pred)
        degradation = ((current_wape - baseline_wape) / max(0.01, baseline_wape)) * 100.0

        if degradation >= 50.0:
            action = RetrainingAction.RETRAIN_IMMEDIATELY
            is_concept_drifted = True
            justification = (
                f"Severe performance degradation detected: Rolling WAPE ({current_wape:.2%}) degraded by "
                f"{degradation:+.1f}% over baseline ({baseline_wape:.2%}). Immediate retraining required."
            )
        elif degradation >= 25.0:
            action = RetrainingAction.RETRAIN_RECOMMENDED
            is_concept_drifted = True
            justification = (
                f"Moderate performance degradation: Rolling WAPE ({current_wape:.2%}) breached +25% threshold "
                f"({degradation:+.1f}%). Scheduled model pipeline retraining recommended."
            )
        elif degradation >= 10.0:
            action = RetrainingAction.MONITOR
            is_concept_drifted = False
            justification = (
                f"Mild error increase ({degradation:+.1f}% degradation). Error within tolerance; monitor next cycle."
            )
        else:
            action = RetrainingAction.NO_ACTION
            is_concept_drifted = False
            justification = (
                f"Model performance remains stable: Current WAPE ({current_wape:.2%}) meets benchmark ({baseline_wape:.2%})."
            )

        return ConceptDriftResult(
            baseline_wape=round(baseline_wape, 4),
            current_rolling_wape=round(current_wape, 4),
            wape_degradation_pct=round(degradation, 2),
            is_concept_drifted=is_concept_drifted,
            retraining_action=action,
            justification=justification,
        )
