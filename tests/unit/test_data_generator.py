"""Unit tests for synthetic benchmark dataset generator."""

from datetime import date
import pytest

from foresight.data.generator import generate_benchmark_dataset, generate_product_catalog


@pytest.mark.unit
def test_product_catalog_generation() -> None:
    """Verify generate_product_catalog produces exact requested number of SKUs and categories."""
    num_skus = 20
    df = generate_product_catalog(num_skus=num_skus, seed=42)

    assert len(df) == num_skus
    assert set(df["category"].unique()).issubset({
        "Electronics", "Apparel", "Home & Kitchen", "Grocery", "Health & Beauty"
    })
    assert (df["unit_price"] > df["unit_cost"]).all()
    assert (df["lead_time_days"] > 0).all()
    assert (df["min_order_qty"] > 0).all()


@pytest.mark.unit
def test_benchmark_dataset_generator_reproducibility() -> None:
    """Verify generator produces identical deterministic datasets under fixed random seed."""
    d1 = generate_benchmark_dataset(num_skus=5, num_days=10, seed=123)
    d2 = generate_benchmark_dataset(num_skus=5, num_days=10, seed=123)

    assert d1["sales"].equals(d2["sales"])
    assert d1["products"].equals(d2["products"])
    assert d1["inventory"].equals(d2["inventory"])


@pytest.mark.unit
def test_benchmark_dataset_dimensions_and_types() -> None:
    """Verify generated dataset contains exact expected time-series row count and valid bounds."""
    num_skus = 10
    num_days = 30
    num_stores = 5
    expected_rows = num_skus * num_stores * num_days

    data = generate_benchmark_dataset(
        num_skus=num_skus,
        start_date=date(2024, 1, 1),
        num_days=num_days,
        seed=42,
    )

    sales_df = data["sales"]
    inv_df = data["inventory"]
    prod_df = data["products"]

    assert len(sales_df) == expected_rows
    assert len(inv_df) == expected_rows
    assert len(prod_df) == num_skus

    # Verify no negative quantities or inventories
    assert (sales_df["quantity"] >= 0).all()
    assert (sales_df["price"] > 0).all()
    assert (inv_df["inventory_level"] >= 0).all()
    assert (inv_df["backorders"] >= 0).all()
