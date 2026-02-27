"""Profit calculation logic for OEM products."""

import math


def calculate_fba_fee(price: int, weight_kg: float = 0.5, category: str = "health") -> int:
    """
    Calculate Amazon FBA fee for Japan marketplace.
    Simplified estimation based on price and weight.
    """
    # Base referral fee (typically 8-15% for health/beauty in Japan)
    referral_rates = {
        "health": 0.10,
        "beauty": 0.10,
        "supplement": 0.10,
        "bath": 0.10,
        "general": 0.15,
    }
    referral_rate = referral_rates.get(category, 0.10)
    referral_fee = int(price * referral_rate)

    # FBA fulfillment fee based on weight (simplified)
    if weight_kg <= 0.25:
        fulfillment_fee = 288
    elif weight_kg <= 0.5:
        fulfillment_fee = 318
    elif weight_kg <= 1.0:
        fulfillment_fee = 381
    elif weight_kg <= 2.0:
        fulfillment_fee = 434
    else:
        fulfillment_fee = 434 + int((weight_kg - 2.0) * 40)

    # Monthly storage fee (estimated per unit)
    storage_fee = 30

    return referral_fee + fulfillment_fee + storage_fee


def calculate_profit(
    selling_price: int,
    manufacturing_cost: int,
    packaging_cost: int,
    fba_fee: int,
    ad_rate: float,
    target_sales: int,
) -> dict:
    """
    Calculate profit metrics for an OEM product.

    Args:
        selling_price: Retail price in JPY
        manufacturing_cost: Manufacturing cost per unit in JPY
        packaging_cost: Packaging/materials cost per unit in JPY
        fba_fee: FBA fee per unit in JPY
        ad_rate: Advertising spend as percentage of revenue (e.g., 15 for 15%)
        target_sales: Target monthly unit sales

    Returns:
        Dictionary with profit metrics
    """
    ad_cost_per_unit = int(selling_price * (ad_rate / 100))
    total_cost = manufacturing_cost + packaging_cost + fba_fee + ad_cost_per_unit

    profit_per_unit = selling_price - total_cost
    profit_margin = profit_per_unit / selling_price if selling_price > 0 else 0

    monthly_revenue = selling_price * target_sales
    monthly_profit = profit_per_unit * target_sales
    annual_profit = monthly_profit * 12

    # Breakeven: fixed costs / profit per unit
    # Assume initial investment = manufacturing_cost * min_lot (1000 units)
    initial_investment = manufacturing_cost * max(target_sales, 1000) + packaging_cost * max(target_sales, 1000)

    if profit_per_unit > 0:
        breakeven_units = math.ceil(initial_investment / profit_per_unit)
        roi = annual_profit / initial_investment if initial_investment > 0 else 0
        payback_months = initial_investment / monthly_profit if monthly_profit > 0 else float("inf")
    else:
        breakeven_units = 0
        roi = 0
        payback_months = float("inf")

    # Cap payback_months for display
    if payback_months == float("inf") or payback_months > 999:
        payback_months = 999.0

    return {
        "profit_per_unit": profit_per_unit,
        "profit_margin": round(profit_margin, 4),
        "monthly_profit": monthly_profit,
        "annual_profit": annual_profit,
        "breakeven_units": breakeven_units,
        "roi": round(roi, 4),
        "payback_months": round(payback_months, 1),
    }


def calculate_scenarios(
    selling_price: int,
    manufacturing_cost: int,
    packaging_cost: int,
    fba_fee: int,
    ad_rate: float,
    target_sales: int,
) -> dict:
    """
    Calculate optimistic/neutral/pessimistic scenarios.
    Optimistic: 1.5x target sales
    Neutral: 1.0x target sales
    Pessimistic: 0.5x target sales
    """
    scenarios = {}
    multipliers = {
        "optimistic": 1.5,
        "neutral": 1.0,
        "pessimistic": 0.5,
    }

    for name, multiplier in multipliers.items():
        adjusted_sales = max(1, int(target_sales * multiplier))
        result = calculate_profit(
            selling_price=selling_price,
            manufacturing_cost=manufacturing_cost,
            packaging_cost=packaging_cost,
            fba_fee=fba_fee,
            ad_rate=ad_rate,
            target_sales=adjusted_sales,
        )
        scenarios[name] = {
            "target_sales": adjusted_sales,
            "monthly_profit": result["monthly_profit"],
            "annual_profit": result["annual_profit"],
            "roi": result["roi"],
        }

    return scenarios
