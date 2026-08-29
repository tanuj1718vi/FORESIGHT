"""001_initial_schema

Revision ID: 001_initial
Revises: None
Create Date: 2026-08-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Products Table
    op.create_table(
        "products",
        sa.Column("sku_id", sa.String(50), primary_key=True, index=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False, index=True),
        sa.Column("subcategory", sa.String(100), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
        sa.Column("min_order_qty", sa.Integer(), default=1),
        sa.Column("demand_pattern", sa.String(50), default="regular"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 2. Sales Records Table
    op.create_table(
        "sales_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku_id", sa.String(50), sa.ForeignKey("products.sku_id"), nullable=False, index=True),
        sa.Column("store_id", sa.String(50), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("is_promoted", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. Inventory Records Table
    op.create_table(
        "inventory_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku_id", sa.String(50), sa.ForeignKey("products.sku_id"), nullable=False, index=True),
        sa.Column("store_id", sa.String(50), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("inventory_level", sa.Integer(), nullable=False),
        sa.Column("units_on_order", sa.Integer(), default=0),
        sa.Column("backorders", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. Forecast Records Table
    op.create_table(
        "forecast_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku_id", sa.String(50), sa.ForeignKey("products.sku_id"), nullable=False, index=True),
        sa.Column("store_id", sa.String(50), nullable=False, index=True),
        sa.Column("forecast_date", sa.Date(), nullable=False, index=True),
        sa.Column("prediction_date", sa.Date(), nullable=False, index=True),
        sa.Column("predicted_demand", sa.Float(), nullable=False),
        sa.Column("p10_lower_bound", sa.Float(), nullable=True),
        sa.Column("p90_upper_bound", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(100), default="XGBoost"),
        sa.Column("model_version", sa.String(50), default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 5. Risk Assessment Records Table
    op.create_table(
        "risk_assessment_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku_id", sa.String(50), sa.ForeignKey("products.sku_id"), nullable=False, index=True),
        sa.Column("store_id", sa.String(50), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("composite_risk_score", sa.Float(), nullable=False),
        sa.Column("stockout_probability", sa.Float(), nullable=False),
        sa.Column("lost_revenue_risk", sa.Float(), nullable=False),
        sa.Column("lost_margin_risk", sa.Float(), nullable=False),
        sa.Column("excess_holding_cost_risk", sa.Float(), nullable=False),
        sa.Column("total_financial_exposure", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(50), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 6. Recommendation Records Table
    op.create_table(
        "recommendation_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("recommendation_id", sa.String(50), unique=True, index=True),
        sa.Column("sku_id", sa.String(50), sa.ForeignKey("products.sku_id"), nullable=False, index=True),
        sa.Column("store_id", sa.String(50), nullable=False, index=True),
        sa.Column("donor_store_id", sa.String(50), nullable=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("action", sa.String(50), nullable=False, index=True),
        sa.Column("recommended_quantity", sa.Float(), nullable=False),
        sa.Column("urgency", sa.String(50), nullable=False, index=True),
        sa.Column("expected_financial_impact", sa.Float(), default=0.0),
        sa.Column("confidence_score", sa.Float(), default=1.0),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 7. Model Runs Table
    op.create_table(
        "model_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(100), unique=True, index=True),
        sa.Column("model_name", sa.String(100), nullable=False, index=True),
        sa.Column("model_version", sa.String(50), default="1.0.0"),
        sa.Column("training_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dataset_version", sa.String(100), default="v1.0"),
        sa.Column("metrics_json", sa.Text(), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=False),
        sa.Column("artifact_path", sa.String(500), nullable=True),
        sa.Column("is_champion", sa.Boolean(), default=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("model_runs")
    op.drop_table("recommendation_records")
    op.drop_table("risk_assessment_records")
    op.drop_table("forecast_records")
    op.drop_table("inventory_records")
    op.drop_table("sales_records")
    op.drop_table("products")
