"""Unit tests for EDA and Business Intelligence Engine."""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from foresight.data.eda import (
    ABCXYZSegmentation,
    DemandProfile,
    EDAEngine,
    EDASummaryReport,
    InventoryHealthProfile,
)


@pytest.fixture
def mock_eda_df() -> pd.DataFrame:
    """Create a realistic multi-SKU mock dataset for EDA engine unit testing."""
    dates = pd.date_range("2024-01-01", "2024-01-30", freq="D")
    skus = ["SKU-1001", "SKU-1002", "SKU-1003"]
    categories = {"SKU-1001": "Electronics", "SKU-1002": "Apparel", "SKU-1003": "Grocery"}
    prices = {"SKU-1001": 100.0, "SKU-1002": 50.0, "SKU-1003": 10.0}
    costs = {"SKU-1001": 60.0, "SKU-1002": 25.0, "SKU-1003": 5.0}

    rows = []
    for d in dates:
        for sku in skus:
            # SKU-1001: high volume & price; SKU-1003: volatile/intermittent
            if sku == "SKU-1001":
                qty = 20 + (5 if d.weekday() in [5, 6] else 0)
            elif sku == "SKU-1002":
                qty = 10
            else:
                qty = 0 if d.day % 3 != 0 else 15

            rows.append({
                "date": d,
                "sku_id": sku,
                "store_id": "STORE-001",
                "product_name": f"Product {sku}",
                "category": categories[sku],
                "subcategory": "General",
                "quantity": qty,
                "price": prices[sku],
                "unit_cost": costs[sku],
                "is_promoted": d.day in [10, 11, 12],
                "inventory_level": max(0, 100 - qty * 2),
                "units_on_order": 50,
                "backorders": 5 if (sku == "SKU-1001" and d.day == 25) else 0,
                "demand_pattern": "intermittent" if sku == "SKU-1003" else "regular",
            })

    return pd.DataFrame(rows)


@pytest.mark.unit
def test_compute_demand_profile(mock_eda_df: pd.DataFrame) -> None:
    """Verify compute_demand_profile correctly calculates volume, revenue, and seasonality indices."""
    engine = EDAEngine()
    profile = engine.compute_demand_profile(mock_eda_df)

    assert isinstance(profile, DemandProfile)
    assert profile.total_sales_units > 0
    assert profile.total_revenue > 0
    assert len(profile.weekday_seasonality_indices) == 7
    assert profile.promotional_demand_lift >= 0.5


@pytest.mark.unit
def test_compute_sku_segmentation(mock_eda_df: pd.DataFrame) -> None:
    """Verify compute_sku_segmentation produces valid ABC and XYZ classifications."""
    engine = EDAEngine()
    seg = engine.compute_sku_segmentation(mock_eda_df)

    assert isinstance(seg, ABCXYZSegmentation)
    assert seg.total_skus == 3
    assert len(seg.sku_details) == 3

    # SKU-1001 has highest price and volume -> should be Class A
    sku1 = next(item for item in seg.sku_details if item.sku_id == "SKU-1001")
    assert sku1.abc_class == "A"

    # All segments must be 2 characters (e.g. AX, AY, etc.)
    for item in seg.sku_details:
        assert len(item.abc_xyz_segment) == 2
        assert item.abc_class in ["A", "B", "C"]
        assert item.xyz_class in ["X", "Y", "Z"]


@pytest.mark.unit
def test_compute_inventory_health(mock_eda_df: pd.DataFrame) -> None:
    """Verify compute_inventory_health calculates turnover, stockout rate, and DOS."""
    engine = EDAEngine()
    health = engine.compute_inventory_health(mock_eda_df)

    assert isinstance(health, InventoryHealthProfile)
    assert health.total_cogs > 0
    assert health.average_inventory_value > 0
    assert health.annualized_inventory_turnover > 0
    assert health.overall_days_of_supply > 0
    assert health.total_backordered_units == 5


@pytest.mark.unit
def test_eda_summary_report_and_save(mock_eda_df: pd.DataFrame, tmp_path: Path) -> None:
    """Verify generate_full_report creates markdown/json exportable report."""
    engine = EDAEngine()
    report = engine.generate_full_report(mock_eda_df, dataset_name="mock_test")

    assert isinstance(report, EDASummaryReport)
    assert report.total_records == len(mock_eda_df)

    md = report.to_markdown()
    assert "# FORESIGHT — Exploratory Data Analysis & Business Intelligence" in md
    assert "ABC / XYZ Portfolio Segmentation Matrix" in md

    json_out = tmp_path / "eda_test.json"
    md_out = tmp_path / "eda_test.md"
    report.save(json_out, md_out)

    assert json_out.exists()
    assert md_out.exists()


@pytest.mark.unit
def test_plotly_figures_generation(mock_eda_df: pd.DataFrame) -> None:
    """Verify Plotly figure builder methods return valid go.Figure objects."""
    engine = EDAEngine()

    fig1 = engine.plot_demand_trend_and_seasonality(mock_eda_df)
    assert isinstance(fig1, go.Figure)

    fig2 = engine.plot_day_of_week_seasonality(mock_eda_df)
    assert isinstance(fig2, go.Figure)

    fig3 = engine.plot_abc_xyz_matrix(mock_eda_df)
    assert isinstance(fig3, go.Figure)

    fig4 = engine.plot_sku_inventory_profile(mock_eda_df, sku_id="SKU-1001", store_id="STORE-001")
    assert isinstance(fig4, go.Figure)
