"""What-If scenario simulator for supply chain stress testing and policy sensitivity."""

from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters
from foresight.risk.schema import ScenarioParameters, ScenarioSimulationResult


class WhatIfSimulator:
    """Stress-test engine simulating disruptions in lead time, demand velocity, and service targets."""

    def __init__(self, optimizer: InventoryOptimizer | None = None) -> None:
        self.optimizer = optimizer or InventoryOptimizer()

    def simulate_sku(
        self,
        params: InventoryParameters,
        scenario: ScenarioParameters,
    ) -> ScenarioSimulationResult:
        """Simulate the operational and financial impact of a scenario on an individual SKU."""
        # 1. Baseline Run
        baseline_res = self.optimizer.optimize_sku(params)

        # 2. Construct Perturbed Scenario Parameters
        new_lt = max(1.0, params.lead_time_days * scenario.lead_time_multiplier)
        new_demand_mean = max(0.1, params.forecast_daily_demand_mean * scenario.demand_multiplier)
        new_demand_std = max(0.05, params.forecast_daily_demand_std * scenario.demand_multiplier)
        new_service_level = scenario.target_service_level or params.target_service_level
        new_holding_rate = max(0.01, params.holding_cost_annual_rate * scenario.holding_cost_rate_multiplier)

        perturbed_params = InventoryParameters(
            sku_id=params.sku_id,
            store_id=params.store_id,
            current_on_hand=params.current_on_hand,
            units_on_order=params.units_on_order,
            backorders=params.backorders,
            unit_cost=params.unit_cost,
            unit_price=params.unit_price,
            lead_time_days=new_lt,
            lead_time_std_days=max(0.5, new_lt * 0.15),
            holding_cost_annual_rate=new_holding_rate,
            fixed_order_cost=params.fixed_order_cost,
            min_order_qty=params.min_order_qty,
            target_service_level=new_service_level,
            forecast_daily_demand_mean=new_demand_mean,
            forecast_daily_demand_std=new_demand_std,
        )

        # 3. Simulated Run
        sim_res = self.optimizer.optimize_sku(perturbed_params)

        # 4. Deltas
        delta_ss = sim_res.safety_stock - baseline_res.safety_stock
        delta_rop = sim_res.reorder_point - baseline_res.reorder_point
        delta_capital = sim_res.working_capital_committed - baseline_res.working_capital_committed
        delta_stockout = sim_res.stockout_risk_prob - baseline_res.stockout_risk_prob
        delta_cost = sim_res.total_annual_inventory_cost - baseline_res.total_annual_inventory_cost

        return ScenarioSimulationResult(
            scenario_name=scenario.scenario_name,
            sku_id=params.sku_id,
            store_id=params.store_id,
            baseline_safety_stock=baseline_res.safety_stock,
            simulated_safety_stock=sim_res.safety_stock,
            delta_safety_stock=round(delta_ss, 2),
            baseline_reorder_point=baseline_res.reorder_point,
            simulated_reorder_point=sim_res.reorder_point,
            delta_reorder_point=round(delta_rop, 2),
            baseline_working_capital=baseline_res.working_capital_committed,
            simulated_working_capital=sim_res.working_capital_committed,
            delta_working_capital=round(delta_capital, 2),
            baseline_stockout_risk=baseline_res.stockout_risk_prob,
            simulated_stockout_risk=sim_res.stockout_risk_prob,
            delta_stockout_risk=round(delta_stockout, 4),
            baseline_total_annual_cost=baseline_res.total_annual_inventory_cost,
            simulated_total_annual_cost=sim_res.total_annual_inventory_cost,
            delta_total_annual_cost=round(delta_cost, 2),
        )

    def simulate_portfolio(
        self,
        portfolio_params: list[InventoryParameters],
        scenario: ScenarioParameters,
    ) -> list[ScenarioSimulationResult]:
        """Simulate stress scenario across all nodes in the enterprise portfolio."""
        return [self.simulate_sku(p, scenario) for p in portfolio_params]
