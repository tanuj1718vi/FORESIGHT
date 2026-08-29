"""Exploratory Data Analysis (EDA) and Intelligence Engine for Project FORESIGHT."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field

from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class DemandProfile(BaseModel):
    """Statistical summary of aggregate demand patterns."""
    total_sales_units: int
    total_revenue: float
    mean_daily_sales: float
    median_daily_sales: float
    std_daily_sales: float
    min_daily_sales: int
    max_daily_sales: int
    skewness: float
    kurtosis: float
    weekday_seasonality_indices: dict[str, float]  # Day -> Normalized Index (1.0 = Average)
    monthly_seasonality_indices: dict[str, float]  # Month -> Normalized Index
    promotional_demand_lift: float  # Multiplier: Promo Demand / Non-Promo Demand
    annualized_trend_growth_pct: float  # Linear regression annualized slope percentage


class SKUPerformanceItem(BaseModel):
    """Detailed commercial performance and volatility metrics for a single SKU."""
    sku_id: str
    product_name: str
    category: str
    total_units_sold: int
    total_revenue: float
    revenue_share_pct: float
    cumulative_revenue_pct: float
    mean_daily_demand: float
    std_daily_demand: float
    coefficient_of_variation: float
    abc_class: str  # A, B, C
    xyz_class: str  # X, Y, Z
    abc_xyz_segment: str  # e.g., AX, BY, CZ
    demand_pattern: str


class ABCXYZSegmentation(BaseModel):
    """Catalog-wide ABC/XYZ portfolio classification summary."""
    total_skus: int
    segment_counts: dict[str, int]
    top_revenue_skus: list[str]
    bottom_revenue_skus: list[str]
    most_volatile_skus: list[str]
    intermittent_skus: list[str]
    sku_details: list[SKUPerformanceItem]


class InventoryHealthProfile(BaseModel):
    """Enterprise inventory dynamics, stockout risk, and capital efficiency metrics."""
    total_cogs: float
    average_inventory_units: float
    average_inventory_value: float
    total_backordered_units: int
    stockout_incident_days: int
    stockout_rate_pct: float
    overall_days_of_supply: float
    annualized_inventory_turnover: float
    inventory_turnover_days: float


class EDASummaryReport(BaseModel):
    """Unified comprehensive EDA analytics report."""
    dataset_name: str
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    date_range_start: str
    date_range_end: str
    total_days: int
    total_records: int
    demand_profile: DemandProfile
    segmentation: ABCXYZSegmentation
    inventory_health: InventoryHealthProfile

    def to_markdown(self) -> str:
        """Generate executive-grade Markdown summary of EDA findings."""
        dp = self.demand_profile
        seg = self.segmentation
        ih = self.inventory_health

        lines = [
            f"# FORESIGHT — Exploratory Data Analysis & Business Intelligence",
            f"",
            f"**Dataset:** `{self.dataset_name}`  ",
            f"**Observation Period:** `{self.date_range_start}` to `{self.date_range_end}` ({self.total_days} days)  ",
            f"**Total Records:** `{self.total_records:,}` | **Generated:** `{self.generated_at}`",
            f"",
            f"---",
            f"",
            f"## 1. Executive Key Performance Indicators",
            f"",
            f"| Metric | Value | Interpretation |",
            f"| :--- | :--- | :--- |",
            f"| **Total Sales Volume** | `{dp.total_sales_units:,} units` | Total fulfilled retail demand |",
            f"| **Total Gross Revenue** | `${dp.total_revenue:,.2f}` | Cumulative sales proceeds |",
            f"| **Mean Daily Demand** | `{dp.mean_daily_sales:.1f} units/day` | Aggregate network daily velocity |",
            f"| **Promotional Lift** | `{dp.promotional_demand_lift:.2f}x` | Average demand surge during active markdown/promo |",
            f"| **Annual Market Trend** | `{dp.annualized_trend_growth_pct:+.1f}%/yr` | Underling structural market growth rate |",
            f"| **Average Working Inventory Value** | `${ih.average_inventory_value:,.2f}` | Tied-up working capital in physical stock |",
            f"| **Stockout Rate** | `{ih.stockout_rate_pct:.2f}%` | Percentage of SKU-store days experiencing stock depletion |",
            f"| **Total Backorders** | `{ih.total_backordered_units:,} units` | Unfulfilled customer demand lost/backordered |",
            f"| **Inventory Turnover Ratio** | `{ih.annualized_inventory_turnover:.2f}x / yr` | Velocity of inventory replenishment cycle |",
            f"| **Average Days of Supply (DOS)** | `{ih.overall_days_of_supply:.1f} days` | Projected coverage buffer at current demand rate |",
            f"",
            f"---",
            f"",
            f"## 2. Demand Seasonality & Cyclicality",
            f"",
            f"### Day-of-Week Seasonality Index (1.0 = Average Day)",
            f"",
            f"| Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |",
            f"| :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
            f"| {dp.weekday_seasonality_indices.get('Monday', 1.0):.2f} | {dp.weekday_seasonality_indices.get('Tuesday', 1.0):.2f} | {dp.weekday_seasonality_indices.get('Wednesday', 1.0):.2f} | {dp.weekday_seasonality_indices.get('Thursday', 1.0):.2f} | {dp.weekday_seasonality_indices.get('Friday', 1.0):.2f} | **{dp.weekday_seasonality_indices.get('Saturday', 1.0):.2f}** | **{dp.weekday_seasonality_indices.get('Sunday', 1.0):.2f}** |",
            f"",
            f"---",
            f"",
            f"## 3. ABC / XYZ Portfolio Segmentation Matrix",
            f"",
            f"The catalog of **{seg.total_skus} SKUs** is segmented by revenue contribution (ABC) and demand variability (XYZ):",
            f"",
            f"| Segment Breakdown | Count | SKU Share | Strategy Profile |",
            f"| :--- | :--- | :--- | :--- |",
        ]

        for seg_key, count in sorted(seg.segment_counts.items()):
            share = (count / seg.total_skus) * 100
            strategy = "High Value, Low Volatility (Automated Replenish)" if "AX" in seg_key else (
                "High Value, High Volatility (Safety Buffer & ML Forecast)" if "AZ" in seg_key else (
                    "Low Value, Intermittent (Order-on-demand / Low Stock)" if "CZ" in seg_key else "Standard Dynamic ROP"
                )
            )
            lines.append(f"| **{seg_key}** | `{count}` | `{share:.1f}%` | {strategy} |")

        lines.extend([
            f"",
            f"### Top Revenue Driving SKUs (Pareto Class A)",
            f"- {', '.join(seg.top_revenue_skus[:5])}",
            f"",
            f"### High Volatility / Intermittent SKUs (Class Z)",
            f"- {', '.join(seg.most_volatile_skus[:5])}",
            f"",
        ])

        return "\n".join(lines)

    def save(self, json_path: Path | str, md_path: Path | str | None = None) -> None:
        """Save report to JSON and Markdown destinations."""
        j_path = Path(json_path)
        j_path.parent.mkdir(parents=True, exist_ok=True)
        with open(j_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        logger.info(f"Saved EDA summary JSON to {j_path}")

        if md_path:
            m_path = Path(md_path)
            m_path.parent.mkdir(parents=True, exist_ok=True)
            with open(m_path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown())
            logger.info(f"Saved EDA summary Markdown to {m_path}")


class EDAEngine:
    """Core analytics engine for statistical demand exploration and SKU intelligence."""

    def __init__(
        self,
        date_col: str = "date",
        sku_col: str = "sku_id",
        store_col: str = "store_id",
        quantity_col: str = "quantity",
        price_col: str = "price",
        unit_cost_col: str = "unit_cost",
        inventory_col: str = "inventory_level",
        backorder_col: str = "backorders",
        category_col: str = "category",
        promo_col: str = "is_promoted",
    ) -> None:
        self.date_col = date_col
        self.sku_col = sku_col
        self.store_col = store_col
        self.quantity_col = quantity_col
        self.price_col = price_col
        self.unit_cost_col = unit_cost_col
        self.inventory_col = inventory_col
        self.backorder_col = backorder_col
        self.category_col = category_col
        self.promo_col = promo_col

    def compute_demand_profile(self, df: pd.DataFrame) -> DemandProfile:
        """Compute aggregate statistical properties of demand distribution."""
        data = df.copy()
        data[self.date_col] = pd.to_datetime(data[self.date_col])

        # Revenue
        if self.price_col in data.columns:
            data["revenue"] = data[self.quantity_col] * data[self.price_col]
        else:
            data["revenue"] = data[self.quantity_col]

        total_sales_units = int(data[self.quantity_col].sum())
        total_revenue = float(data["revenue"].sum())

        # Daily aggregate series
        daily_agg = data.groupby(self.date_col)[self.quantity_col].sum()
        mean_daily = float(daily_agg.mean())
        median_daily = float(daily_agg.median())
        std_daily = float(daily_agg.std())
        min_daily = int(daily_agg.min())
        max_daily = int(daily_agg.max())
        skewness = float(daily_agg.skew())
        kurtosis = float(daily_agg.kurt())

        # Weekday Seasonality
        data["day_of_week_num"] = data[self.date_col].dt.dayofweek
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_means = data.groupby("day_of_week_num")[self.quantity_col].mean()
        overall_mean = data[self.quantity_col].mean()
        weekday_indices = {
            day_names[i]: round(float(weekday_means.get(i, overall_mean) / (overall_mean if overall_mean > 0 else 1.0)), 3)
            for i in range(7)
        }

        # Monthly Seasonality
        data["month_name"] = data[self.date_col].dt.strftime("%B")
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        monthly_means = data.groupby("month_name")[self.quantity_col].mean()
        monthly_indices = {
            m: round(float(monthly_means.get(m, overall_mean) / (overall_mean if overall_mean > 0 else 1.0)), 3)
            for m in month_order if m in monthly_means
        }

        # Promotional Lift
        if self.promo_col in data.columns and data[self.promo_col].nunique() > 1:
            promo_mean = data[data[self.promo_col] == True][self.quantity_col].mean()
            non_promo_mean = data[data[self.promo_col] == False][self.quantity_col].mean()
            promo_lift = round(float(promo_mean / non_promo_mean), 3) if non_promo_mean > 0 else 1.0
        else:
            promo_lift = 1.0

        # Annualized Market Trend (OLS on daily total volume)
        days_axis = np.arange(len(daily_agg))
        if len(days_axis) > 1:
            slope, intercept = np.polyfit(days_axis, daily_agg.values, deg=1)
            annual_growth_pct = round(float((slope * 365.0) / (intercept if intercept > 0 else mean_daily) * 100.0), 2)
        else:
            annual_growth_pct = 0.0

        return DemandProfile(
            total_sales_units=total_sales_units,
            total_revenue=round(total_revenue, 2),
            mean_daily_sales=round(mean_daily, 2),
            median_daily_sales=round(median_daily, 2),
            std_daily_sales=round(std_daily, 2),
            min_daily_sales=min_daily,
            max_daily_sales=max_daily,
            skewness=round(skewness, 3),
            kurtosis=round(kurtosis, 3),
            weekday_seasonality_indices=weekday_indices,
            monthly_seasonality_indices=monthly_indices,
            promotional_demand_lift=promo_lift,
            annualized_trend_growth_pct=annual_growth_pct,
        )

    def compute_sku_segmentation(self, df: pd.DataFrame) -> ABCXYZSegmentation:
        """Perform Pareto ABC and Volatility XYZ classification for all SKUs."""
        data = df.copy()
        if self.price_col in data.columns:
            data["revenue"] = data[self.quantity_col] * data[self.price_col]
        else:
            data["revenue"] = data[self.quantity_col]

        sku_grp = data.groupby(self.sku_col)
        sku_stats = sku_grp.agg(
            total_units=(self.quantity_col, "sum"),
            total_revenue=("revenue", "sum"),
            mean_daily_demand=(self.quantity_col, "mean"),
            std_daily_demand=(self.quantity_col, "std"),
            category=(self.category_col, "first") if self.category_col in data.columns else (self.sku_col, "first"),
            product_name=("product_name", "first") if "product_name" in data.columns else (self.sku_col, "first"),
            demand_pattern=("demand_pattern", "first") if "demand_pattern" in data.columns else (self.sku_col, lambda _: "regular"),
        ).reset_index()

        # Sort by revenue descending for ABC analysis
        sku_stats = sku_stats.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
        total_catalog_revenue = sku_stats["total_revenue"].sum()

        sku_stats["revenue_share_pct"] = (sku_stats["total_revenue"] / total_catalog_revenue * 100).round(3)
        sku_stats["cumulative_revenue_pct"] = (sku_stats["total_revenue"].cumsum() / total_catalog_revenue * 100).round(3)

        # ABC Classification (A <= 80%, B 80%-95%, C > 95%)
        def assign_abc(cum_pct: float) -> str:
            if cum_pct <= 80.0:
                return "A"
            elif cum_pct <= 95.0:
                return "B"
            else:
                return "C"

        sku_stats["abc_class"] = sku_stats["cumulative_revenue_pct"].apply(assign_abc)

        # Coefficient of Variation = std / mean
        sku_stats["std_daily_demand"] = sku_stats["std_daily_demand"].fillna(0.0)
        sku_stats["coefficient_of_variation"] = np.where(
            sku_stats["mean_daily_demand"] > 0,
            sku_stats["std_daily_demand"] / sku_stats["mean_daily_demand"],
            0.0,
        ).round(3)

        # XYZ Classification (X < 0.35, Y 0.35 - 0.70, Z >= 0.70)
        def assign_xyz(cv: float) -> str:
            if cv < 0.35:
                return "X"
            elif cv < 0.70:
                return "Y"
            else:
                return "Z"

        sku_stats["xyz_class"] = sku_stats["coefficient_of_variation"].apply(assign_xyz)
        sku_stats["abc_xyz_segment"] = sku_stats["abc_class"] + sku_stats["xyz_class"]

        segment_counts = sku_stats["abc_xyz_segment"].value_counts().to_dict()

        items: list[SKUPerformanceItem] = []
        for _, row in sku_stats.iterrows():
            items.append(
                SKUPerformanceItem(
                    sku_id=str(row[self.sku_col]),
                    product_name=str(row["product_name"]),
                    category=str(row["category"]),
                    total_units_sold=int(row["total_units"]),
                    total_revenue=round(float(row["total_revenue"]), 2),
                    revenue_share_pct=float(row["revenue_share_pct"]),
                    cumulative_revenue_pct=float(row["cumulative_revenue_pct"]),
                    mean_daily_demand=round(float(row["mean_daily_demand"]), 2),
                    std_daily_demand=round(float(row["std_daily_demand"]), 2),
                    coefficient_of_variation=float(row["coefficient_of_variation"]),
                    abc_class=str(row["abc_class"]),
                    xyz_class=str(row["xyz_class"]),
                    abc_xyz_segment=str(row["abc_xyz_segment"]),
                    demand_pattern=str(row["demand_pattern"]),
                )
            )

        top_skus = sku_stats.head(5)[self.sku_col].tolist()
        bottom_skus = sku_stats.tail(5)[self.sku_col].tolist()
        volatile_skus = sku_stats.sort_values(by="coefficient_of_variation", ascending=False).head(5)[self.sku_col].tolist()
        intermittent_skus = sku_stats[sku_stats["demand_pattern"] == "intermittent"][self.sku_col].tolist()

        return ABCXYZSegmentation(
            total_skus=len(sku_stats),
            segment_counts=segment_counts,
            top_revenue_skus=top_skus,
            bottom_revenue_skus=bottom_skus,
            most_volatile_skus=volatile_skus,
            intermittent_skus=intermittent_skus,
            sku_details=items,
        )

    def compute_inventory_health(self, df: pd.DataFrame) -> InventoryHealthProfile:
        """Compute network-wide inventory positions, stockout severity, and turnover ratios."""
        data = df.copy()
        data[self.date_col] = pd.to_datetime(data[self.date_col])

        # COGS calculation
        if self.unit_cost_col in data.columns:
            data["cogs"] = data[self.quantity_col] * data[self.unit_cost_col]
            data["inv_value"] = data[self.inventory_col] * data[self.unit_cost_col]
        else:
            data["cogs"] = data[self.quantity_col] * 10.0
            data["inv_value"] = data[self.inventory_col] * 10.0

        total_cogs = float(data["cogs"].sum())
        total_days = max(1, (data[self.date_col].max() - data[self.date_col].min()).days + 1)
        annual_factor = 365.0 / total_days
        annualized_cogs = total_cogs * annual_factor

        # Daily network-level aggregated inventory and sales
        daily_network_inv = data.groupby(self.date_col)["inv_value"].sum()
        daily_network_units = data.groupby(self.date_col)[self.inventory_col].sum()
        daily_network_cogs = data.groupby(self.date_col)["cogs"].sum()

        avg_inventory_units = float(daily_network_units.mean())
        avg_inventory_val = float(daily_network_inv.mean())
        avg_daily_cogs = float(daily_network_cogs.mean())

        total_backorders = int(data[self.backorder_col].sum()) if self.backorder_col in data.columns else 0

        # Stockout days: when inventory was 0 or backorders occurred
        if self.backorder_col in data.columns:
            stockout_mask = (data[self.inventory_col] == 0) & ((data[self.quantity_col] > 0) | (data[self.backorder_col] > 0))
        else:
            stockout_mask = (data[self.inventory_col] == 0) & (data[self.quantity_col] > 0)

        stockout_incident_days = int(stockout_mask.sum())
        total_records = len(data)
        stockout_rate_pct = round((stockout_incident_days / total_records * 100) if total_records > 0 else 0.0, 3)

        days_of_supply = round(avg_inventory_val / avg_daily_cogs, 1) if avg_daily_cogs > 0 else 0.0
        turnover = round(annualized_cogs / avg_inventory_val, 2) if avg_inventory_val > 0 else 0.0
        turnover_days = round(365.0 / turnover, 1) if turnover > 0 else 0.0

        return InventoryHealthProfile(
            total_cogs=round(total_cogs, 2),
            average_inventory_units=round(avg_inventory_units, 1),
            average_inventory_value=round(avg_inventory_val, 2),
            total_backordered_units=total_backorders,
            stockout_incident_days=stockout_incident_days,
            stockout_rate_pct=stockout_rate_pct,
            overall_days_of_supply=days_of_supply,
            annualized_inventory_turnover=turnover,
            inventory_turnover_days=turnover_days,
        )

    def generate_full_report(self, df: pd.DataFrame, dataset_name: str = "sales_processed") -> EDASummaryReport:
        """Run all analytics modules and assemble unified EDASummaryReport."""
        logger.info(f"Generating comprehensive EDA report for '{dataset_name}'...")
        dates = pd.to_datetime(df[self.date_col])
        start_str = dates.min().strftime("%Y-%m-%d")
        end_str = dates.max().strftime("%Y-%m-%d")
        total_days = (dates.max() - dates.min()).days + 1

        demand_prof = self.compute_demand_profile(df)
        seg = self.compute_sku_segmentation(df)
        inv_health = self.compute_inventory_health(df)

        return EDASummaryReport(
            dataset_name=dataset_name,
            date_range_start=start_str,
            date_range_end=end_str,
            total_days=total_days,
            total_records=len(df),
            demand_profile=demand_prof,
            segmentation=seg,
            inventory_health=inv_health,
        )

    # -------------------------------------------------------------------------
    # Plotly Visualization Builders
    # -------------------------------------------------------------------------

    def plot_demand_trend_and_seasonality(self, df: pd.DataFrame) -> go.Figure:
        """Generate interactive Plotly multi-curve line chart with rolling averages."""
        data = df.copy()
        data[self.date_col] = pd.to_datetime(data[self.date_col])
        daily = data.groupby(self.date_col)[self.quantity_col].sum().reset_index()
        daily["rolling_7"] = daily[self.quantity_col].rolling(7, min_periods=1).mean()
        daily["rolling_28"] = daily[self.quantity_col].rolling(28, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily[self.date_col],
            y=daily[self.quantity_col],
            mode="lines",
            name="Daily Realized Demand",
            line=dict(color="rgba(31, 119, 180, 0.35)", width=1),
        ))
        fig.add_trace(go.Scatter(
            x=daily[self.date_col],
            y=daily["rolling_7"],
            mode="lines",
            name="7-Day Moving Avg",
            line=dict(color="#1f77b4", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=daily[self.date_col],
            y=daily["rolling_28"],
            mode="lines",
            name="28-Day Moving Avg",
            line=dict(color="#ff7f0e", width=2.5),
        ))

        fig.update_layout(
            title="FORESIGHT — Aggregate Network Demand Trend & Rolling Moving Averages",
            xaxis_title="Date",
            yaxis_title="Total Units Sold",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        return fig

    def plot_day_of_week_seasonality(self, df: pd.DataFrame) -> go.Figure:
        """Generate day-of-week demand bar chart by Category."""
        data = df.copy()
        data[self.date_col] = pd.to_datetime(data[self.date_col])
        data["day_of_week"] = data[self.date_col].dt.day_name()

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_cat = data.groupby(["day_of_week", self.category_col])[self.quantity_col].mean().reset_index()

        fig = px.bar(
            dow_cat,
            x="day_of_week",
            y=self.quantity_col,
            color=self.category_col,
            barmode="group",
            category_orders={"day_of_week": day_order},
            title="Mean Daily Sales by Day of Week & Product Category",
            labels={self.quantity_col: "Mean Daily Units", "day_of_week": "Day of Week"},
            template="plotly_white",
        )
        return fig

    def plot_abc_xyz_matrix(self, df: pd.DataFrame) -> go.Figure:
        """Generate interactive ABC/XYZ scatter matrix (Revenue vs. Coefficient of Variation)."""
        seg = self.compute_sku_segmentation(df)
        items_df = pd.DataFrame([item.model_dump() for item in seg.sku_details])

        fig = px.scatter(
            items_df,
            x="coefficient_of_variation",
            y="total_revenue",
            size="total_units_sold",
            color="abc_xyz_segment",
            hover_name="sku_id",
            hover_data=["product_name", "category", "abc_class", "xyz_class", "demand_pattern"],
            log_y=True,
            title="FORESIGHT — ABC/XYZ Portfolio Matrix (Revenue vs. Volatility)",
            labels={
                "coefficient_of_variation": "Coefficient of Variation (Volatility)",
                "total_revenue": "Total Gross Revenue ($ USD, Log Scale)",
                "abc_xyz_segment": "Segment",
            },
            template="plotly_white",
        )
        return fig

    def plot_sku_inventory_profile(self, df: pd.DataFrame, sku_id: str = "SKU-1001", store_id: str = "STORE-001") -> go.Figure:
        """Generate dual-axis time-series for a single SKU showing sales, inventory, and backorders."""
        sub = df[(df[self.sku_col] == sku_id) & (df[self.store_col] == store_id)].sort_values(by=self.date_col)
        dates = pd.to_datetime(sub[self.date_col])

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sub[self.inventory_col],
                name="On-Hand Inventory",
                line=dict(color="#2ca02c", width=2),
                fill="tozeroy",
                fillcolor="rgba(44, 160, 44, 0.1)",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Bar(
                x=dates,
                y=sub[self.quantity_col],
                name="Daily Sales Units",
                marker_color="rgba(31, 119, 180, 0.6)",
            ),
            secondary_y=True,
        )

        if self.backorder_col in sub.columns and sub[self.backorder_col].sum() > 0:
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=sub[self.backorder_col],
                    name="Stockout Backorders",
                    marker_color="rgba(214, 39, 40, 0.8)",
                ),
                secondary_y=True,
            )

        fig.update_layout(
            title=f"Inventory & Demand Trajectory — {sku_id} at {store_id}",
            xaxis_title="Date",
            template="plotly_white",
            hovermode="x unified",
        )
        fig.update_yaxes(title_text="On-Hand Inventory Units", secondary_y=False)
        fig.update_yaxes(title_text="Daily Sales / Backorder Units", secondary_y=True)
        return fig
