"""Database seeder populating SQLite database with enterprise benchmark datasets."""

from datetime import datetime
import json
from pathlib import Path
import pandas as pd

from foresight.config.constants import MODELS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR
from foresight.database.models import (
    ForecastRecord,
    InventoryRecord,
    ModelRun,
    Product,
    RecommendationRecord,
    RiskAssessmentRecord,
    SalesRecord,
)
from foresight.database.session import init_db, session_scope
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def seed_database(
    raw_dir: Path | str = RAW_DATA_DIR,
    processed_dir: Path | str = PROCESSED_DATA_DIR,
    models_dir: Path | str = MODELS_DIR,
) -> dict[str, int]:
    """Populate database tables from filesystem data artifacts."""
    init_db()
    r_dir = Path(raw_dir)
    p_dir = Path(processed_dir)
    m_dir = Path(models_dir)

    counts = {
        "products": 0,
        "sales": 0,
        "inventory": 0,
        "risk_assessments": 0,
        "recommendations": 0,
        "model_runs": 0,
    }

    with session_scope() as session:
        # 1. Seed Products
        prod_path = r_dir / "products_raw.csv"
        if prod_path.exists():
            df_prod = pd.read_csv(prod_path)
            for _, r in df_prod.iterrows():
                sku = str(r["sku_id"])
                if not session.get(Product, sku):
                    p = Product(
                        sku_id=sku,
                        product_name=str(r.get("product_name", f"Product {sku}")),
                        category=str(r.get("category", "General")),
                        subcategory=str(r.get("subcategory", "Standard")),
                        unit_cost=float(r.get("unit_cost", 10.0)),
                        unit_price=float(r.get("unit_price", 20.0)),
                        lead_time_days=int(r.get("lead_time_days", 7)),
                        min_order_qty=int(r.get("min_order_qty", 1)),
                        demand_pattern=str(r.get("demand_pattern", "regular")),
                    )
                    session.add(p)
                    counts["products"] += 1
            session.flush()
            logger.info(f"Seeded {counts['products']} Products.")

        # 2. Seed Risk Assessments
        risk_path = p_dir / "risk_assessments.parquet"
        if risk_path.exists():
            # Clear existing risk assessments if re-seeding
            session.query(RiskAssessmentRecord).delete()
            df_risk = pd.read_parquet(risk_path)
            for _, r in df_risk.iterrows():
                rec = RiskAssessmentRecord(
                    sku_id=str(r["sku_id"]),
                    store_id=str(r["store_id"]),
                    date=pd.to_datetime(r.get("date", datetime.now())).date(),
                    composite_risk_score=float(r.get("composite_risk_score", 0.0)),
                    stockout_probability=float(r.get("stockout_probability", 0.0)),
                    lost_revenue_risk=float(r.get("lost_revenue_risk", 0.0)),
                    lost_margin_risk=float(r.get("lost_margin_risk", 0.0)),
                    excess_holding_cost_risk=float(r.get("excess_holding_cost_risk", 0.0)),
                    total_financial_exposure=float(r.get("total_financial_exposure", 0.0)),
                    risk_level=str(r.get("risk_level", "LOW")),
                )
                session.add(rec)
                counts["risk_assessments"] += 1
            session.flush()
            logger.info(f"Seeded {counts['risk_assessments']} Risk Assessments.")

        # 3. Seed Prescriptive Recommendations
        rec_path = p_dir / "prescriptive_recommendations.parquet"
        if rec_path.exists():
            # Clear existing recommendations if re-seeding
            session.query(RecommendationRecord).delete()
            df_rec = pd.read_parquet(rec_path)
            seen_ids = set()
            for idx, r in df_rec.iterrows():
                rec_id = str(r.get("recommendation_id", f"REC-{r['sku_id']}-{r['store_id']}"))
                if rec_id in seen_ids:
                    rec_id = f"{rec_id}-{idx}"
                seen_ids.add(rec_id)

                rec = RecommendationRecord(
                    recommendation_id=rec_id,
                    sku_id=str(r["sku_id"]),
                    store_id=str(r["store_id"]),
                    donor_store_id=str(r["donor_store_id"]) if pd.notnull(r.get("donor_store_id")) else None,
                    date=pd.to_datetime(r.get("date", datetime.now())).date(),
                    action=str(r.get("action", "MONITOR")),
                    recommended_quantity=float(r.get("recommended_quantity", 0.0)),
                    urgency=str(r.get("urgency", "LOW")),
                    expected_financial_impact=float(r.get("expected_financial_impact", 0.0)),
                    confidence_score=float(r.get("confidence_score", 1.0)),
                    justification=str(r.get("justification", "")),
                )
                session.add(rec)
                counts["recommendations"] += 1
            session.flush()
            logger.info(f"Seeded {counts['recommendations']} Recommendations.")

        # 4. Seed Champion Model Run
        champ_meta_path = m_dir / "champion_metadata.json"
        if champ_meta_path.exists():
            with open(champ_meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            run_id = meta.get("run_id", "champion-xgboost-v1")
            existing_run = session.query(ModelRun).filter_by(run_id=run_id).first()
            if not existing_run:
                run = ModelRun(
                    run_id=run_id,
                    model_name=meta.get("champion_model_name", "XGBoost"),
                    model_version="1.0.0",
                    training_timestamp=datetime.now(),
                    dataset_version=meta.get("dataset_version", "sales_v1.0"),
                    metrics_json=json.dumps(meta.get("metrics", {})),
                    parameters_json=json.dumps(meta.get("parameters", {})),
                    artifact_path=str(m_dir / "champion_forecaster.pkl"),
                    is_champion=True,
                )
                session.add(run)
                counts["model_runs"] += 1
                session.flush()
                logger.info(f"Seeded {counts['model_runs']} Model Run records.")

    return counts


if __name__ == "__main__":
    seed_database()
