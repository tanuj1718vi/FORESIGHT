"""Risk & Action Center tab: Prescriptive recommendations, lateral transfers, and work orders."""

import pandas as pd
import streamlit as st

from foresight.dashboard.components.charts import (
    plot_3d_echelon_network,
    plot_3d_risk_landscape,
    plot_risk_matrix_scatter,
)
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import (
    load_inventory_recommendations,
    load_prescriptive_recommendations,
    load_risk_assessments,
)


def render_risk_action_center_tab() -> None:
    """Render Risk & Prescriptive Action Center tab."""
    st.markdown("### 🎯 Prescriptive Decision & Financial Risk Command Center")

    recs_df = load_prescriptive_recommendations()
    risk_df = load_risk_assessments()
    inv_df = load_inventory_recommendations()

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

    # Prescriptive Action Work Orders
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
