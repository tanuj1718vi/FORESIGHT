"""Commercial pricing, promotional, and inventory operational features for Project FORESIGHT."""

import numpy as np
import pandas as pd


def create_business_features(
    df: pd.DataFrame,
    unit_price_col: str = "unit_price",
    price_col: str = "price",
    promo_col: str = "is_promoted",
    inventory_col: str = "inventory_level",
    rolling_demand_col: str = "rolling_mean_7",
) -> pd.DataFrame:
    """Generate pricing markdown, commercial promo, and operational inventory signals.

    Features generated:
    - discount_percentage: Markdown fraction relative to standard catalog price.
    - price_ratio: Realized price / base unit price.
    - is_promoted_int: Binary indicator (0/1).
    - inventory_ratio: Current physical on-hand stock relative to 7-day velocity.
    - days_of_inventory: Estimated stock coverage buffer at recent velocity.
    """
    data = df.copy()
    eps = 1e-5

    # Pricing & Discounts
    if unit_price_col in data.columns and price_col in data.columns:
        catalog_p = data[unit_price_col]
        realized_p = data[price_col]
        data["discount_percentage"] = np.maximum(
            0.0, (catalog_p - realized_p) / (catalog_p + eps)
        )
        data["price_ratio"] = (realized_p / (catalog_p + eps))
    else:
        data["discount_percentage"] = 0.0
        data["price_ratio"] = 1.0

    # Promotional Indicator
    if promo_col in data.columns:
        data["is_promoted_int"] = data[promo_col].astype(int)
    else:
        data["is_promoted_int"] = 0

    # Operational Inventory Signals
    if inventory_col in data.columns and rolling_demand_col in data.columns:
        inv = data[inventory_col]
        vel = data[rolling_demand_col]
        data["inventory_ratio"] = (inv / (vel + eps))
        data["days_of_inventory"] = np.clip(inv / (vel + eps), 0.0, 365.0)

    return data
