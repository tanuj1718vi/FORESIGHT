"""Executive Overview tab: High-level financial KPIs, portfolio health, and urgent priorities."""

import pandas as pd
import plotly.express as px
import streamlit as st

from foresight.dashboard.components.charts import (
    plot_3d_risk_landscape,
    plot_portfolio_health_donut,
)
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import (
    load_inventory_recommendations,
    load_report_json,
    load_risk_assessments,
)


def render_executive_overview_tab() -> None:
    """Render Executive Overview dashboard tab."""
    st.markdown("### 📊 Executive Inventory Intelligence & Working Capital Overview")

    inv_rep = load_report_json("inventory_optimization_report")
    risk_rep = load_report_json("risk_assessment_report")
    inv_df = load_inventory_recommendations()
    risk_df = load_risk_assessments()

    if inv_df.empty or risk_df.empty:
        st.warning("Inventory intelligence data not found. Run pipeline optimizers to generate latest state.")
        return

    # Top KPI Metrics Row (3D Glow Cards)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cap = inv_rep.get("total_working_capital_committed", inv_df["working_capital_committed"].sum())
        render_kpi_card(
            title="Committed Working Capital",
            value=f"${cap:,.0f}",
            subtitle=f"Across {len(inv_df)} SKU-Store Nodes",
            delta="12.4% Optimal vs Baseline",
            theme="cyan",
            icon="💎",
        )

    with col2:
        units = inv_rep.get("total_recommended_order_units", inv_df["recommended_order_quantity"].sum())
        render_kpi_card(
            title="Urgent Replenishment Required",
            value=f"{units:,.0f} units",
            subtitle="Immediate Purchase Orders",
            delta="48h Fulfillment Window",
            theme="amber",
            icon="📦",
        )

    with col3:
        lost_margin = risk_rep.get("total_lost_margin_exposure", risk_df["lost_margin_risk"].sum())
        render_kpi_card(
            title="Lost Gross Margin Risk",
            value=f"${lost_margin:,.0f}",
            subtitle="Potential Stockout Impact",
            theme="crimson",
            icon="🚨",
        )

    with col4:
        carrying_cost = inv_rep.get("total_annual_inventory_cost", inv_df["total_annual_inventory_cost"].sum())
        render_kpi_card(
            title="Annual Carrying Cost",
            value=f"${carrying_cost:,.0f}/yr",
            subtitle="Holding + Ordering Costs",
            delta="EOQ Minimized",
            theme="emerald",
            icon="📈",
        )

    st.markdown("---")

    # Second Row: Portfolio Health Donut + Financial Exposure Breakdown
    c_left, c_right = st.columns([1, 1])

    with c_left:
        health_counts = inv_rep.get("health_distribution", inv_df["health_status"].value_counts().to_dict())
        fig_donut = plot_portfolio_health_donut(health_counts)
        st.plotly_chart(fig_donut, use_container_width=True, key="exec_health_donut_chart")

    with c_right:
        st.markdown("#### ⚡ Financial Exposure vs Loss Mitigation")
        financial_df = pd.DataFrame([
            {"Risk Category": "Lost Gross Margin (Stockout Exposure)", "Financial Exposure ($)": float(risk_rep.get("total_lost_margin_exposure", 0))},
            {"Risk Category": "Excess Holding Penalty (Dead Stock)", "Financial Exposure ($)": float(risk_rep.get("total_excess_holding_risk", 0))},
        ])
        fig_bar = px.bar(
            financial_df,
            x="Financial Exposure ($)",
            y="Risk Category",
            orientation="h",
            color="Risk Category",
            color_discrete_sequence=["#ff0055", "#a855f7"],
            text="Financial Exposure ($)",
            template="plotly_dark",
        )
        fig_bar.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.7)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            height=350,
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="exec_fin_exposure_bar_chart")

    st.markdown("---")

    # Third Row: Interactive 3D Risk Terrain Visualizer
    st.markdown("#### 🌐 3D Multi-Echelon Risk Topography (Interactive 3D View)")
    merged_risk_df = risk_df.merge(inv_df[["sku_id", "store_id", "days_of_supply"]], on=["sku_id", "store_id"], how="left")
    st.plotly_chart(plot_3d_risk_landscape(merged_risk_df), use_container_width=True, key="exec_3d_risk_landscape_chart")

    st.markdown("---")

    # Fourth Row: Priority Urgent Actions Table with Quick Click Filter
    st.markdown("#### 🚨 Priority Action Work Orders")
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        view_filter = st.radio(
            "Filter Queue:",
            ["🔴 CRITICAL EXPEDITE & ORDER", "🟣 OVERSTOCKED / EXCESS", "🟢 ALL NODES"],
            horizontal=True,
            key="exec_view_filter",
        )

    if "CRITICAL" in view_filter:
        display_df = inv_df[inv_df["recommended_action"].isin(["EXPEDITE", "ORDER"])].sort_values("stockout_risk_prob", ascending=False).head(15)
    elif "OVERSTOCKED" in view_filter:
        display_df = inv_df[inv_df["health_status"].isin(["OVERSTOCKED", "CRITICAL_EXCESS"])].sort_values("days_of_supply", ascending=False).head(15)
    else:
        display_df = inv_df.head(15)

    display_cols = [
        "sku_id", "store_id", "net_stock", "safety_stock", "reorder_point",
        "recommended_order_quantity", "days_of_supply", "stockout_risk_prob", "health_status", "recommended_action"
    ]
    
    st.dataframe(
        display_df[display_cols].style.format({
            "net_stock": "{:.0f}",
            "safety_stock": "{:.1f}",
            "reorder_point": "{:.1f}",
            "recommended_order_quantity": "{:.0f}",
            "days_of_supply": "{:.1f}d",
            "stockout_risk_prob": "{:.1%}",
        }),
        use_container_width=True,
    )
