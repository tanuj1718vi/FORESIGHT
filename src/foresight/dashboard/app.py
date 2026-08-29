"""Main Streamlit entrypoint for FORESIGHT Enterprise Demand & Inventory Intelligence Dashboard.

Ultra-modern 3D glassmorphic cybernetic interface with glowing animations.
"""

import streamlit as st

from foresight.dashboard.tabs.executive_overview import render_executive_overview_tab
from foresight.dashboard.tabs.governance import render_governance_tab
from foresight.dashboard.tabs.inventory_workbench import render_inventory_workbench_tab
from foresight.dashboard.tabs.risk_action_center import render_risk_action_center_tab
from foresight.dashboard.tabs.sku_explorer import render_sku_explorer_tab
from foresight.dashboard.tabs.what_if_simulator import render_what_if_simulator_tab


def main() -> None:
    """Main dashboard application renderer."""
    # Page Configuration
    st.set_page_config(
        page_title="FORESIGHT — Decision Intelligence Platform",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Ultra-Modern 3D Cyberpunk Dark Glassmorphism CSS & Keyframe Animations
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

        /* Base App Background & Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .main {
            background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(8, 14, 26, 1) 90%) !important;
            color: #f8fafc;
        }

        /* Animated Glowing Headers */
        .cyber-header {
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -0.02em;
            text-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
        }

        /* 3D Glass Cards & Glow Transitions */
        .glow-card-3d:hover {
            transform: perspective(1000px) translateY(-6px) scale(1.015) !important;
            box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.7), 0 0 25px 2px rgba(0, 240, 255, 0.35) !important;
            border-color: rgba(0, 240, 255, 0.8) !important;
        }

        /* Cyber Pulse Animation */
        @keyframes pulse-live {
            0% {
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
            }
        }

        .live-dot {
            width: 10px;
            height: 10px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            animation: pulse-live 2s infinite;
        }

        /* Streamlit Tabs 3D Redesign */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: rgba(15, 23, 42, 0.6);
            padding: 8px 12px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            white-space: pre-wrap;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 10px;
            padding: 10px 18px;
            color: #94a3b8;
            font-weight: 600;
            font-size: 0.92rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.25s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.3);
            transform: translateY(-2px);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%) !important;
            color: #38bdf8 !important;
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.35), inset 0 0 10px rgba(56, 189, 248, 0.15);
            font-weight: 700 !important;
        }

        /* Glowing Buttons & Interactivity */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
            color: #ffffff;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        div.stButton > button:first-child:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6), 0 0 15px rgba(14, 165, 233, 0.8);
            border: none;
            color: #ffffff;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: rgba(10, 15, 30, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
        }

        /* Dataframe Glow Container */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load dynamic metadata
    from foresight.dashboard.data_provider import get_dashboard_metadata
    meta = get_dashboard_metadata()

    # Sidebar Branding & Live Telemetry
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; filter: drop-shadow(0 0 10px #38bdf8);">🔮</div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">FORESIGHT</div>
                        <div style="font-size: 0.75rem; color: #38bdf8; font-weight: 600;">ENTERPRISE AI PLATFORM</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 8px;
                padding: 8px 12px;
                margin: 10px 0 16px 0;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span class="live-dot"></span>
                <span style="font-size: 0.80rem; font-weight: 600; color: #34d399;">LIVE INFERENCE ACTIVE</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### 🌐 Enterprise Scope")
        st.markdown(f"- 📦 **Monitored SKUs:** `{meta['sku_count']} SKUs`")
        st.markdown(f"- 🏬 **Store Network:** `{meta['store_count']} Locations`")
        st.markdown(f"- 🔄 **Active Nodes:** `{meta['node_count']} SKU-Store Pairs`")
        st.markdown(f"- 🏆 **Champion Model:** `{meta['model_name']}`")
        st.markdown(f"- 🎯 **Empirical WAPE:** `{meta['wape_str']}`")
        st.markdown("- 🛡️ **Uncertainty:** `Combined (Lead-Time + Demand)`")
        
        st.markdown("---")
        st.markdown("### ⚡ System Status")
        st.markdown(f"🔒 **Target Service SLA:** `{meta['target_sla']}`")
        st.markdown(f"📡 **Database:** `SQLAlchemy SQLite Layer`")
        st.markdown(f"🚀 **Release:** `{meta['version']}`")

    # Header Hero Banner with 3D Holographic Visual
    st.markdown(
        """
        <div style="
            position: relative;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid #00f0ff;
            border-radius: 16px;
            padding: 22px 28px;
            margin-bottom: 24px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(0, 240, 255, 0.15);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1 class="cyber-header" style="margin: 0; font-size: 2.2rem;">🔮 FORESIGHT Intelligence Command Center</h1>
                    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px; font-weight: 500;">
                        Real-time AI Demand Forecasting, Multi-Echelon Policy Optimization, and Prescriptive Exposure Management
                    </div>
                </div>
                <div style="
                    background: rgba(0, 240, 255, 0.1);
                    border: 1px solid #00f0ff;
                    border-radius: 10px;
                    padding: 8px 16px;
                    color: #00f0ff;
                    font-weight: 700;
                    font-size: 0.85rem;
                    box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
                ">
                    ⚡ MULTI-ECHELON AUTONOMY
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tab Navigation
    tabs = st.tabs([
        "📊 Executive Overview",
        "🔍 SKU & Forecast Explorer",
        "⚙️ Inventory Workbench",
        "🎯 Risk & Action Center",
        "🧪 What-If Simulator",
        "🛡️ Governance & Quality",
    ])

    with tabs[0]:
        render_executive_overview_tab()

    with tabs[1]:
        render_sku_explorer_tab()

    with tabs[2]:
        render_inventory_workbench_tab()

    with tabs[3]:
        render_risk_action_center_tab()

    with tabs[4]:
        render_what_if_simulator_tab()

    with tabs[5]:
        render_governance_tab()


if __name__ == "__main__":
    main()
