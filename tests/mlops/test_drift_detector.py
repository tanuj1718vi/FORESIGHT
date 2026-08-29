"""Unit tests for statistical drift detection algorithms (PSI, KS-test, and Concept Drift)."""

import numpy as np
import pytest

from foresight.mlops.drift_detector import (
    DriftDetector,
    calculate_ks_test,
    calculate_psi,
)
from foresight.mlops.schema import DriftSeverity, RetrainingAction


@pytest.mark.mlops
def test_psi_stable_vs_drifted_distributions() -> None:
    """Verify PSI < 0.10 on stable distribution and PSI > 0.20 on heavily drifted distribution."""
    np.random.seed(42)
    ref = np.random.normal(loc=100.0, scale=15.0, size=3000)
    stable_prod = np.random.normal(loc=100.2, scale=14.9, size=1500)
    drifted_prod = np.random.normal(loc=125.0, scale=25.0, size=1500)

    psi_stable = calculate_psi(ref, stable_prod)
    psi_drifted = calculate_psi(ref, drifted_prod)

    assert psi_stable < 0.05
    assert psi_drifted > 0.20


@pytest.mark.mlops
def test_ks_test_divergence() -> None:
    """Verify KS-test produces high p-value on identical dist and p < 0.01 on drifted dist."""
    np.random.seed(42)
    ref = np.random.exponential(scale=10.0, size=2000)
    stable_prod = np.random.exponential(scale=10.1, size=1000)
    drifted_prod = np.random.exponential(scale=20.0, size=1000)

    _, p_stable = calculate_ks_test(ref, stable_prod)
    stat_drift, p_drift = calculate_ks_test(ref, drifted_prod)

    assert p_stable > 0.05
    assert p_drift < 0.001
    assert stat_drift > 0.15


@pytest.mark.mlops
def test_evaluate_feature_drift() -> None:
    """Verify DriftDetector correctly classifies DriftSeverity."""
    detector = DriftDetector()
    ref = np.random.normal(50, 5, 2000)
    prod_drifted = np.random.normal(70, 10, 1000)

    res = detector.evaluate_feature_drift(ref, prod_drifted, "lag_1")
    assert res.is_drifted is True
    assert res.drift_severity in [DriftSeverity.MODERATE_DRIFT, DriftSeverity.SIGNIFICANT_DRIFT]


@pytest.mark.mlops
def test_concept_drift_retraining_trigger() -> None:
    """Verify rolling WAPE degradation triggers appropriate RetrainingAction."""
    detector = DriftDetector()
    y_true = np.array([100.0, 150.0, 200.0, 120.0])

    # 1. Healthy predictions (WAPE ~ 5%)
    y_pred_healthy = np.array([98.0, 145.0, 205.0, 122.0])
    res_healthy = detector.evaluate_concept_drift(y_true, y_pred_healthy, baseline_wape=0.1894)
    assert res_healthy.retraining_action == RetrainingAction.NO_ACTION

    # 2. Severely degraded predictions (WAPE > 40%)
    y_pred_degraded = np.array([40.0, 60.0, 90.0, 50.0])
    res_degraded = detector.evaluate_concept_drift(y_true, y_pred_degraded, baseline_wape=0.1894)
    assert res_degraded.retraining_action == RetrainingAction.RETRAIN_IMMEDIATELY
    assert res_degraded.is_concept_drifted is True
