"""Unit tests for database models, repositories, and transactional session scopes."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from foresight.database.base import Base
from foresight.database.models import (
    ForecastRecord,
    InventoryRecord,
    ModelRun,
    Product,
    RecommendationRecord,
    RiskAssessmentRecord,
    SalesRecord,
)
from foresight.database.repositories import (
    ForecastRepository,
    InventoryRepository,
    ModelRepository,
    ProductRepository,
    RecommendationRepository,
    RiskRepository,
    SalesRepository,
)


@pytest.fixture
def in_memory_db() -> Session:
    """Fixture providing an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


@pytest.mark.unit
def test_product_repository_crud(in_memory_db: Session) -> None:
    """Verify product CRUD operations and category filters."""
    repo = ProductRepository(in_memory_db)

    p1 = Product(
        sku_id="SKU-TEST-1",
        product_name="Test Widget",
        category="Electronics",
        subcategory="Gadgets",
        unit_cost=10.0,
        unit_price=25.0,
        lead_time_days=7,
        min_order_qty=5,
    )
    repo.add(p1)
    in_memory_db.commit()

    assert repo.count() == 1
    fetched = repo.get_by_sku("SKU-TEST-1")
    assert fetched is not None
    assert fetched.product_name == "Test Widget"
    assert fetched.category == "Electronics"

    cat_prods = repo.list_by_category("Electronics")
    assert len(cat_prods) == 1


@pytest.mark.unit
def test_risk_and_recommendation_repositories(in_memory_db: Session) -> None:
    """Verify risk assessment and prescriptive recommendation repositories."""
    from datetime import date

    # Add product first for FK constraint
    p = Product(
        sku_id="SKU-100",
        product_name="Sample Item",
        category="Apparel",
        subcategory="Tops",
        unit_cost=15.0,
        unit_price=35.0,
        lead_time_days=5,
    )
    in_memory_db.add(p)
    in_memory_db.commit()

    risk_repo = RiskRepository(in_memory_db)
    rec_repo = RecommendationRepository(in_memory_db)

    risk = RiskAssessmentRecord(
        sku_id="SKU-100",
        store_id="STORE-1",
        date=date(2024, 1, 1),
        composite_risk_score=75.0,
        stockout_probability=0.35,
        lost_revenue_risk=500.0,
        lost_margin_risk=250.0,
        excess_holding_cost_risk=0.0,
        total_financial_exposure=250.0,
        risk_level="HIGH",
    )
    risk_repo.add(risk)

    rec = RecommendationRecord(
        recommendation_id="REC-TEST-1",
        sku_id="SKU-100",
        store_id="STORE-1",
        date=date(2024, 1, 1),
        action="ORDER",
        recommended_quantity=50.0,
        urgency="HIGH",
        expected_financial_impact=250.0,
        confidence_score=0.95,
        justification="Reorder point breached",
    )
    rec_repo.add(rec)
    in_memory_db.commit()

    latest_risk = risk_repo.get_latest_assessment("SKU-100", "STORE-1")
    assert latest_risk is not None
    assert latest_risk.composite_risk_score == 75.0

    order_recs = rec_repo.list_by_action("ORDER")
    assert len(order_recs) == 1
    assert order_recs[0].recommended_quantity == 50.0
