"""
Profit calculator for OEM product simulations.
Handles profit calculation, FBA fee estimation for Japan marketplace,
and scenario analysis (optimistic/neutral/pessimistic).
"""

import math
from typing import Any, Dict, List


class ProfitCalculator:
    """Calculator for OEM product profitability analysis."""

    # Amazon.co.jp FBA fee structure (approximate, as of 2024)
    # Small standard size: up to 25x18x5cm, up to 250g
    FBA_FEES_JP: Dict[str, Dict[str, float]] = {
        "small_standard": {
            "pick_pack": 288,       # JPY per unit
            "weight_base": 10,      # JPY per 100g
            "storage_per_cm3": 5.16, # JPY per 1000 cm3/month (Oct-Dec higher)
        },
        "standard": {
            "pick_pack": 434,
            "weight_base": 16,
            "storage_per_cm3": 5.16,
        },
        "large_standard": {
            "pick_pack": 514,
            "weight_base": 40,
            "storage_per_cm3": 5.16,
        },
        "oversize": {
            "pick_pack": 589,
            "weight_base": 52,
            "storage_per_cm3": 3.10,
        },
    }

    # Referral fee rates by category for Amazon.co.jp
    REFERRAL_RATES: Dict[str, float] = {
        "health": 0.10,        # ドラッグストア・ビューティー
        "supplement": 0.10,
        "beauty": 0.10,
        "food": 0.10,
        "baby": 0.08,
        "electronics": 0.08,
        "general": 0.15,
    }

    def calculate_profit(
        self,
        selling_price: float,
        manufacturing_cost: float,
        packaging_cost: float,
        fba_fee: float,
        ad_rate: float,
        target_sales: int,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive profit metrics.

        Args:
            selling_price: Retail price in JPY
            manufacturing_cost: Cost per unit from OEM factory in JPY
            packaging_cost: Packaging cost per unit in JPY
            fba_fee: FBA fulfillment fee per unit in JPY
            ad_rate: Advertising spend as a percentage of revenue (0-100)
            target_sales: Target monthly unit sales

        Returns:
            Dict with profit metrics including per-unit, monthly, annual,
            breakeven, ROI, and payback period.
        """
        # Revenue
        monthly_revenue: float = selling_price * target_sales
        annual_revenue: float = monthly_revenue * 12

        # Ad spend per unit
        ad_cost_per_unit: float = selling_price * (ad_rate / 100)

        # Amazon referral fee (approximately 10% for health category)
        referral_fee: float = selling_price * 0.10

        # Total cost per unit
        total_cost_per_unit: float = (
            manufacturing_cost
            + packaging_cost
            + fba_fee
            + ad_cost_per_unit
            + referral_fee
        )

        # Profit per unit
        profit_per_unit: float = selling_price - total_cost_per_unit

        # Profit margin
        profit_margin: float = (
            (profit_per_unit / selling_price * 100) if selling_price > 0 else 0
        )

        # Monthly and annual profit
        monthly_profit: float = profit_per_unit * target_sales
        annual_profit: float = monthly_profit * 12

        # Breakeven analysis
        fixed_monthly_costs: float = 0  # Can be extended with fixed costs
        breakeven_units: int = (
            math.ceil(fixed_monthly_costs / profit_per_unit)
            if profit_per_unit > 0
            else 0
        )

        # Initial investment (first lot manufacturing + packaging)
        initial_investment: float = (
            (manufacturing_cost + packaging_cost) * target_sales
        )

        # ROI (Return on Investment)
        roi: float = (
            (monthly_profit / initial_investment * 100)
            if initial_investment > 0
            else 0
        )

        # Payback period in months
        payback_months: float = (
            initial_investment / monthly_profit
            if monthly_profit > 0
            else float("inf")
        )

        return {
            "selling_price": selling_price,
            "manufacturing_cost": manufacturing_cost,
            "packaging_cost": packaging_cost,
            "fba_fee": fba_fee,
            "referral_fee": referral_fee,
            "ad_cost_per_unit": ad_cost_per_unit,
            "total_cost_per_unit": round(total_cost_per_unit, 0),
            "profit_per_unit": round(profit_per_unit, 0),
            "profit_margin": round(profit_margin, 1),
            "monthly_revenue": round(monthly_revenue, 0),
            "monthly_profit": round(monthly_profit, 0),
            "annual_revenue": round(annual_revenue, 0),
            "annual_profit": round(annual_profit, 0),
            "breakeven_units": breakeven_units,
            "initial_investment": round(initial_investment, 0),
            "roi": round(roi, 1),
            "payback_months": round(payback_months, 1)
            if payback_months != float("inf")
            else None,
            "target_sales": target_sales,
            "ad_rate": ad_rate,
            "cost_breakdown": {
                "manufacturing": round(manufacturing_cost, 0),
                "packaging": round(packaging_cost, 0),
                "fba": round(fba_fee, 0),
                "referral": round(referral_fee, 0),
                "advertising": round(ad_cost_per_unit, 0),
            },
        }

    def calculate_fba_fee(
        self,
        price: float,
        weight_kg: float = 0.5,
        category: str = "health",
    ) -> Dict[str, Any]:
        """
        Auto-calculate FBA fees for Amazon.co.jp marketplace.

        Args:
            price: Product selling price in JPY
            weight_kg: Product weight in kilograms
            category: Product category for referral fee calculation

        Returns:
            Dict with fee breakdown
        """
        weight_g = weight_kg * 1000

        # Determine size tier based on weight
        if weight_g <= 250:
            tier = "small_standard"
        elif weight_g <= 1000:
            tier = "standard"
        elif weight_g <= 9000:
            tier = "large_standard"
        else:
            tier = "oversize"

        fee_config = self.FBA_FEES_JP[tier]

        # Pick & pack fee
        pick_pack: float = fee_config["pick_pack"]

        # Weight handling fee
        weight_fee: float = fee_config["weight_base"] * (weight_g / 100)

        # Monthly storage fee (estimated for standard packaging)
        # Assume typical supplement box: 15x10x5 cm = 750 cm3
        volume_cm3: float = 750
        storage_fee: float = fee_config["storage_per_cm3"] * (volume_cm3 / 1000)

        # Referral fee
        referral_rate: float = self.REFERRAL_RATES.get(
            category.lower(), self.REFERRAL_RATES["general"]
        )
        referral_fee: float = price * referral_rate

        # Total FBA fee (excluding referral, which is separate)
        fba_fulfillment: float = pick_pack + weight_fee + storage_fee
        total_fee: float = fba_fulfillment + referral_fee

        return {
            "size_tier": tier,
            "pick_pack": round(pick_pack, 0),
            "weight_fee": round(weight_fee, 0),
            "storage_fee": round(storage_fee, 0),
            "fba_fulfillment": round(fba_fulfillment, 0),
            "referral_fee": round(referral_fee, 0),
            "referral_rate": referral_rate,
            "total_fee": round(total_fee, 0),
        }

    def calculate_scenarios(
        self, base_params: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate optimistic, neutral, and pessimistic scenarios.

        Args:
            base_params: Dict with selling_price, manufacturing_cost,
                        packaging_cost, fba_fee, ad_rate, target_sales

        Returns:
            Dict with three scenario results: optimistic (1.5x sales),
            neutral (1.0x sales), pessimistic (0.5x sales)
        """
        base_sales: int = base_params.get("target_sales", 100)

        scenarios: Dict[str, Dict[str, Any]] = {}

        # Optimistic scenario: 1.5x target sales
        optimistic_params = {**base_params, "target_sales": int(base_sales * 1.5)}
        scenarios["optimistic"] = {
            "label": "楽観シナリオ (売上1.5倍)",
            "multiplier": 1.5,
            **self.calculate_profit(**optimistic_params),
        }

        # Neutral scenario: base target sales
        neutral_params = {**base_params, "target_sales": base_sales}
        scenarios["neutral"] = {
            "label": "中立シナリオ (基本)",
            "multiplier": 1.0,
            **self.calculate_profit(**neutral_params),
        }

        # Pessimistic scenario: 0.5x target sales
        pessimistic_params = {**base_params, "target_sales": max(1, int(base_sales * 0.5))}
        scenarios["pessimistic"] = {
            "label": "悲観シナリオ (売上0.5倍)",
            "multiplier": 0.5,
            **self.calculate_profit(**pessimistic_params),
        }

        return scenarios
