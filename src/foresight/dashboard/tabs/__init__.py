"""Dashboard tab modules."""

from foresight.dashboard.tabs.executive_overview import render_executive_overview_tab
from foresight.dashboard.tabs.governance import render_governance_tab
from foresight.dashboard.tabs.inventory_workbench import render_inventory_workbench_tab
from foresight.dashboard.tabs.risk_action_center import render_risk_action_center_tab
from foresight.dashboard.tabs.sku_explorer import render_sku_explorer_tab
from foresight.dashboard.tabs.what_if_simulator import render_what_if_simulator_tab

__all__ = [
    "render_executive_overview_tab",
    "render_sku_explorer_tab",
    "render_inventory_workbench_tab",
    "render_risk_action_center_tab",
    "render_what_if_simulator_tab",
    "render_governance_tab",
]
