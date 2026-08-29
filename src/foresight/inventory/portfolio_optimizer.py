"""Portfolio-wide batch inventory optimization and working capital intelligence report generator."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any
import pandas as pd
from pydantic import BaseModel, Field

from foresight.config.constants import PROCESSED_DATA_DIR, REPORTS_DIR
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import (
    InventoryHealthStatus,
    InventoryOptimizationResult,
    InventoryParameters,
    OrderAction,
    SafetyStockMethod,
)
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioOptimizationReport(BaseModel):
    """Enterprise-wide inventory optimization and working capital report."""
    audit_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_sku_store_nodes: int
    target_service_level: float
    total_working_capital_committed: float
    total_recommended_order_units: float
    total_annual_holding_cost: float
    total_annual_ordering_cost: float
    total_annual_inventory_cost: float
    health_distribution: dict[str, int]
    action_distribution: dict[str, int]
    top_urgent_reorders: list[dict[str, Any]]
    top_overstocked_skus: list[dict[str, Any]]

    def to_markdown(self) -> str:
        """Render report as a clean GitHub Flavored Markdown document."""
        lines = [
            "# FORESIGHT — Portfolio Inventory Optimization & Working Capital Audit",
            "",
            f"**Audit Timestamp:** `{self.audit_date}`  ",
            f"**Enterprise Portfolio Scope:** `{self.total_sku_store_nodes}` SKU-Store replenishment nodes  ",
            f"**Target Service Level:** `{self.target_service_level * 100:.1f}%`  ",
            "",
            "---",
            "",
            "## 1. Executive Financial Summary",
            "",
            f"| Metric | Portfolio Aggregate Value |",
            f"| :--- | :--- |",
            f"| **Total Working Capital Committed** | **${self.total_working_capital_committed:,.2f}** |",
            f"| **Total Units to Order Now** | **{self.total_recommended_order_units:,.0f} units** |",
            f"| **Annual Inventory Holding Cost** | **${self.total_annual_holding_cost:,.2f}/yr** |",
            f"| **Annual Purchase Ordering Cost** | **${self.total_annual_ordering_cost:,.2f}/yr** |",
            f"| **Total Annual Inventory Carrying Cost** | **${self.total_annual_inventory_cost:,.2f}/yr** |",
            "",
            "---",
            "",
            "## 2. Portfolio Health Breakdown",
            "",
            "| Health Position | Node Count | Percentage of Portfolio | Operational Implication |",
            "| :--- | :---: | :---: | :--- |",
        ]

        total = self.total_sku_store_nodes
        for status, count in self.health_distribution.items():
            pct = (count / total) * 100 if total > 0 else 0
            lines.append(f"| `{status}` | **{count}** | `{pct:.1f}%` | Active monitoring / Action |")

        lines.extend([
            "",
            "### 2.1 Prescriptive Action Summary",
            "",
            "| Prescriptive Action | Node Count | Operational Workflow |",
            "| :--- | :---: | :--- |",
        ])

        for action, count in self.action_distribution.items():
            lines.append(f"| **{action}** | **{count}** | Prescribed replenishment decision |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Priority Reorder Actions (Top Stockout Risks)",
            "",
            "| SKU ID | Store ID | Net Stock Position | Safety Stock | ROP | Rec. Order Qty | Days of Supply | Stockout Risk |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        ])

        for r in self.top_urgent_reorders[:10]:
            lines.append(
                f"| `{r['sku_id']}` | `{r['store_id']}` | {r['net_stock']:.0f} | {r['safety_stock']:.1f} | {r['reorder_point']:.1f} | **{r['recommended_order_quantity']:.0f}** | `{r['days_of_supply']:.1f}d` | **{r['stockout_risk_prob'] * 100:.1f}%** |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 4. Priority Capital Optimization (Top Excess Overstocks)",
            "",
            "| SKU ID | Store ID | Net Stock Position | Safety Stock | Days of Supply | Committed Capital | Prescribed Action |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for r in self.top_overstocked_skus[:10]:
            lines.append(
                f"| `{r['sku_id']}` | `{r['store_id']}` | {r['net_stock']:.0f} | {r['safety_stock']:.1f} | `{r['days_of_supply']:.1f}d` | **${r['working_capital_committed']:,.2f}** | **REDUCE / HOLD** |"
            )

        return "\n".join(lines)

    def save(self, json_path: Path | str, md_path: Path | str | None = None) -> None:
        """Save report to JSON and Markdown."""
        j_path = Path(json_path)
        j_path.parent.mkdir(parents=True, exist_ok=True)
        with open(j_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        logger.info(f"Saved inventory optimization report JSON to {j_path}")

        if md_path:
            m_path = Path(md_path)
            m_path.parent.mkdir(parents=True, exist_ok=True)
            with open(m_path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown())
            logger.info(f"Saved inventory optimization report Markdown to {m_path}")


def optimize_portfolio_inventory(
    features_path: Path | str | None = None,
    service_level: float = 0.95,
    method: SafetyStockMethod = SafetyStockMethod.COMBINED_UNCERTAINTY,
    output_dir: Path | str = PROCESSED_DATA_DIR,
    reports_dir: Path | str = REPORTS_DIR,
) -> tuple[pd.DataFrame, PortfolioOptimizationReport]:
    """Execute inventory optimization across all SKU-Store nodes in the enterprise portfolio."""
    f_path = Path(features_path or (PROCESSED_DATA_DIR / "features_engineered.parquet"))
    logger.info(f"Loading feature snapshot for inventory optimization from {f_path}...")
    df = pd.read_parquet(f_path)

    # Get latest observation per (sku_id, store_id)
    latest_snapshot = df.sort_values("date").groupby(["sku_id", "store_id"]).last().reset_index()
    logger.info(f"Extracted latest inventory snapshot for {len(latest_snapshot)} SKU-Store nodes.")

    optimizer = InventoryOptimizer(default_method=method)
    results: list[InventoryOptimizationResult] = []

    for _, row in latest_snapshot.iterrows():
        # Demand mean & std from rolling indicators
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
            target_service_level=service_level,
            forecast_daily_demand_mean=mean_d,
            forecast_daily_demand_std=std_d,
        )

        res = optimizer.optimize_sku(params, method=method)
        results.append(res)

    results_data = [r.model_dump() for r in results]
    results_df = pd.DataFrame(results_data)

    # Save recommendations table
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / "inventory_recommendations.parquet"
    csv_path = out_dir / "inventory_recommendations.csv"
    results_df.to_parquet(parquet_path, index=False)
    results_df.to_csv(csv_path, index=False)
    logger.info(f"Saved inventory recommendations to {parquet_path}")

    # Build summary report
    health_counts = results_df["health_status"].value_counts().to_dict()
    action_counts = results_df["recommended_action"].value_counts().to_dict()

    urgent_reorders = (
        results_df[results_df["recommended_action"].isin(["ORDER", "EXPEDITE"])]
        .sort_values("stockout_risk_prob", ascending=False)
        .head(15)
        .to_dict(orient="records")
    )

    overstocked = (
        results_df[results_df["health_status"].isin(["OVERSTOCKED", "CRITICAL_EXCESS"])]
        .sort_values("days_of_supply", ascending=False)
        .head(15)
        .to_dict(orient="records")
    )

    report = PortfolioOptimizationReport(
        total_sku_store_nodes=len(results_df),
        target_service_level=service_level,
        total_working_capital_committed=round(float(results_df["working_capital_committed"].sum()), 2),
        total_recommended_order_units=round(float(results_df["recommended_order_quantity"].sum()), 0),
        total_annual_holding_cost=round(float(results_df["annual_holding_cost"].sum()), 2),
        total_annual_ordering_cost=round(float(results_df["annual_ordering_cost"].sum()), 2),
        total_annual_inventory_cost=round(float(results_df["total_annual_inventory_cost"].sum()), 2),
        health_distribution={str(k): int(v) for k, v in health_counts.items()},
        action_distribution={str(k): int(v) for k, v in action_counts.items()},
        top_urgent_reorders=urgent_reorders,
        top_overstocked_skus=overstocked,
    )

    rep_dir = Path(reports_dir)
    rep_dir.mkdir(parents=True, exist_ok=True)
    report.save(
        json_path=rep_dir / "inventory_optimization_report.json",
        md_path=rep_dir / "inventory_optimization_report.md",
    )

    return results_df, report


if __name__ == "__main__":
    optimize_portfolio_inventory()
