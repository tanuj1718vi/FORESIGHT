"""High-fidelity, reproducible benchmark dataset generator for Project FORESIGHT."""

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from foresight.config.constants import RAW_DATA_DIR
from foresight.utils.logger import get_logger

logger = get_logger(__name__)

# Standard Category Catalog Definition
CATEGORY_CATALOG = {
    "Electronics": {
        "subcategories": ["Audio", "Wearables", "Accessories", "Peripherals"],
        "price_range": (25.0, 299.0),
        "margin_range": (0.30, 0.55),
        "lead_time_range": (10, 21),
        "moq_range": (20, 100),
        "seasonality_q4_boost": 1.6,
        "weekend_boost": 1.25,
    },
    "Apparel": {
        "subcategories": ["Tops", "Bottoms", "Footwear", "Outerwear"],
        "price_range": (19.0, 149.0),
        "margin_range": (0.45, 0.65),
        "lead_time_range": (14, 28),
        "moq_range": (50, 200),
        "seasonality_q4_boost": 1.4,
        "weekend_boost": 1.40,
    },
    "Home & Kitchen": {
        "subcategories": ["Appliances", "Cookware", "Storage", "Dining"],
        "price_range": (15.0, 189.0),
        "margin_range": (0.35, 0.50),
        "lead_time_range": (7, 18),
        "moq_range": (25, 150),
        "seasonality_q4_boost": 1.3,
        "weekend_boost": 1.30,
    },
    "Grocery": {
        "subcategories": ["Beverages", "Pantry", "Snacks", "Condiments"],
        "price_range": (4.5, 34.0),
        "margin_range": (0.20, 0.35),
        "lead_time_range": (3, 7),
        "moq_range": (100, 500),
        "seasonality_q4_boost": 1.15,
        "weekend_boost": 1.50,
    },
    "Health & Beauty": {
        "subcategories": ["Skincare", "Haircare", "Supplements", "Personal Care"],
        "price_range": (9.0, 79.0),
        "margin_range": (0.50, 0.70),
        "lead_time_range": (7, 14),
        "moq_range": (30, 120),
        "seasonality_q4_boost": 1.25,
        "weekend_boost": 1.20,
    },
}

STORES = [
    {"store_id": "STORE-001", "store_name": "Metro Flagship - North", "volume_scale": 1.35},
    {"store_id": "STORE-002", "store_name": "Suburban Center - West", "volume_scale": 1.05},
    {"store_id": "STORE-003", "store_name": "Downtown Express - Central", "volume_scale": 0.85},
    {"store_id": "STORE-004", "store_name": "Regional Hub - South", "volume_scale": 1.20},
    {"store_id": "STORE-005", "store_name": "E-Commerce Fulfillment Center", "volume_scale": 1.55},
]


def generate_product_catalog(num_skus: int = 50, seed: int = 42) -> pd.DataFrame:
    """Generate product master metadata catalog."""
    rng = np.random.default_rng(seed)
    categories = list(CATEGORY_CATALOG.keys())
    products = []

    for i in range(1, num_skus + 1):
        sku_id = f"SKU-{1000 + i}"
        cat_name = categories[(i - 1) % len(categories)]
        cat_info = CATEGORY_CATALOG[cat_name]

        subcat = rng.choice(cat_info["subcategories"])
        unit_price = round(float(rng.uniform(*cat_info["price_range"])), 2)
        margin = float(rng.uniform(*cat_info["margin_range"]))
        unit_cost = round(unit_price * (1.0 - margin), 2)
        lead_time = int(rng.integers(cat_info["lead_time_range"][0], cat_info["lead_time_range"][1] + 1))
        moq = int(rng.integers(cat_info["moq_range"][0], cat_info["moq_range"][1] + 1))

        # Assign demand archetype
        pattern_roll = rng.random()
        if pattern_roll < 0.55:
            pattern = "regular"
            base_rate = rng.uniform(8.0, 30.0)
        elif pattern_roll < 0.75:
            pattern = "seasonal"
            base_rate = rng.uniform(15.0, 45.0)
        elif pattern_roll < 0.90:
            pattern = "volatile"
            base_rate = rng.uniform(5.0, 25.0)
        else:
            pattern = "intermittent"
            base_rate = rng.uniform(1.0, 4.0)

        product_name = f"{cat_name} {subcat} Item {i}"

        products.append({
            "sku_id": sku_id,
            "product_name": product_name,
            "category": cat_name,
            "subcategory": subcat,
            "unit_price": unit_price,
            "unit_cost": unit_cost,
            "lead_time_days": lead_time,
            "min_order_qty": moq,
            "demand_pattern": pattern,
            "base_demand_rate": round(base_rate, 2),
            "holding_cost_annual_rate": 0.20,
        })

    return pd.DataFrame(products)


def generate_benchmark_dataset(
    num_skus: int = 50,
    start_date: date = date(2023, 1, 1),
    num_days: int = 730,
    seed: int = 42,
) -> dict[str, pd.DataFrame]:
    """Generate synthetic sales, product, and inventory dataset with realistic dynamics."""
    logger.info(f"Generating benchmark dataset with {num_skus} SKUs over {num_days} days (seed={seed})")
    rng = np.random.default_rng(seed)

    products_df = generate_product_catalog(num_skus=num_skus, seed=seed)
    date_range = [start_date + timedelta(days=i) for i in range(num_days)]

    sales_records: list[dict[str, Any]] = []
    inventory_records: list[dict[str, Any]] = []

    # Identify major calendar promo windows (e.g. Black Friday week, Mid-Summer Sale, Spring promo)
    promo_days = set()
    for yr in [2023, 2024]:
        # Spring Sale (Mid-April)
        for d in range(105, 112):
            promo_days.add(date(yr, 1, 1) + timedelta(days=d))
        # Summer Prime Sale (Mid-July)
        for d in range(195, 202):
            promo_days.add(date(yr, 1, 1) + timedelta(days=d))
        # Black Friday / Cyber Week (Late Nov)
        for d in range(324, 332):
            promo_days.add(date(yr, 1, 1) + timedelta(days=d))

    for _, store in pd.DataFrame(STORES).iterrows():
        store_id = store["store_id"]
        store_scale = store["volume_scale"]

        for _, prod in products_df.iterrows():
            sku_id = prod["sku_id"]
            cat_name = prod["category"]
            cat_info = CATEGORY_CATALOG[cat_name]
            base_rate = prod["base_demand_rate"]
            pattern = prod["demand_pattern"]
            lead_time = prod["lead_time_days"]
            moq = prod["min_order_qty"]
            regular_price = prod["unit_price"]

            # Initialize inventory state for this (store, sku)
            initial_stock = int(base_rate * store_scale * (lead_time + 14) * rng.uniform(0.9, 1.4))
            current_inventory = max(initial_stock, moq)
            reorder_point = int(base_rate * store_scale * lead_time * 1.5)
            pipeline_orders: list[dict[str, Any]] = []  # [{arrival_day_idx, quantity}]

            for day_idx, current_date in enumerate(date_range):
                # 1. Process arriving supplier orders
                arriving_qty = sum(
                    order["quantity"]
                    for order in pipeline_orders
                    if order["arrival_day_idx"] == day_idx
                )
                current_inventory += arriving_qty
                pipeline_orders = [o for o in pipeline_orders if o["arrival_day_idx"] > day_idx]

                # 2. Promotional status and pricing
                is_global_promo = current_date in promo_days
                # Occasional SKU-specific flash markdown (5% chance)
                is_flash_promo = rng.random() < 0.05
                is_promoted = is_global_promo or is_flash_promo

                if is_promoted:
                    discount_pct = rng.uniform(0.10, 0.30)
                    price = round(regular_price * (1.0 - discount_pct), 2)
                    promo_lift = 1.0 + (discount_pct * 2.5)  # Elasticity response
                else:
                    price = regular_price
                    promo_lift = 1.0

                # 3. Calendar & Trend Factors
                weekday = current_date.weekday()
                is_weekend = weekday in [5, 6]
                day_factor = cat_info["weekend_boost"] if is_weekend else 1.0

                # Annual Q4 seasonality
                month = current_date.month
                season_factor = cat_info["seasonality_q4_boost"] if month in [11, 12] else 1.0

                # Slight positive multi-year market trend (+5% per year)
                trend_factor = 1.0 + (day_idx / 730.0) * 0.08

                # Expected demand rate
                expected_demand = (
                    base_rate * store_scale * day_factor * season_factor * promo_lift * trend_factor
                )

                # 4. Generate actual realized demand
                if pattern == "intermittent":
                    # Zero-inflated Poisson
                    if rng.random() < 0.65:
                        demanded_qty = 0
                    else:
                        demanded_qty = int(rng.poisson(max(1.0, expected_demand * 2.5)))
                elif pattern == "volatile":
                    # Higher variance log-normal
                    noise = rng.lognormal(mean=0.0, sigma=0.45)
                    demanded_qty = max(0, int(round(expected_demand * noise)))
                else:
                    # Regular or seasonal Poisson with slight dispersion
                    demanded_qty = int(rng.poisson(max(0.5, expected_demand)))

                # 5. Inventory Fulfillment & Stockout Dynamics
                fulfilled_qty = min(current_inventory, demanded_qty)
                backorder_qty = demanded_qty - fulfilled_qty
                current_inventory -= fulfilled_qty

                # 6. Reorder Trigger Policy
                units_in_transit = sum(o["quantity"] for o in pipeline_orders)
                inventory_position = current_inventory + units_in_transit - backorder_qty

                if inventory_position <= reorder_point:
                    # Place reorder
                    order_size = max(moq, int(base_rate * store_scale * (lead_time + 10)))
                    arrival_day = day_idx + lead_time + int(rng.choice([0, 0, 1, -1]))
                    arrival_day = max(day_idx + 1, arrival_day)
                    pipeline_orders.append({
                        "arrival_day_idx": arrival_day,
                        "quantity": order_size,
                    })

                # Record observations
                sales_records.append({
                    "date": current_date,
                    "sku_id": sku_id,
                    "store_id": store_id,
                    "quantity": fulfilled_qty,
                    "price": price,
                    "is_promoted": is_promoted,
                })

                inventory_records.append({
                    "date": current_date,
                    "sku_id": sku_id,
                    "store_id": store_id,
                    "inventory_level": current_inventory,
                    "units_on_order": units_in_transit,
                    "backorders": backorder_qty,
                })

    sales_df = pd.DataFrame(sales_records)
    inventory_df = pd.DataFrame(inventory_records)

    logger.info(
        f"Generated {len(sales_df):,} sales records and {len(inventory_df):,} inventory records."
    )
    return {
        "sales": sales_df,
        "products": products_df,
        "inventory": inventory_df,
    }


def save_raw_datasets(
    datasets: dict[str, pd.DataFrame],
    target_dir: Path = RAW_DATA_DIR,
) -> dict[str, Path]:
    """Save generated datasets as raw CSV files."""
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: dict[str, Path] = {}

    for name, df in datasets.items():
        file_path = target_dir / f"{name}_raw.csv"
        df.to_csv(file_path, index=False)
        saved_paths[name] = file_path
        logger.info(f"Saved {name} to {file_path} ({len(df):,} rows)")

    return saved_paths


if __name__ == "__main__":
    data = generate_benchmark_dataset(num_skus=50, num_days=730, seed=42)
    save_raw_datasets(data)
