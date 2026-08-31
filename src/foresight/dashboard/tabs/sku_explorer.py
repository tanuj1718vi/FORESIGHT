"""SKU & Forecast Explorer tab: Point forecasts, P10-P90 intervals, TreeSHAP waterfall decomposition."""

from datetime import datetime, timedelta
import time
import textwrap
import numpy as np
import pandas as pd
import streamlit as st

from foresight.dashboard.components.charts import plot_forecast_with_intervals
from foresight.dashboard.components.kpi_cards import render_kpi_card
from foresight.dashboard.data_provider import (
    load_champion_model,
    load_engineered_features,
    load_quantile_model,
)
from foresight.explainability.shap_explainer import ForecastExplainer


def render_sku_explorer_tab() -> None:
    """Render SKU Deep-Dive & Forecast Explorer tab with high-graphics UI."""
    st.markdown("### 🔍 SKU Deep-Dive & Probabilistic Forecast Explorer")

    # Visual Flowchart of Active Inference Pipeline
    st.markdown(
        textwrap.dedent("""
        <div style="
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(56, 189, 248, 0.25);
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
            <span style="color:#38bdf8; font-weight:700;">⚡ LIVE INFERENCE PIPELINE:</span>
            <span>1️⃣ Ingest History</span> <span>➔</span>
            <span>2️⃣ Extract 60 Features</span> <span>➔</span>
            <span>3️⃣ XGBoost Model Inference</span> <span>➔</span>
            <span>4️⃣ Quantile Intervals (P10/P90)</span> <span>➔</span>
            <span>5️⃣ TreeSHAP Attribution</span>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    df = load_engineered_features()
    model = load_champion_model()
    q_model = load_quantile_model()

    if df.empty or model is None:
        st.warning("Forecasting models or feature data not loaded.")
        return

    # Selectors & Real-Time Parameter Controls
    col_sku, col_store, col_horizon, col_promo = st.columns([1.2, 1.2, 1.0, 1.2])

    available_skus = sorted(df["sku_id"].unique())
    available_stores = sorted(df["store_id"].unique())

    with col_sku:
        selected_sku = st.selectbox("📦 Target SKU:", available_skus, index=0, key="sku_sel_dropdown")
    with col_store:
        selected_store = st.selectbox("🏬 Fulfillment Node:", available_stores, index=0, key="store_sel_dropdown")
    with col_horizon:
        horizon_days = st.slider("📅 Horizon (Days):", min_value=7, max_value=60, value=30, step=7, key="horizon_slider")
    with col_promo:
        promo_boost = st.selectbox(
            "⚡ Promo / Market Condition:",
            ["Normal Baseline (1.0x)", "Active Promotion (+30% Lift)", "Flash Sale Surge (+60% Lift)", "Off-Season Slowdown (-20%)"],
            index=0,
            key="sku_promo_boost_sel",
        )

    promo_multiplier = 1.0
    if "+30%" in promo_boost:
        promo_multiplier = 1.30
    elif "+60%" in promo_boost:
        promo_multiplier = 1.60
    elif "-20%" in promo_boost:
        promo_multiplier = 0.80

    # Filter data for selected node
    sku_df = df[(df["sku_id"] == selected_sku) & (df["store_id"] == selected_store)].sort_values("date")
    if sku_df.empty:
        st.error(f"No history found for SKU {selected_sku} at Store {selected_store}.")
        return

    # Start live inference timer
    t_start = time.perf_counter()

    # Telemetry metrics
    mean_sales = float(sku_df["quantity"].mean())
    max_sales = float(sku_df["quantity"].max())
    rolling_vol = float(sku_df["rolling_std_7"].iloc[-1]) if "rolling_std_7" in sku_df.columns else 2.5
    price = float(sku_df["unit_price"].iloc[-1]) if "unit_price" in sku_df.columns else 25.0

    # Prepare Historical Slice
    hist_slice = sku_df.tail(90)
    dates_hist = hist_slice["date"].tolist()
    y_hist = hist_slice["quantity"].tolist()

    # Generate Real-Time Forward Forecast via Model.predict()
    latest_row = sku_df.iloc[-1]
    features = model.feature_names_ or []

    fc_dates = [latest_row["date"] + timedelta(days=i) for i in range(1, horizon_days + 1)]

    fc_rows = []
    curr_row = latest_row.copy()
    for d in fc_dates:
        curr_row["date"] = d
        curr_row["day_of_week"] = d.dayofweek
        curr_row["is_weekend"] = int(d.dayofweek in [5, 6])
        curr_row["month"] = d.month
        if promo_multiplier > 1.0:
            curr_row["is_promoted"] = 1
        elif promo_multiplier < 1.0:
            curr_row["is_promoted"] = 0
        fc_rows.append(curr_row[features].to_dict())

    X_fc = pd.DataFrame(fc_rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y_fc_raw = model.predict(X_fc)
    y_fc = [float(max(0.0, v * promo_multiplier)) for v in y_fc_raw]

    # Quantile bounds
    if q_model is not None:
        q_preds = q_model.predict_quantiles(X_fc, quantiles=[0.10, 0.90])
        y_p10 = [max(0.0, float(v * promo_multiplier)) for v in q_preds[0.10]]
        y_p90 = [max(float(y_p10[i]), float(v * promo_multiplier)) for i, v in enumerate(q_preds[0.90])]
    else:
        std_val = float(latest_row.get("rolling_std_7", max(1.0, np.mean(y_fc) * 0.25)))
        y_p10 = [max(0.0, float(v - 1.645 * std_val)) for v in y_fc]
        y_p90 = [float(v + 1.645 * std_val) for v in y_fc]

    inference_ms = (time.perf_counter() - t_start) * 1000.0

    # Live Inference Telemetry Badge
    total_forecast_units = sum(y_fc)
    avg_daily_forecast = np.mean(y_fc)

    col_tele1, col_tele2 = st.columns([3, 1])
    with col_tele1:
        st.caption(f"⚡ **Real-Time Model Execution:** `{model.name}` | Horizon: `{horizon_days} days` | Latency: `{inference_ms:.2f} ms` | Cumulative Forecast: `{total_forecast_units:,.0f} units`")
    with col_tele2:
        if st.button("🔄 Re-Run Live Inference", key="rerun_inf_btn"):
            st.toast("⚡ Model inference re-executed across forward horizon!")

    # 3D KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Mean Daily Demand", f"{mean_sales:.1f} units", "Historical 2-yr Mean", theme="cyan", icon="📊")
    with k2:
        render_kpi_card("Forward Avg Forecast", f"{avg_daily_forecast:.1f} units/d", f"{horizon_days}-day Model Prediction", delta=f"{((avg_daily_forecast - mean_sales)/max(0.1, mean_sales)):+.1%}", theme="amber", icon="🔮")
    with k3:
        render_kpi_card("Demand Volatility (σ)", f"±{rolling_vol:.2f}", "7-day Rolling Std", theme="purple", icon="🌊")
    with k4:
        render_kpi_card("Unit Retail Price", f"${price:.2f}", "Catalog Active Price", theme="emerald", icon="🏷️")

    # Plot Trajectory with glowing ribbon
    fig_fc = plot_forecast_with_intervals(
        dates_hist=dates_hist,
        y_hist=y_hist,
        dates_fc=fc_dates,
        y_fc=y_fc,
        y_p10=y_p10,
        y_p90=y_p90,
        sku_id=str(selected_sku),
        store_id=str(selected_store),
    )
    st.plotly_chart(fig_fc, use_container_width=True, key="sku_fc_trajectory_chart")

    st.markdown("---")

    # TreeSHAP Local Driver Decomposition & Executive Narrative
    st.markdown("#### 💡 Explainable AI: TreeSHAP Feature Attributions & Executive Narrative")

    explainer = ForecastExplainer(model)
    local_exp = explainer.explain_observation(
        row_features=latest_row,
        sku_id=str(selected_sku),
        store_id=str(selected_store),
        date=str(latest_row["date"])[:10],
    )

    # Glowing Executive Narrative Card
    st.markdown(
        textwrap.dedent(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(56, 189, 248, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-left: 4px solid #818cf8;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), 0 0 15px rgba(99, 102, 241, 0.2);
        ">
            <div style="font-size: 0.85rem; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 0.05em;">
                🧠 Executive Decision Narrative
            </div>
            <div style="color: #f1f5f9; font-size: 0.96rem; margin-top: 6px; font-weight: 500; line-height: 1.5;">
                {local_exp.business_narrative}
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    col_chart, col_table = st.columns([1.4, 1])

    with col_chart:
        fig_waterfall = explainer.plot_waterfall_explanation(local_exp)
        st.plotly_chart(fig_waterfall, use_container_width=True, key="sku_waterfall_shap_chart")

    with col_table:
        st.markdown("**Top Positive Drivers**")
        pos_df = pd.DataFrame([d.model_dump() for d in local_exp.top_positive_drivers])
        if not pos_df.empty:
            st.dataframe(pos_df[["feature_name", "feature_value", "attribution_units"]], use_container_width=True)

        st.markdown("**Top Negative Drivers**")
        neg_df = pd.DataFrame([d.model_dump() for d in local_exp.top_negative_drivers])
        if not neg_df.empty:
            st.dataframe(neg_df[["feature_name", "feature_value", "attribution_units"]], use_container_width=True)

    # Interactive Instant Custom Sandbox Predictor
    with st.expander("🧪 Interactive Live Prediction Sandbox (Test Custom Feature Inputs)"):
        st.markdown("Enter custom scenario features to trigger the live model regressor instantly:")
        c_in1, c_in2, c_in3, c_in4 = st.columns(4)
        with c_in1:
            cust_lag1 = st.number_input("Yesterday Demand (Lag 1):", value=float(mean_sales), step=1.0)
        with c_in2:
            cust_lag7 = st.number_input("Last Week Demand (Lag 7):", value=float(mean_sales * 1.05), step=1.0)
        with c_in3:
            cust_rolling7 = st.number_input("7-Day Moving Avg:", value=float(mean_sales), step=1.0)
        with c_in4:
            cust_promo = st.checkbox("Active Promotion Flag", value=False)

        if st.button("🔮 Run Instant Custom Prediction", key="run_custom_pred_btn"):
            custom_row = latest_row.copy()
            if "lag_1" in custom_row:
                custom_row["lag_1"] = cust_lag1
            if "lag_7" in custom_row:
                custom_row["lag_7"] = cust_lag7
            if "rolling_mean_7" in custom_row:
                custom_row["rolling_mean_7"] = cust_rolling7
            if "is_promoted" in custom_row:
                custom_row["is_promoted"] = int(cust_promo)

            custom_X = pd.DataFrame([custom_row[features].to_dict()]).fillna(0.0)
            custom_pred = float(model.predict(custom_X)[0])
            st.success(f"🎯 **Model Predicted Demand:** `{custom_pred:.1f} units/day` (Executed in real time)")
