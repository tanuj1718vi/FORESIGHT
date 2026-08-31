"""Risk & Action Center tab: Prescriptive recommendations, lateral transfers, and work orders."""

import math
import textwrap
from scipy.stats import norm
import pandas as pd
import streamlit as st

from foresight.dashboard.components.charts import (
    plot_3d_echelon_network,
    plot_3d_risk_landscape,
    plot_risk_matrix_scatter,
)
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import (
    load_engineered_features,
    load_inventory_recommendations,
    load_prescriptive_recommendations,
    load_risk_assessments,
)
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters
from foresight.recommendations.engine import PrescriptiveEngine
from foresight.risk.scorer import assess_sku_risk


def render_risk_action_center_tab() -> None:
    """Render Risk & Prescriptive Action Center tab with real-time dynamic decisioning engine."""
    st.markdown("### 🎯 Prescriptive Decision & Financial Risk Command Center")

    # Visual Workflow Flowchart
    st.markdown(
        textwrap.dedent("""
        <div style="
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(244, 63, 94, 0.25);
            border-radius: 10px;
            padding: 12px 18px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.82rem;
            color: #cbd5e1;
        ">
            <span style="color:#f43f5e; font-weight:700;">⚡ REAL-TIME RISK DECISIONING LOGIC:</span>
            <span>1️⃣ Forecast Lead-Time Demand</span> <span>+</span>
            <span>2️⃣ Net Inventory Position</span> <span>+</span>
            <span>3️⃣ Replenishment Lead Time</span> <span>➔</span>
            <span>4️⃣ Stockout / Overstock Exposure</span> <span>➔</span>
            <span>5️⃣ Prescriptive Work Order</span>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    recs_df = load_prescriptive_recommendations()
    risk_df = load_risk_assessments()
    inv_df = load_inventory_recommendations()
    feat_df = load_engineered_features()

    if recs_df.empty or risk_df.empty:
        st.warning("Prescriptive recommendation data not found.")
        return

    # Top KPI Row
    total_exposure = risk_df["total_financial_exposure"].sum()
    lateral_transfers = recs_df[recs_df["action"] == "REBALANCE"]
    lateral_savings = lateral_transfers["expected_financial_impact"].sum() if not lateral_transfers.empty else 0.0
    critical_actions = len(recs_df[recs_df["urgency"].isin(["CRITICAL", "HIGH"])])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Financial Exposure", f"${total_exposure:,.0f}", "Value at Risk across Portfolio", theme="crimson", icon="🚨")
    with k2:
        render_kpi_card("High Urgency Orders", f"{critical_actions} Actions", "Immediate Execution Queue", theme="amber", icon="⚡")
    with k3:
        render_kpi_card("Lateral Opportunities", f"{len(lateral_transfers)} Transfers", "Intra-Store Load Balancing", theme="cyan", icon="🔄")
    with k4:
        render_kpi_card("Capital Saved via Rebalancing", f"${lateral_savings:,.0f}", "Bypasses Supplier Lead Times", theme="emerald", icon="💰")

    st.markdown("---")

    # ==========================================
    # ⚡ LIVE INTERACTIVE RISK & DECISION CALCULATOR
    # ==========================================
    with st.expander("⚡ Interactive Real-Time Risk & Prescriptive Decision Calculator (Live Calculation Engine)", expanded=True):
        st.markdown("Select a node or adjust parameters dynamically to execute live safety stock, stockout probability, and prescriptive work order generation:")

        available_skus = sorted(feat_df["sku_id"].unique()) if not feat_df.empty else ["SKU-1001"]
        available_stores = sorted(feat_df["store_id"].unique()) if not feat_df.empty else ["STORE-001"]

        c_calc1, c_calc2, c_calc3 = st.columns(3)
        with c_calc1:
            calc_sku = st.selectbox("Target SKU:", available_skus, key="calc_sku_sel")
        with c_calc2:
            calc_store = st.selectbox("Target Store:", available_stores, key="calc_store_sel")
        with c_calc3:
            calc_sla = st.slider("Target Service Level (SLA):", min_value=0.80, max_value=0.999, value=0.95, step=0.01, key="calc_sla_slider")

        # Fetch underlying parameters
        if not feat_df.empty:
            sub = feat_df[(feat_df["sku_id"] == calc_sku) & (feat_df["store_id"] == calc_store)].sort_values("date")
            row = sub.iloc[-1] if not sub.empty else {}
        else:
            row = {}

        def_mean = float(row.get("rolling_mean_7", row.get("quantity", 25.0)))
        def_std = float(row.get("rolling_std_7", max(1.0, def_mean * 0.25)))
        def_lt = float(row.get("lead_time_days", 14.0))
        def_oh = float(row.get("inventory_level", 120.0))
        def_oo = float(row.get("units_on_order", 0.0))
        def_cost = float(row.get("unit_cost", 20.0))
        def_price = float(row.get("unit_price", 38.0))

        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            inp_oh = st.number_input("On-Hand Physical Stock (Units):", value=float(def_oh), step=10.0, key="inp_oh")
            inp_oo = st.number_input("In-Transit On-Order (Units):", value=float(def_oo), step=10.0, key="inp_oo")
        with c_p2:
            inp_mean = st.number_input("Predicted Daily Demand (Units/d):", value=float(def_mean), step=1.0, key="inp_mean")
            inp_std = st.number_input("Demand Uncertainty (σ):", value=float(def_std), step=0.5, key="inp_std")
        with c_p3:
            inp_lt = st.number_input("Supplier Lead Time (Days):", value=float(def_lt), step=1.0, key="inp_lt")
            inp_lt_std = st.number_input("Lead Time Uncertainty (Days):", value=float(max(0.5, def_lt * 0.15)), step=0.5, key="inp_lt_std")
        with c_p4:
            inp_cost = st.number_input("Unit Cost ($/₹):", value=float(def_cost), step=1.0, key="inp_cost")
            inp_price = st.number_input("Unit Selling Price ($/₹):", value=float(def_price), step=1.0, key="inp_price")

        # Live Real-Time Mathematical Engine Execution
        params_live = InventoryParameters(
            sku_id=str(calc_sku),
            store_id=str(calc_store),
            current_on_hand=inp_oh,
            units_on_order=inp_oo,
            backorders=0.0,
            unit_cost=inp_cost,
            unit_price=inp_price,
            lead_time_days=inp_lt,
            lead_time_std_days=inp_lt_std,
            holding_cost_annual_rate=0.20,
            fixed_order_cost=50.0,
            min_order_qty=10.0,
            target_service_level=calc_sla,
            forecast_daily_demand_mean=inp_mean,
            forecast_daily_demand_std=inp_std,
        )

        opt_live = InventoryOptimizer().optimize_sku(params_live)
        risk_live = assess_sku_risk(opt_live, params_live)
        rec_live = PrescriptiveEngine().generate_recommendation(opt_live, risk_live, params_live)

        # 4-Quadrant Classification Matrix Logic
        st.markdown("#### 📊 Live Decisioning Result & Prescriptive Work Order")
        c_res1, c_res2, c_res3, c_res4 = st.columns(4)

        theme_badge = "#10b981"
        quadrant_label = "✅ HEALTHY BUFFER"
        if risk_live.stockout_risk_score >= 50.0 and risk_live.overstock_risk_score < 40.0:
            theme_badge = "#ff0055"
            quadrant_label = "🚨 REORDER NOW / EXPEDITE"
        elif risk_live.overstock_risk_score >= 50.0 and risk_live.stockout_risk_score < 40.0:
            theme_badge = "#a855f7"
            quadrant_label = "🏷️ MARKDOWN / CLEAR"
        elif risk_live.stockout_risk_score >= 50.0 and risk_live.overstock_risk_score >= 50.0:
            theme_badge = "#f59e0b"
            quadrant_label = "⚠️ WATCH / VOLATILE"

        with c_res1:
            st.metric("Net Stock Position", f"{opt_live.net_stock:.0f} units", help="On-Hand + On-Order - Backorders")
            st.metric("Lead-Time Demand", f"{opt_live.lead_time_demand:.1f} units", help="Daily Mean * Lead Time Days")
        with c_res2:
            st.metric("Safety Stock Buffer", f"{opt_live.safety_stock:.1f} units", help=f"Sized for {calc_sla*100:.0f}% SLA")
            st.metric("Reorder Point (ROP)", f"{opt_live.reorder_point:.1f} units", help="LTD + Safety Stock")
        with c_res3:
            st.metric("Stockout Probability", f"{opt_live.stockout_risk_prob:.1%}", delta=f"{risk_live.stockout_risk_score:.0f}/100 Risk", delta_color="inverse")
            st.metric("Days of Supply (DOS)", f"{opt_live.days_of_supply:.1f} days")
        with c_res4:
            st.markdown(
                textwrap.dedent(f"""
                <div style="background: rgba(30,41,59,0.8); border: 2px solid {theme_badge}; border-radius: 10px; padding: 12px 14px; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">4-QUADRANT STATUS</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: {theme_badge}; margin: 4px 0;">{quadrant_label}</div>
                    <div style="font-size: 0.75rem; color: #cbd5e1;">Prescribed Action: <b>{rec_live.action.value}</b> ({rec_live.recommended_quantity:.0f} units)</div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

        # Decision Narrative Justification
        st.info(f"💡 **Decision Rationale:** {rec_live.justification} | **Value at Stake:** ${risk_live.total_financial_exposure:,.2f} (Lost Margin Risk: ${risk_live.lost_margin_risk:,.2f}, Carrying Risk: ${risk_live.excess_holding_cost_risk:,.2f}/yr)")

    st.markdown("---")

    # Merge for comprehensive risk matrix
    merged_risk_df = risk_df.merge(inv_df[["sku_id", "store_id", "days_of_supply"]], on=["sku_id", "store_id"], how="left")

    # Visualizations Row: 2D Matrix vs 3D Landscape
    v_tab1, v_tab2, v_tab3 = st.tabs(["🌐 3D Risk Topography", "🗺️ 3D Lateral Transfer Network", "📊 2D Risk Matrix Scatter"])

    with v_tab1:
        st.plotly_chart(plot_3d_risk_landscape(merged_risk_df), use_container_width=True, key="risk_3d_risk_landscape_chart")

    with v_tab2:
        if not lateral_transfers.empty:
            st.plotly_chart(plot_3d_echelon_network(lateral_transfers), use_container_width=True, key="risk_3d_network_topology_chart")
        else:
            st.info("No active lateral transfers to display in 3D network topology.")

    with v_tab3:
        st.plotly_chart(plot_risk_matrix_scatter(merged_risk_df), use_container_width=True, key="risk_2d_matrix_scatter_chart")

    st.markdown("---")

    # Prescriptive Action Work Orders Queue
    st.markdown("#### 📋 Prescriptive Replenishment & Corrective Work Orders Queue")

    c_filter1, c_filter2 = st.columns(2)
    with c_filter1:
        selected_action = st.selectbox(
            "Filter by Prescriptive Action:",
            ["ALL"] + sorted(recs_df["action"].unique().tolist()),
            key="risk_action_filter_dropdown",
        )
    with c_filter2:
        selected_urgency = st.selectbox(
            "Filter by Urgency Level:",
            ["ALL"] + sorted(recs_df["urgency"].unique().tolist()),
            key="risk_urgency_filter_dropdown",
        )

    filtered_recs = recs_df.copy()
    if selected_action != "ALL":
        filtered_recs = filtered_recs[filtered_recs["action"] == selected_action]
    if selected_urgency != "ALL":
        filtered_recs = filtered_recs[filtered_recs["urgency"] == selected_urgency]

    st.dataframe(
        filtered_recs[[
            "recommendation_id", "action", "sku_id", "store_id",
            "recommended_quantity", "urgency", "expected_financial_impact", "confidence_score", "justification"
        ]].style.format({
            "recommended_quantity": "{:.0f}",
            "expected_financial_impact": "${:,.2f}",
            "confidence_score": "{:.1%}",
        }),
        use_container_width=True,
    )

    # Interactive Action Execution
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        if st.button("⚡ Execute Selected Work Orders", key="exec_orders"):
            st.toast(f"✅ Approved and dispatched {len(filtered_recs)} work orders to supply chain orchestration layer!")

    st.markdown("---")

    # 3. Lateral Multi-Store Transfers
    st.markdown("#### 🔄 Intra-Network Lateral Rebalancing Transfers")
    if not lateral_transfers.empty:
        st.dataframe(
            lateral_transfers[[
                "recommendation_id", "sku_id", "store_id", "donor_store_id",
                "recommended_quantity", "expected_financial_impact", "justification"
            ]].style.format({
                "recommended_quantity": "{:.0f}",
                "expected_financial_impact": "${:,.2f}",
            }),
            use_container_width=True,
        )
        if st.button("🚚 Approve All Lateral Rebalance Transfers", key="approve_transfers"):
            st.toast("✅ All intra-network transfers queued for carrier pickup!")
    else:
        st.info("No lateral store transfers currently required; all stores maintain balanced allocations.")

    # 4. Download Action Plan
    csv_data = filtered_recs.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Prescriptive Action Work Orders (CSV)",
        data=csv_data,
        file_name="foresight_prescriptive_work_orders.csv",
        mime="text/csv",
        key="download_work_orders_btn",
    )
