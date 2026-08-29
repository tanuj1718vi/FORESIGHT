"""Time-series cross-validation, forecasting metrics, and benchmarking suite."""

from foresight.evaluation.benchmark import (
    BenchmarkLeaderboardReport,
    ModelBenchmarkRunner,
    ModelBenchmarkSummary,
)
from foresight.evaluation.cross_validation import RollingOriginCV, TimeSeriesCVFold
from foresight.evaluation.metrics import (
    MetricScoreSet,
    evaluate_predictions,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_absolute_scaled_error,
    pinball_loss,
    root_mean_squared_error,
    symmetric_mean_absolute_percentage_error,
    weighted_absolute_percentage_error,
)

__all__ = [
    "MetricScoreSet",
    "calculate_wape",
    "mean_absolute_error",
    "root_mean_squared_error",
    "weighted_absolute_percentage_error",
    "symmetric_mean_absolute_percentage_error",
    "mean_absolute_percentage_error",
    "mean_absolute_scaled_error",
    "pinball_loss",
    "evaluate_predictions",
    "TimeSeriesCVFold",
    "RollingOriginCV",
    "ModelBenchmarkSummary",
    "BenchmarkLeaderboardReport",
    "ModelBenchmarkRunner",
]
