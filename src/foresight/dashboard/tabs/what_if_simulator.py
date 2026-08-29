"""What-If Scenario Simulator tab: Interactive stress testing of supply chain disruptions."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from foresight.dashboard.components.charts import get_dark_cyber_layout
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import load_engineered_features
from foresight.inventory.schema import InventoryParameters
from foresight.risk.schema import ScenarioParameters
from foresight.risk.simulator import WhatIfSimulator


def render_what_if_simulator_tab() -> None:
    """Render What-If Scenario Simulator tab with 3D sensitivity surface and interactive shock presets."""
    st.markdown("### 🧪 Supply Chain Stress & What-If Disruption Simulator")
    st.caption("Simulate macroeconomic disruptions, supplier lead time bottlenecks, and market surges in real-time.")

    df = load_engineered_features()
    if df.empty:
        st.warning("Feature data not found.")
        return

    # Preset Disruption Quick-Buttons
    st.markdown("#### ⚡ Disruption Scenario Quick Presets")
    col_p1, col_p2, col_p3 = st.columns(3)

    if "preset" not in st.session_state:
        st.session_state["preset"] = "custom"

    with col_p1:
        if st.button("🚢 Port Bottleneck (+80% Lead Time)", key="btn_port"):
            st.session_state["lt_val"] = 1.8
            st.session_state["dem_val"] = 1.0
    with col_p2:
        if st.button("⚡ Demand Surge (+50% Market Spike)", key="btn_spike"):
            st.session_state["lt_val"] = 1.0
            st.session_state["dem_val"] = 1.5
    with col_p3:
        if st.button("🌊 Black Swan Combined (+60% LT, +30% Dem)", key="btn_swan"):
            st.session_state["lt_val"] = 1.6
            st.session_state["dem_val"] = 1.3

    lt_default = st.session_state.get("lt_val", 1.5)
    dem_default = st.session_state.get("dem_val", 1.25)

    # Scenario Parameter Controls in Sidebar/Columns
    st.markdown("#### 1. Stress Parameter Control Center")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        lt_mult = st.slider("Supplier Lead Time Shift:", min_value=0.5, max_value=2.5, value=float(lt_default), step=0.1, help="1.5x = +50% supplier delay", key="sim_lt_slider")
    with col_s2:
        dem_mult = st.slider("Market Demand Surge / Drop:", min_value=0.5, max_value=2.0, value=float(dem_default), step=0.05, help="1.25x = +25% demand surge", key="sim_dem_slider")
    with col_s3:
        target_sl = st.slider("Target Service Level (SLA):", min_value=0.80, max_value=0.999, value=0.98, step=0.01, key="sim_sla_slider")
    with col_s4:
        hold_mult = st.slider("Holding Cost Rate Shift:", min_value=0.5, max_value=2.0, value=1.0, step=0.1, key="sim_hold_slider")

    available_skus = sorted(df["sku_id"].unique())
    available_stores = sorted(df["store_id"].unique())

    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        selected_sku = st.selectbox("Select Target SKU:", available_skus, key="sim_sku")
    with c_sel2:
        selected_store = st.selectbox("Select Store Location:", available_stores, key="sim_store")

    # Extract slice
    sku_df = df[(df["sku_id"] == selected_sku) & (df["store_id"] == selected_store)].sort_values("date")
    if sku_df.empty:
        st.error("No observation data found.")
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
        target_service_level=0.95,
        forecast_daily_demand_mean=mean_d,
        forecast_daily_demand_std=std_d,
    )

    scenario = ScenarioParameters(
        scenario_name="Stress Simulation",
        lead_time_multiplier=lt_mult,
        demand_multiplier=dem_mult,
        target_service_level=target_sl,
        holding_cost_rate_multiplier=hold_mult,
    )

    simulator = WhatIfSimulator()
    sim_res = simulator.simulate_sku(params, scenario)

    st.markdown("---")

    # 2. 3D Delta Impact KPI Tiles
    st.markdown("#### 2. Operational & Capital Exposure Delta Scorecard")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        render_kpi_card(
            title="Safety Stock Buffer",
            value=f"{sim_res.simulated_safety_stock:.1f} units",
            subtitle=f"Baseline: {sim_res.baseline_safety_stock:.1f} units",
            delta=f"{sim_res.delta_safety_stock:+.1f} units buffer",
            theme="cyan",
            icon="🛡️",
        )

    with kpi2:
        render_kpi_card(
            title="Reorder Point (ROP)",
            value=f"{sim_res.simulated_reorder_point:.1f} units",
            subtitle=f"Baseline: {sim_res.baseline_reorder_point:.1f} units",
            delta=f"{sim_res.delta_reorder_point:+.1f} units trigger",
            theme="amber",
            icon="🎯",
        )

    with kpi3:
        render_kpi_card(
            title="Committed Working Capital",
            value=f"${sim_res.simulated_working_capital:,.2f}",
            subtitle="Required Cash Allocation",
            delta=f"${sim_res.delta_working_capital:+,.2f} change",
            theme="crimson" if sim_res.delta_working_capital > 0 else "emerald",
            icon="💎",
        )

    with kpi4:
        render_kpi_card(
            title="Annual Carrying Cost",
            value=f"${sim_res.simulated_total_annual_cost:,.2f}/yr",
            subtitle="Holding + Ordering",
            delta=f"${sim_res.delta_total_annual_cost:+,.2f}/yr",
            theme="purple",
            icon="📈",
        )

    st.markdown("---")

    # 3. 3D Stress Sensitivity Surface Plot
    st.markdown("#### 🌐 3D Supply Chain Stress Sensitivity Surface")
    
    # Generate 3D Grid: Lead Time Multiplier vs Demand Multiplier vs Delta Safety Stock
    lt_grid = np.linspace(0.8, 2.2, 20)
    dem_grid = np.linspace(0.8, 2.0, 20)
    LT, DEM = np.meshgrid(lt_grid, dem_grid)
    
    # Calculate SS surface for grid
    z_scores = 1.96  # ~97.5% SL
    SS_SURFACE = z_scores * np.sqrt(
        (lead_time * LT * ((std_d * DEM) ** 2)) + (((mean_d * DEM) ** 2) * ((params.lead_time_std_days * LT) ** 2))
    )

    fig_3d_surf = go.Figure(
        data=[
            go.Surface(
                x=LT,
                y=DEM,
                z=SS_SURFACE,
                colorscale="Plasma",
                colorbar=dict(title="Required Safety Stock (Units)", tickfont=dict(color="#94a3b8")),
                opacity=0.9,
            )
        ]
    )

    fig_3d_surf.update_layout(
        title=dict(
            text=f"<b>3D Stress Response Topography for {selected_sku} @ {selected_store}</b>",
            font=dict(color="#f8fafc", size=14),
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        scene=dict(
            xaxis=dict(title=dict(text="Lead Time Multiplier (Shift)", font=dict(color="#38bdf8")), backgroundcolor="rgba(15,23,42,0.6)", gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="#94a3b8")),
            yaxis=dict(title=dict(text="Demand Surge Multiplier", font=dict(color="#a855f7")), backgroundcolor="rgba(15,23,42,0.6)", gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="#94a3b8")),
            zaxis=dict(title=dict(text="Required Safety Stock", font=dict(color="#10b981")), backgroundcolor="rgba(15,23,42,0.6)", gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="#94a3b8")),
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.2)),
        ),
        height=480,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    st.plotly_chart(fig_3d_surf, use_container_width=True, key="sim_3d_stress_surface_chart")

    st.markdown("---")

    # 4. Side-by-Side Comparison Chart
    st.markdown("#### 📊 Baseline vs Simulated Scenario Policy Comparison")

    categories = ["Safety Stock (Units)", "Reorder Point (Units)", "Working Capital ($100s)", "Annual Carrying Cost ($100s)"]
    baseline_vals = [
        sim_res.baseline_safety_stock,
        sim_res.baseline_reorder_point,
        sim_res.baseline_working_capital / 100.0,
        sim_res.baseline_total_annual_cost / 100.0,
    ]
    simulated_vals = [
        sim_res.simulated_safety_stock,
        sim_res.simulated_reorder_point,
        sim_res.simulated_working_capital / 100.0,
        sim_res.simulated_total_annual_cost / 100.0,
    ]

    fig_comp = go.Figure(
        data=[
            go.Bar(name="Baseline Policy", x=categories, y=baseline_vals, marker_color="#475569"),
            go.Bar(name=f"Simulated Scenario ({lt_mult:.1f}x LT, {dem_mult:.2f}x Dem)", x=categories, y=simulated_vals, marker_color="#00f0ff"),
        ]
    )

    layout = get_dark_cyber_layout(f"Policy Delta: Baseline vs Stress for {selected_sku} @ {selected_store}", height=400)
    fig_comp.update_layout(**layout)
    fig_comp.update_layout(barmode="group")

    st.plotly_chart(fig_comp, use_container_width=True, key="sim_policy_comparison_bar_chart")
