"""Risk assessment audit runner, lateral transfer detector, and report generator."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any
import pandas as pd
from pydantic import BaseModel, Field

from foresight.config.constants import PROCESSED_DATA_DIR, REPORTS_DIR, RecommendationAction, RiskLevel
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryOptimizationResult, InventoryParameters
from foresight.risk.prescriptive import PrescriptiveEngine
from foresight.risk.schema import PrescriptiveRecommendation, RiskAssessment
from foresight.risk.scorer import assess_sku_risk
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioRiskReport(BaseModel):
    """Enterprise risk assessment and prescriptive recommendations report."""
    audit_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_sku_store_nodes: int
    total_lost_margin_exposure: float
    total_excess_holding_risk: float
    total_financial_exposure: float
    risk_level_distribution: dict[str, int]
    action_distribution: dict[str, int]
    lateral_rebalances_identified: int
    top_financial_risks: list[dict[str, Any]]
    prescriptive_action_plan: list[dict[str, Any]]

    def to_markdown(self) -> str:
        """Render risk audit report as clean GitHub Flavored Markdown."""
        lines = [
            "# FORESIGHT — Enterprise Inventory Risk & Prescriptive Decision Audit",
            "",
            f"**Audit Timestamp:** `{self.audit_date}`  ",
            f"**Portfolio Scope:** `{self.total_sku_store_nodes}` SKU-Store replenishment nodes  ",
            f"**Lateral Rebalances Identified:** `{self.lateral_rebalances_identified}` multi-store transfers  ",
            "",
            "---",
            "",
            "## 1. Financial Exposure & Capital at Risk",
            "",
            f"| Financial Risk Category | Exposure Amount ($) | Business Implication |",
            f"| :--- | :---: | :--- |",
            f"| **Lost Gross Margin Risk** | **${self.total_lost_margin_exposure:,.2f}** | Unmet customer demand from stockouts |",
            f"| **Excess Holding Cost Penalty** | **${self.total_excess_holding_risk:,.2f}/yr** | Capital tied up in stagnant/excess stock |",
            f"| **Total Financial Exposure** | **${self.total_financial_exposure:,.2f}** | Combined enterprise inventory vulnerability |",
            "",
            "---",
            "",
            "## 2. Risk Severity Tier Distribution",
            "",
            "| Risk Severity Level | Node Count | Percentage of Portfolio | Management Action |",
            "| :--- | :---: | :---: | :--- |",
        ]

        total = self.total_sku_store_nodes
        for level, count in self.risk_level_distribution.items():
            pct = (count / total) * 100 if total > 0 else 0
            lines.append(f"| `{level}` | **{count}** | `{pct:.1f}%` | Active SLA compliance & monitoring |")

        lines.extend([
            "",
            "### 2.1 Prescriptive Action Work Orders",
            "",
            "| Action Type | Order Count | Operational Directive |",
            "| :--- | :---: | :--- |",
        ])

        for action, count in self.action_distribution.items():
            lines.append(f"| **{action}** | **{count}** | Trigger automated ERP/WMS workflow |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Top 10 Critical Financial Risks",
            "",
            "| SKU ID | Store ID | Risk Level | Composite Score | Stockout Prob | Lost Margin Risk | Excess Holding Risk | Total Exposure |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        ])

        for r in self.top_financial_risks[:10]:
            lines.append(
                f"| `{r['sku_id']}` | `{r['store_id']}` | `{r['risk_level']}` | **{r['composite_risk_score']:.1f}** | `{r['stockout_probability'] * 100:.1f}%` | ${r['lost_margin_risk']:,.2f} | ${r['excess_holding_cost_risk']:,.2f} | **${r['total_financial_exposure']:,.2f}** |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 4. Priority Prescriptive Action Work Orders (Top Recommendations)",
            "",
            "| Rec ID | Action | SKU ID | Store ID | Quantity | Urgency | Expected Impact | Justification |",
            "| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |",
        ])

        for rec in self.prescriptive_action_plan[:10]:
            donor = rec.get("donor_store_id")
            donor_note = f" (Transfer from {donor})" if (donor and str(donor).lower() not in ["none", "nan", ""]) else ""
            lines.append(
                f"| `{rec['recommendation_id']}` | **{rec['action']}**{donor_note} | `{rec['sku_id']}` | `{rec['store_id']}` | **{rec['recommended_quantity']:.0f}** | `{rec['urgency']}` | ${rec['expected_financial_impact']:,.2f} | {rec['justification']} |"
            )

        return "\n".join(lines)

    def save(self, json_path: Path | str, md_path: Path | str | None = None) -> None:
        """Save risk audit report to JSON and Markdown."""
        j_path = Path(json_path)
        j_path.parent.mkdir(parents=True, exist_ok=True)
        with open(j_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        logger.info(f"Saved risk audit report JSON to {j_path}")

        if md_path:
            m_path = Path(md_path)
            m_path.parent.mkdir(parents=True, exist_ok=True)
            with open(m_path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown())
            logger.info(f"Saved risk audit report Markdown to {m_path}")


def run_portfolio_risk_audit(
    features_path: Path | str | None = None,
    output_dir: Path | str = PROCESSED_DATA_DIR,
    reports_dir: Path | str = REPORTS_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, PortfolioRiskReport]:
    """Execute risk quantification and prescriptive action synthesis across all 250 portfolio nodes."""
    f_path = Path(features_path or (PROCESSED_DATA_DIR / "features_engineered.parquet"))
    logger.info(f"Loading features from {f_path} for risk audit...")
    df = pd.read_parquet(f_path)

    latest_snapshot = df.sort_values("date").groupby(["sku_id", "store_id"]).last().reset_index()

    optimizer = InventoryOptimizer()
    prescriptive_engine = PrescriptiveEngine()

    opt_results: list[InventoryOptimizationResult] = []
    risk_results: list[RiskAssessment] = []
    base_recs: list[PrescriptiveRecommendation] = []
    all_params: list[InventoryParameters] = []

    for _, row in latest_snapshot.iterrows():
        mean_d = float(row.get("rolling_mean_7", row.get("quantity", 10.0)))
        std_d = float(row.get("rolling_std_7", max(1.0, mean_d * 0.25)))
        lead_time = float(row.get("lead_time_days", 7.0))
        unit_cost = float(row.get("unit_cost", 20.0))
        unit_price = float(row.get("unit_price", 35.0))
        on_hand = float(row.get("inventory_level", 50.0))
        on_order = float(row.get("units_on_order", 0.0))
        backorders = float(row.get("backorders", 0.0))
        moq = float(row.get("min_order_qty", 1.0))
        holding_rate = float(row.get("holding_cost_annual_rate", 0.20))

        params = InventoryParameters(
            sku_id=str(row["sku_id"]),
            store_id=str(row["store_id"]),
            current_on_hand=on_hand,
            units_on_order=on_order,
            backorders=backorders,
            unit_cost=unit_cost,
            unit_price=unit_price,
            lead_time_days=lead_time,
            lead_time_std_days=max(0.5, lead_time * 0.15),
            holding_cost_annual_rate=holding_rate,
            fixed_order_cost=50.0,
            min_order_qty=moq,
            target_service_level=0.95,
            forecast_daily_demand_mean=mean_d,
            forecast_daily_demand_std=std_d,
        )
        all_params.append(params)

        opt_res = optimizer.optimize_sku(params)
        opt_results.append(opt_res)

        risk_res = assess_sku_risk(opt_res, params)
        risk_results.append(risk_res)

        rec = prescriptive_engine.generate_recommendation(opt_res, risk_res, params)
        base_recs.append(rec)

    # Lateral Rebalancing Detection
    lateral_recs = prescriptive_engine.identify_lateral_rebalance_opportunities(
        recommendations=base_recs,
        inventory_results=opt_results,
    )
    final_recs = lateral_recs + base_recs

    # DataFrames
    risk_df = pd.DataFrame([r.model_dump() for r in risk_results])
    recs_df = pd.DataFrame([r.model_dump() for r in final_recs])

    # Save to disk
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    risk_df.to_parquet(out_dir / "risk_assessments.parquet", index=False)
    risk_df.to_csv(out_dir / "risk_assessments.csv", index=False)
    recs_df.to_parquet(out_dir / "prescriptive_recommendations.parquet", index=False)
    recs_df.to_csv(out_dir / "prescriptive_recommendations.csv", index=False)

    # Compile report
    risk_counts = risk_df["risk_level"].value_counts().to_dict()
    action_counts = recs_df["action"].value_counts().to_dict()

    top_risks = risk_df.sort_values("total_financial_exposure", ascending=False).head(15).to_dict(orient="records")
    top_recs = recs_df.sort_values("expected_financial_impact", ascending=False).head(20).to_dict(orient="records")

    report = PortfolioRiskReport(
        total_sku_store_nodes=len(risk_df),
        total_lost_margin_exposure=round(float(risk_df["lost_margin_risk"].sum()), 2),
        total_excess_holding_risk=round(float(risk_df["excess_holding_cost_risk"].sum()), 2),
        total_financial_exposure=round(float(risk_df["total_financial_exposure"].sum()), 2),
        risk_level_distribution={str(k): int(v) for k, v in risk_counts.items()},
        action_distribution={str(k): int(v) for k, v in action_counts.items()},
        lateral_rebalances_identified=len(lateral_recs),
        top_financial_risks=top_risks,
        prescriptive_action_plan=top_recs,
    )

    rep_dir = Path(reports_dir)
    rep_dir.mkdir(parents=True, exist_ok=True)
    report.save(
        json_path=rep_dir / "risk_assessment_report.json",
        md_path=rep_dir / "risk_assessment_report.md",
    )

    return risk_df, recs_df, report


if __name__ == "__main__":
    run_portfolio_risk_audit()
