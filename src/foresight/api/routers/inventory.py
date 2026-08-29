"""Inventory optimization REST endpoints."""

from fastapi import APIRouter

from foresight.api.schemas.inventory import (
    BatchInventoryOptimizeRequest,
    BatchInventoryOptimizeResponse,
    InventoryOptimizeRequest,
    InventoryOptimizeResponse,
)
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory Optimization"])
_optimizer = InventoryOptimizer()


def _request_to_params(req: InventoryOptimizeRequest) -> InventoryParameters:
    return InventoryParameters(
        sku_id=req.sku_id,
        store_id=req.store_id,
        current_on_hand=req.current_on_hand,
        units_on_order=req.units_on_order,
        backorders=req.backorders,
        unit_cost=req.unit_cost,
        unit_price=req.unit_price,
        lead_time_days=req.lead_time_days,
        lead_time_std_days=req.lead_time_std_days,
        holding_cost_annual_rate=req.holding_cost_annual_rate,
        fixed_order_cost=req.fixed_order_cost,
        min_order_qty=req.min_order_qty,
        target_service_level=req.target_service_level,
        forecast_daily_demand_mean=req.forecast_daily_demand_mean,
        forecast_daily_demand_std=req.forecast_daily_demand_std,
    )


@router.post("/optimize", response_model=InventoryOptimizeResponse)
def optimize_single_sku(req: InventoryOptimizeRequest) -> InventoryOptimizeResponse:
    """Optimize safety stock, ROP, EOQ, and replenishment policy for an individual SKU."""
    params = _request_to_params(req)
    res = _optimizer.optimize_sku(params, method=req.method)

    return InventoryOptimizeResponse(
        sku_id=res.sku_id,
        store_id=res.store_id,
        net_stock=res.net_stock,
        safety_stock=res.safety_stock,
        reorder_point=res.reorder_point,
        economic_order_quantity=res.economic_order_quantity,
        recommended_order_quantity=res.recommended_order_quantity,
        days_of_supply=res.days_of_supply,
        stockout_risk_prob=res.stockout_risk_prob,
        health_status=res.health_status,
        recommended_action=res.recommended_action,
        working_capital_committed=res.working_capital_committed,
        total_annual_inventory_cost=res.total_annual_inventory_cost,
    )


@router.post("/optimize/batch", response_model=BatchInventoryOptimizeResponse)
def optimize_batch_skus(req: BatchInventoryOptimizeRequest) -> BatchInventoryOptimizeResponse:
    """Optimize replenishment policies across a collection of SKU-Store items."""
    results = []
    for item in req.items:
        params = _request_to_params(item)
        res = _optimizer.optimize_sku(params, method=item.method)
        results.append(
            InventoryOptimizeResponse(
                sku_id=res.sku_id,
                store_id=res.store_id,
                net_stock=res.net_stock,
                safety_stock=res.safety_stock,
                reorder_point=res.reorder_point,
                economic_order_quantity=res.economic_order_quantity,
                recommended_order_quantity=res.recommended_order_quantity,
                days_of_supply=res.days_of_supply,
                stockout_risk_prob=res.stockout_risk_prob,
                health_status=res.health_status,
                recommended_action=res.recommended_action,
                working_capital_committed=res.working_capital_committed,
                total_annual_inventory_cost=res.total_annual_inventory_cost,
            )
        )

    return BatchInventoryOptimizeResponse(total_items=len(results), results=results)
