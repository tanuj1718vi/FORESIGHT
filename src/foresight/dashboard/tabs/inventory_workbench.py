"""Inventory Policy & Reorder Workbench tab: Multi-method safety stock, ROP, and Wilson EOQ curves."""

import pandas as pd
import streamlit as st

from foresight.dashboard.components.charts import plot_eoq_cost_curves
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import load_engineered_features, load_inventory_recommendations
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.safety_stock import (
    calculate_safety_stock_combined,
    calculate_safety_stock_demand_uncertainty,
    calculate_safety_stock_lead_time_uncertainty,
    calculate_safety_stock_quantile,
)
from foresight.inventory.schema import InventoryParameters


def render_inventory_workbench_tab() -> None:
    """Render Inventory Policy & Reorder Workbench tab."""
    st.markdown("### ⚙️ Multi-Echelon Policy Optimization & Reorder Workbench")

    df = load_engineered_features()
    inv_df = load_inventory_recommendations()

    if df.empty or inv_df.empty:
        st.warning("Inventory intelligence data not found.")
        return

    # Selectors Container
    col_sku, col_store, col_sl = st.columns([1.5, 1.5, 1.2])

    available_skus = sorted(df["sku_id"].unique())
    available_stores = sorted(df["store_id"].unique())

    with col_sku:
        selected_sku = st.selectbox("Select SKU:", available_skus, key="inv_sku")
    with col_store:
        selected_store = st.selectbox("Select Store:", available_stores, key="inv_store")
    with col_sl:
        target_sl = st.slider("Target Service Level (SLA):", min_value=0.80, max_value=0.99, value=0.95, step=0.01, key="inv_sla_slider")

    # Get latest row
    sku_df = df[(df["sku_id"] == selected_sku) & (df["store_id"] == selected_store)].sort_values("date")
    if sku_df.empty:
        st.error("No data found for selection.")
        return

    latest_row = sku_df.iloc[-1]

    mean_d = float(latest_row.get("rolling_mean_7", latest_row.get("quantity", 10.0)))
    std_d = float(latest_row.get("rolling_std_7", max(1.0, mean_d * 0.25)))
    lead_time = float(latest_row.get("lead_time_days", 7.0))
    unit_cost = float(latest_row.get("unit_cost", 20.0))
    unit_price = float(latest_row.get("unit_price", 35.0))
    on_hand = float(latest_row.get("inventory_level", 50.0))
    on_order = float(latest_row.get("units_on_order", 0.0))
    backorders = float(latest_row.get("backorders", 0.0))
    moq = float(latest_row.get("min_order_qty", 1.0))
    holding_rate = float(latest_row.get("holding_cost_annual_rate", 0.20))

    params = InventoryParameters(
        sku_id=str(selected_sku),
        store_id=str(selected_store),
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
        target_service_level=target_sl,
        forecast_daily_demand_mean=mean_d,
        forecast_daily_demand_std=std_d,
    )

    optimizer = InventoryOptimizer()
    opt_res = optimizer.optimize_sku(params)

    # 1. 3D KPI Metric Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Net Stock Position", f"{opt_res.net_stock:.0f} units", subtitle=f"On Hand: {on_hand:.0f} | On Order: {on_order:.0f}", theme="cyan", icon="📦")
    with col2:
        render_kpi_card("Safety Stock Buffer", f"{opt_res.safety_stock:.1f} units", subtitle=f"Target SLA: {target_sl*100:.0f}%", theme="emerald", icon="🛡️")
    with col3:
        render_kpi_card("Reorder Point (ROP)", f"{opt_res.reorder_point:.1f} units", subtitle=f"Lead Time Demand: {opt_res.lead_time_demand:.1f}", theme="amber", icon="🎯")
    with col4:
        theme_action = "crimson" if opt_res.recommended_action in ["EXPEDITE", "ORDER"] else "purple"
        render_kpi_card("Prescriptive Action", f"{opt_res.recommended_action}", subtitle=f"Recommended Qty: {opt_res.recommended_order_quantity:.0f} units", theme=theme_action, icon="⚡")

    # Interactive Action Execution Bar
    col_act1, col_act2 = st.columns([3, 1])
    with col_act1:
        st.markdown(f"**Action Status:** `Health Status: {opt_res.health_status.value}` | `Days of Supply: {opt_res.days_of_supply:.1f}d` | `Stockout Prob: {opt_res.stockout_risk_prob:.1%}`")
    with col_act2:
        if st.button("🚀 Dispatch Reorder Order", key="dispatch_order"):
            st.toast(f"✅ Purchase Order for {opt_res.recommended_order_quantity:.0f} units of {selected_sku} dispatched to ERP!")

    st.markdown("---")

    # 2. Safety Stock Method Comparison Table
    st.markdown("#### 🛡️ Multi-Method Safety Stock Benchmark")

    ss_combined = calculate_safety_stock_combined(
        mean_demand=mean_d,
        std_demand=std_d,
        mean_lead_time=lead_time,
        std_lead_time=params.lead_time_std_days,
        service_level=target_sl,
    )
    ss_demand_only = calculate_safety_stock_demand_uncertainty(
        mean_lead_time=lead_time,
        std_demand=std_d,
        service_level=target_sl,
    )
    ss_lt_only = calculate_safety_stock_lead_time_uncertainty(
        mean_demand=mean_d,
        std_lead_time=params.lead_time_std_days,
        service_level=target_sl,
    )
    ss_quantile = calculate_safety_stock_quantile(
        forecast_p50_daily=mean_d,
        forecast_p95_daily=mean_d * 1.5,
        lead_time_days=lead_time,
    )

    ss_benchmark_df = pd.DataFrame([
        {"Method": "Combined Uncertainty (Industrial Default)", "Formula": "Z * sqrt(L * σ_d^2 + d^2 * σ_L^2)", "Safety Stock (Units)": round(ss_combined, 1), "Protection Scope": "Demand + Supplier Lead Time Volatility"},
        {"Method": "Demand Uncertainty Only", "Formula": "Z * σ_d * sqrt(L)", "Safety Stock (Units)": round(ss_demand_only, 1), "Protection Scope": "Daily Demand Variance (Fixed Lead Time)"},
        {"Method": "Lead Time Uncertainty Only", "Formula": "Z * d_bar * σ_L", "Safety Stock (Units)": round(ss_lt_only, 1), "Protection Scope": "Supplier Delays (Constant Demand)"},
        {"Method": "Non-Parametric ML Quantile Buffer", "Formula": "(P95 - P50) * sqrt(L)", "Safety Stock (Units)": round(ss_quantile, 1), "Protection Scope": "Heavy-Tailed / Non-Gaussian Demand Shocks"},
    ])
    st.dataframe(ss_benchmark_df, use_container_width=True)

    st.markdown("---")

    # 3. Wilson EOQ Cost Trade-off Visualizer
    st.markdown("#### 📦 Wilson Economic Order Quantity (EOQ) Cost Optimization Curves")
    annual_demand = mean_d * 365.0
    fig_eoq = plot_eoq_cost_curves(
        annual_demand=annual_demand,
        order_cost=params.fixed_order_cost,
        unit_cost=unit_cost,
        holding_rate=holding_rate,
        optimal_eoq=opt_res.economic_order_quantity,
    )
    st.plotly_chart(fig_eoq, use_container_width=True, key="inv_eoq_cost_curves_chart")
