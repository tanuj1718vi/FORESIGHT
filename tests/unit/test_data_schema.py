"""Unit tests for Pydantic data schemas and constraints."""

from datetime import date
import pytest
from pydantic import ValidationError

from foresight.data.schema import (
    InventorySnapshotRecord,
    ProcessedTimeSeriesRecord,
    ProductMasterRecord,
    RawSalesRecord,
)


@pytest.mark.unit
def test_valid_raw_sales_record() -> None:
    """Verify RawSalesRecord successfully validates legitimate sales transaction."""
    rec = RawSalesRecord(
        date=date(2024, 1, 15),
        sku_id="SKU-1001",
        store_id="STORE-001",
        quantity=15,
        price=29.99,
        is_promoted=True,
    )
    assert rec.quantity == 15
    assert rec.price == 29.99
    assert rec.is_promoted is True


@pytest.mark.unit
def test_invalid_negative_sales_quantity() -> None:
    """Verify RawSalesRecord rejects negative sales quantity."""
    with pytest.raises(ValidationError):
        RawSalesRecord(
            date=date(2024, 1, 15),
            sku_id="SKU-1001",
            store_id="STORE-001",
            quantity=-5,
            price=29.99,
        )


@pytest.mark.unit
def test_invalid_non_positive_price() -> None:
    """Verify RawSalesRecord rejects zero or negative price."""
    with pytest.raises(ValidationError):
        RawSalesRecord(
            date=date(2024, 1, 15),
            sku_id="SKU-1001",
            store_id="STORE-001",
            quantity=5,
            price=0.0,
        )


@pytest.mark.unit
def test_valid_product_master_record() -> None:
    """Verify ProductMasterRecord validates product metadata constraints."""
    prod = ProductMasterRecord(
        sku_id="SKU-1010",
        product_name="Electronics Audio Item 10",
        category="Electronics",
        subcategory="Audio",
        unit_cost=15.0,
        unit_price=35.0,
        lead_time_days=14,
        min_order_qty=25,
        demand_pattern="regular",
    )
    assert prod.lead_time_days == 14
    assert prod.min_order_qty == 25


@pytest.mark.unit
def test_valid_processed_time_series_record() -> None:
    """Verify ProcessedTimeSeriesRecord validates fully unified record."""
    row = ProcessedTimeSeriesRecord(
        date=date(2024, 6, 1),
        sku_id="SKU-1025",
        store_id="STORE-002",
        category="Apparel",
        subcategory="Footwear",
        quantity=8,
        price=89.99,
        unit_cost=45.00,
        is_promoted=False,
        inventory_level=50,
        units_on_order=100,
        backorders=0,
        lead_time_days=21,
        min_order_qty=50,
        demand_pattern="seasonal",
    )
    assert row.category == "Apparel"
    assert row.inventory_level == 50
