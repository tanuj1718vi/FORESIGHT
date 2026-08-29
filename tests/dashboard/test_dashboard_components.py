"""Unit and smoke tests for dashboard data loaders and Plotly chart renderers."""

import pandas as pd
import pytest

from foresight.dashboard.components.charts import (
    plot_eoq_cost_curves,
    plot_forecast_with_intervals,
    plot_portfolio_health_donut,
    plot_risk_matrix_scatter,
)
from foresight.dashboard.data_provider import (
    load_engineered_features,
    load_inventory_recommendations,
    load_prescriptive_recommendations,
    load_risk_assessments,
)


@pytest.mark.dashboard
def test_dashboard_data_provider_loaders() -> None:
    """Verify all dashboard data loader functions return populated dataframes."""
    df_feat = load_engineered_features()
    df_inv = load_inventory_recommendations()
    df_rec = load_prescriptive_recommendations()
    df_risk = load_risk_assessments()

    assert not df_feat.empty
    assert not df_inv.empty
    assert not df_rec.empty
    assert not df_risk.empty

    assert len(df_inv) == 250
    assert len(df_risk) == 250
    assert "recommended_action" in df_inv.columns
    assert "composite_risk_score" in df_risk.columns


@pytest.mark.dashboard
def test_plot_forecast_with_intervals() -> None:
    """Verify forecast trajectory figure generation with P10-P90 ribbons."""
    dates_hist = ["2024-01-01", "2024-01-02", "2024-01-03"]
    y_hist = [10.0, 12.0, 15.0]
    dates_fc = ["2024-01-04", "2024-01-05", "2024-01-06"]
    y_fc = [14.0, 16.0, 18.0]
    y_p10 = [11.0, 13.0, 15.0]
    y_p90 = [17.0, 19.0, 21.0]

    fig = plot_forecast_with_intervals(dates_hist, y_hist, dates_fc, y_fc, y_p10, y_p90)
    assert fig is not None
    assert len(fig.data) >= 3


@pytest.mark.dashboard
def test_plot_portfolio_health_donut() -> None:
    """Verify portfolio health donut chart generation."""
    health_counts = {"OPTIMAL": 127, "UNDERSTOCKED": 56, "STOCKOUT_IMMINENT": 59, "OVERSTOCKED": 8}
    fig = plot_portfolio_health_donut(health_counts)
    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].hole == 0.55


@pytest.mark.dashboard
def test_plot_eoq_cost_curves() -> None:
    """Verify Wilson EOQ total cost curve figure generation."""
    fig = plot_eoq_cost_curves(annual_demand=3650.0, order_cost=50.0, unit_cost=20.0, holding_rate=0.20, optimal_eoq=302.0)
    assert fig is not None
    assert len(fig.data) >= 3


@pytest.mark.dashboard
def test_plot_risk_matrix_scatter() -> None:
    """Verify risk matrix scatter figure generation."""
    risk_df = pd.DataFrame([
        {"days_of_supply": 2.0, "stockout_probability": 0.85, "lost_margin_risk": 1500.0, "risk_level": "CRITICAL", "sku_id": "SKU-1", "store_id": "STORE-1", "composite_risk_score": 85.0, "total_financial_exposure": 1500.0},
        {"days_of_supply": 25.0, "stockout_probability": 0.05, "lost_margin_risk": 50.0, "risk_level": "LOW", "sku_id": "SKU-2", "store_id": "STORE-1", "composite_risk_score": 5.0, "total_financial_exposure": 50.0},
    ])
    fig = plot_risk_matrix_scatter(risk_df)
    assert fig is not None
    assert len(fig.data) >= 1
