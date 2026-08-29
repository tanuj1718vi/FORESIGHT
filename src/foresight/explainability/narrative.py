"""Natural language narrative generator converting mathematical SHAP attributions into commercial insights."""

from foresight.explainability.schema import DriverContribution


class NarrativeGenerator:
    """Translates local SHAP feature attributions into executive English demand drivers."""

    @staticmethod
    def generate_narrative(
        sku_id: str,
        base_value: float,
        predicted_value: float,
        positive_drivers: list[DriverContribution],
        negative_drivers: list[DriverContribution],
    ) -> str:
        """Construct executive narrative explaining why demand deviated from baseline."""
        diff = predicted_value - base_value
        pct_diff = (diff / max(0.1, base_value)) * 100.0

        if abs(diff) < 0.5:
            return (
                f"Demand for {sku_id} is forecast at {predicted_value:.1f} units, closely matching the historical "
                f"portfolio baseline of {base_value:.1f} units with neutral market drivers."
            )

        direction = "above" if diff > 0 else "below"
        lead_sentence = (
            f"Forecast for {sku_id} is {predicted_value:.1f} units ({abs(pct_diff):.1f}% {direction} baseline of "
            f"{base_value:.1f} units)."
        )

        pos_reasons = []
        for d in positive_drivers[:3]:
            pos_reasons.append(NarrativeGenerator._describe_driver(d, is_positive=True))

        neg_reasons = []
        for d in negative_drivers[:2]:
            neg_reasons.append(NarrativeGenerator._describe_driver(d, is_positive=False))

        details = []
        if pos_reasons:
            details.append(f"Primary upward drivers include: {', '.join(pos_reasons)}.")
        if neg_reasons:
            details.append(f"Partially dampened by: {', '.join(neg_reasons)}.")

        return f"{lead_sentence} {' '.join(details)}"

    @staticmethod
    def _describe_driver(driver: DriverContribution, is_positive: bool) -> str:
        """Generate human-friendly phrase for an individual feature contribution."""
        feat = driver.feature_name.lower()
        val = driver.feature_value
        units = abs(driver.attribution_units)

        if "promot" in feat or "discount" in feat:
            return f"active promotional discount (+{units:.1f} units)" if is_positive else f"lack of promotion (-{units:.1f} units)"
        elif "weekend" in feat or "day_of_week" in feat or "sin_day" in feat or "cos_day" in feat:
            return f"strong weekend shopping seasonality (+{units:.1f} units)" if is_positive else f"mid-week low seasonality (-{units:.1f} units)"
        elif "lag_1" in feat:
            return f"recent sales momentum from prior day (+{units:.1f} units)" if is_positive else f"sluggish prior day sales (-{units:.1f} units)"
        elif "lag_7" in feat or "rolling_mean_7" in feat:
            return f"elevated 7-day velocity (+{units:.1f} units)" if is_positive else f"subdued weekly demand rate (-{units:.1f} units)"
        elif "price" in feat:
            return f"favorable price point (+{units:.1f} units)" if is_positive else f"higher unit price resistance (-{units:.1f} units)"
        elif "growth" in feat or "trend" in feat or "momentum" in feat:
            return f"accelerating demand momentum (+{units:.1f} units)" if is_positive else f"decelerating trend (-{units:.1f} units)"
        else:
            prefix = "+" if is_positive else "-"
            return f"{driver.feature_name} ({prefix}{units:.1f} units)"
