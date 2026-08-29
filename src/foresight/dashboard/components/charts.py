"""Ultra-modern 3D, holographic, and high-graphics Plotly charts for Project FORESIGHT."""

from typing import Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_dark_cyber_layout(title: str, height: int = 450) -> dict[str, Any]:
    """Return unified cyberpunk dark glassmorphism layout configuration for Plotly figures."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Inter, sans-serif", size=15, color="#f8fafc"),
            x=0.02,
            y=0.96,
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        height=height,
        margin=dict(l=40, r=40, t=55, b=40),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.07)",
            zerolinecolor="rgba(255, 255, 255, 0.15)",
            showline=True,
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color="#94a3b8", size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.07)",
            zerolinecolor="rgba(255, 255, 255, 0.15)",
            showline=True,
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color="#94a3b8", size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(color="#cbd5e1", size=11),
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#00f0ff",
            font=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
        ),
    )


def plot_forecast_with_intervals(
    dates_hist: list[Any],
    y_hist: list[float],
    dates_fc: list[Any],
    y_fc: list[float],
    y_p10: list[float] | None = None,
    y_p90: list[float] | None = None,
    sku_id: str = "SKU",
    store_id: str = "STORE",
) -> go.Figure:
    """Render demand forecast with glowing P10-P90 prediction interval ribbon and cyber-styled traces."""
    fig = go.Figure()

    # 1. Historical Actuals (Cyan Neon Trace)
    fig.add_trace(
        go.Scatter(
            x=dates_hist,
            y=y_hist,
            name="Historical Actual Demand",
            line=dict(color="#00f0ff", width=2.5),
            mode="lines",
            hoverinfo="x+y+name",
        )
    )

    # 2. Prediction Interval Ribbon (Electric Violet Glow)
    if y_p10 is not None and y_p90 is not None:
        fig.add_trace(
            go.Scatter(
                x=dates_fc,
                y=y_p90,
                name="P90 (Upper Bound)",
                line=dict(color="rgba(168, 85, 247, 0.3)", width=0),
                mode="lines",
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates_fc,
                y=y_p10,
                name="80% Prediction Interval (P10 - P90)",
                line=dict(color="rgba(168, 85, 247, 0.3)", width=0),
                fill="tonexty",
                fillcolor="rgba(168, 85, 247, 0.22)",
                mode="lines",
                hoverinfo="skip",
            )
        )

    # 3. Point Forecast (Amber Laser)
    fig.add_trace(
        go.Scatter(
            x=dates_fc,
            y=y_fc,
            name="Point Forecast (Champion XGBoost)",
            line=dict(color="#fbbf24", width=3, dash="solid"),
            mode="lines+markers",
            marker=dict(size=5, color="#fbbf24", symbol="diamond", line=dict(color="#000000", width=1)),
            hoverinfo="x+y+name",
        )
    )

    layout = get_dark_cyber_layout(f"🔮 Demand Forecast Trajectory: {sku_id} @ {store_id}", height=460)
    fig.update_layout(**layout)
    fig.update_xaxes(title_text="Date Timeline")
    fig.update_yaxes(title_text="Units Sold / Day")

    return fig


def plot_portfolio_health_donut(health_counts: dict[str, int]) -> go.Figure:
    """Render 3D-styled Neon Donut chart of inventory health positions."""
    color_map = {
        "OPTIMAL": "#10b981",
        "UNDERSTOCKED": "#f59e0b",
        "STOCKOUT_IMMINENT": "#ff0055",
        "OVERSTOCKED": "#a855f7",
        "CRITICAL_EXCESS": "#ec4899",
    }

    labels = list(health_counts.keys())
    values = list(health_counts.values())
    colors = [color_map.get(k, "#64748b") for k in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(
                    colors=colors,
                    line=dict(color="#0f172a", width=3),
                ),
                textinfo="label+percent",
                textfont=dict(color="#ffffff", size=11, family="Inter, sans-serif"),
                hoverinfo="label+value+percent",
                pull=[0.05 if "STOCKOUT" in l or "CRITICAL" in l else 0 for l in labels],
            )
        ]
    )

    # Center text KPI
    total_nodes = sum(values)
    fig.add_annotation(
        text=f"<b>{total_nodes}</b><br><span style='font-size:11px;color:#94a3b8;'>NODES</span>",
        x=0.5,
        y=0.5,
        font=dict(size=20, color="#ffffff", family="Inter, sans-serif"),
        showarrow=False,
    )

    layout = get_dark_cyber_layout("⚡ Portfolio Multi-Echelon Health Distribution", height=380)
    fig.update_layout(**layout)
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )

    return fig


def plot_3d_risk_landscape(risk_df: pd.DataFrame) -> go.Figure:
    """Render interactive 3D Risk Terrain scatter plot in 3D Euclidean space.

    Axes:
        X: Days of Supply (Inventory Runway)
        Y: Stockout Probability (0.0 to 1.0)
        Z: Total Financial Exposure ($ Exposure)
    """
    color_map = {
        "CRITICAL": "#ff0055",
        "HIGH": "#f97316",
        "MEDIUM": "#fbbf24",
        "LOW": "#10b981",
    }

    colors = [color_map.get(str(r), "#38bdf8") for r in risk_df.get("risk_level", ["LOW"] * len(risk_df))]

    # Cap days of supply for clean 3D viewing
    clean_dos = np.clip(risk_df.get("days_of_supply", [10] * len(risk_df)), 0, 90)
    stockout_p = risk_df.get("stockout_probability", [0.1] * len(risk_df))
    exposure = risk_df.get("total_financial_exposure", [100] * len(risk_df))

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=clean_dos,
                y=stockout_p,
                z=exposure,
                mode="markers",
                marker=dict(
                    size=6,
                    color=exposure,
                    colorscale="Viridis",
                    opacity=0.85,
                    colorbar=dict(
                        title=dict(text="Financial Exposure ($)", font=dict(color="#cbd5e1", size=11)),
                        thickness=12,
                        len=0.7,
                        tickfont=dict(color="#94a3b8"),
                    ),
                    line=dict(color="rgba(255,255,255,0.4)", width=1),
                ),
                text=[
                    f"SKU: {sku}<br>Store: {store}<br>Exposure: ${exp:,.2f}<br>Stockout Prob: {p:.1%}<br>Runway: {d:.1f}d"
                    for sku, store, exp, p, d in zip(
                        risk_df.get("sku_id", []),
                        risk_df.get("store_id", []),
                        exposure,
                        stockout_p,
                        clean_dos,
                    )
                ],
                hoverinfo="text",
                name="Inventory Nodes",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="<b>🌐 3D Multi-Echelon Risk Landscape & Financial Exposure Topography</b>",
            font=dict(family="Inter, sans-serif", size=15, color="#f8fafc"),
            x=0.02,
            y=0.96,
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        scene=dict(
            xaxis=dict(
                title=dict(
                    text="Days of Supply (Runway)",
                    font=dict(color="#38bdf8"),
                ),
                backgroundcolor="rgba(15, 23, 42, 0.6)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                showbackground=True,
                tickfont=dict(color="#94a3b8"),
            ),
            yaxis=dict(
                title=dict(
                    text="Stockout Risk Probability",
                    font=dict(color="#a855f7"),
                ),
                backgroundcolor="rgba(15, 23, 42, 0.6)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                showbackground=True,
                tickfont=dict(color="#94a3b8"),
            ),
            zaxis=dict(
                title=dict(
                    text="Financial Exposure ($)",
                    font=dict(color="#10b981"),
                ),
                backgroundcolor="rgba(15, 23, 42, 0.6)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                showbackground=True,
                tickfont=dict(color="#94a3b8"),
            ),
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.2),
            ),
        ),
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


def plot_3d_echelon_network(lateral_df: pd.DataFrame) -> go.Figure:
    """Render 3D Spatial Network Graph of Multi-Store Lateral Transfers & Fulfillment Nodes."""
    store_coords = {
        "STORE-001": (10, 20, 5),
        "STORE-002": (35, 15, 8),
        "STORE-003": (25, 45, 12),
        "STORE-004": (50, 40, 6),
        "STORE-005": (15, 60, 10),
        "CENTRAL_DC": (28, 35, 25),
    }

    fig = go.Figure()

    # 1. Add Store Nodes
    store_names = list(store_coords.keys())
    sx = [store_coords[k][0] for k in store_names]
    sy = [store_coords[k][1] for k in store_names]
    sz = [store_coords[k][2] for k in store_names]

    fig.add_trace(
        go.Scatter3d(
            x=sx,
            y=sy,
            z=sz,
            mode="markers+text",
            marker=dict(
                size=[14 if k == "CENTRAL_DC" else 10 for k in store_names],
                color=["#00f0ff" if k == "CENTRAL_DC" else "#a855f7" for k in store_names],
                line=dict(color="#ffffff", width=2),
                opacity=0.9,
            ),
            text=store_names,
            textposition="top center",
            textfont=dict(color="#ffffff", size=11),
            name="Echelon Hubs",
            hoverinfo="text",
        )
    )

    # 2. Add Lateral Transfer Arc Lines
    for _, row in lateral_df.iterrows():
        donor = str(row.get("donor_store_id", "STORE-001"))
        dest = str(row.get("store_id", "STORE-002"))
        if donor in store_coords and dest in store_coords:
            c1 = store_coords[donor]
            c2 = store_coords[dest]
            fig.add_trace(
                go.Scatter3d(
                    x=[c1[0], c2[0]],
                    y=[c1[1], c2[1]],
                    z=[c1[2], c2[2]],
                    mode="lines",
                    line=dict(color="#10b981", width=5),
                    name=f"{donor} ➔ {dest}",
                    hoverinfo="text",
                    text=f"Transfer {row.get('recommended_quantity', 0):.0f} units of {row.get('sku_id', '')} (Impact: ${row.get('expected_financial_impact', 0):,.2f})",
                )
            )

    fig.update_layout(
        title=dict(
            text="<b>⚡ 3D Multi-Echelon Intra-Network Transfer Matrix</b>",
            font=dict(family="Inter, sans-serif", size=15, color="#f8fafc"),
            x=0.02,
            y=0.96,
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        scene=dict(
            xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3)),
        ),
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
    )

    return fig


def plot_eoq_cost_curves(
    annual_demand: float,
    order_cost: float,
    unit_cost: float,
    holding_rate: float,
    optimal_eoq: float,
) -> go.Figure:
    """Render Wilson EOQ annual cost trade-off curves with cyber styling."""
    q_max = max(100.0, optimal_eoq * 2.5)
    q_vals = np.linspace(max(1.0, optimal_eoq * 0.1), q_max, 150)

    h = max(0.01, unit_cost * holding_rate)
    holding_costs = (q_vals / 2.0) * h
    ordering_costs = (annual_demand / q_vals) * order_cost
    total_costs = holding_costs + ordering_costs

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=q_vals, y=holding_costs, name="Annual Holding Cost (Q/2 * H)", line=dict(color="#00f0ff", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=q_vals, y=ordering_costs, name="Annual Ordering Cost (D/Q * S)", line=dict(color="#ff0055", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=q_vals, y=total_costs, name="Total Annual Carrying Cost", line=dict(color="#10b981", width=3.5)))

    # Optimal EOQ Marker
    opt_cost = ((optimal_eoq / 2.0) * h) + ((annual_demand / optimal_eoq) * order_cost)
    fig.add_vline(x=optimal_eoq, line_dash="dash", line_color="#fbbf24", annotation_text=f"EOQ = {optimal_eoq:.0f} units")
    fig.add_trace(go.Scatter(x=[optimal_eoq], y=[opt_cost], mode="markers", marker=dict(size=11, color="#fbbf24", symbol="diamond"), name=f"Optimal EOQ (${opt_cost:,.0f}/yr)"))

    layout = get_dark_cyber_layout(f"⚙️ Wilson EOQ Cost Optimization Curve (Annual Demand: {annual_demand:,.0f} units)", height=420)
    fig.update_layout(**layout)
    fig.update_xaxes(title_text="Order Quantity (Q units)")
    fig.update_yaxes(title_text="Annual Cost ($/year)")

    return fig


def plot_risk_matrix_scatter(risk_df: pd.DataFrame) -> go.Figure:
    """Render risk exposure scatter matrix with high-contrast glowing tiers."""
    fig = px.scatter(
        risk_df,
        x="days_of_supply",
        y="stockout_probability",
        size="lost_margin_risk",
        color="risk_level",
        color_discrete_map={
            "CRITICAL": "#ff0055",
            "HIGH": "#f97316",
            "MEDIUM": "#fbbf24",
            "LOW": "#10b981",
        },
        hover_data=["sku_id", "store_id", "composite_risk_score", "total_financial_exposure"],
        title="🎯 Enterprise Inventory Risk Matrix (Stockout Prob vs Days of Supply)",
        template="plotly_dark",
    )

    layout = get_dark_cyber_layout("🎯 Enterprise Inventory Risk Matrix (Stockout Prob vs Days of Supply)", height=440)
    fig.update_layout(**layout)
    fig.update_xaxes(title_text="Days of Supply (Runway)")
    fig.update_yaxes(title_text="Stockout Risk Probability")

    return fig
