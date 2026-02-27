"""
Profit simulator router for OEM product profitability analysis.
Provides endpoints for calculating profit, saving simulations,
viewing history, and deleting simulations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import ProfitSimulation, get_db
from backend.services.profit_calculator import ProfitCalculator

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

calculator = ProfitCalculator()


# --- Pydantic Schemas ---


class CalculateRequest(BaseModel):
    """Request schema for profit calculation."""

    selling_price: float = Field(..., gt=0, description="Selling price in JPY")
    manufacturing_cost: float = Field(..., ge=0, description="Manufacturing cost per unit in JPY")
    packaging_cost: float = Field(..., ge=0, description="Packaging cost per unit in JPY")
    fba_fee: Optional[float] = Field(None, ge=0, description="FBA fee per unit in JPY (auto-calculated if not provided)")
    ad_rate: float = Field(15.0, ge=0, le=100, description="Advertising rate as % of revenue")
    target_sales: int = Field(..., gt=0, description="Target monthly unit sales")
    weight_kg: Optional[float] = Field(0.5, gt=0, description="Product weight in kg (for FBA fee calculation)")
    category: Optional[str] = Field("health", description="Product category")


class CalculateResponse(BaseModel):
    """Response schema for profit calculation."""

    selling_price: float
    manufacturing_cost: float
    packaging_cost: float
    fba_fee: float
    referral_fee: float
    ad_cost_per_unit: float
    total_cost_per_unit: float
    profit_per_unit: float
    profit_margin: float
    monthly_revenue: float
    monthly_profit: float
    annual_revenue: float
    annual_profit: float
    breakeven_units: int
    initial_investment: float
    roi: float
    payback_months: Optional[float] = None
    target_sales: int
    ad_rate: float
    cost_breakdown: Dict[str, float]
    fba_fee_detail: Optional[Dict[str, Any]] = None
    scenarios: Optional[Dict[str, Any]] = None


class SaveRequest(BaseModel):
    """Request schema for saving a simulation."""

    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    selling_price: float = Field(..., gt=0)
    manufacturing_cost: float = Field(..., ge=0)
    packaging_cost: float = Field(..., ge=0)
    fba_fee: float = Field(..., ge=0)
    ad_rate: float = Field(..., ge=0, le=100)
    target_sales: int = Field(..., gt=0)


class SaveResponse(BaseModel):
    """Response schema for saved simulation."""

    id: int
    product_name: str
    profit_per_unit: float
    profit_margin: float
    monthly_profit: float
    roi: float
    created_at: str
    message: str


class SimulationHistoryItem(BaseModel):
    """Schema for simulation history entry."""

    id: int
    product_name: str
    selling_price: float
    manufacturing_cost: float
    packaging_cost: float
    fba_fee: float
    ad_rate: float
    target_sales: int
    profit_per_unit: Optional[float] = None
    profit_margin: Optional[float] = None
    monthly_profit: Optional[float] = None
    roi: Optional[float] = None
    created_at: str


# --- Endpoints ---


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_profit(request: CalculateRequest) -> CalculateResponse:
    """
    Calculate profit metrics for an OEM product.
    Optionally auto-calculates FBA fees if not provided.
    Returns detailed breakdown including scenarios.
    """
    fba_fee = request.fba_fee
    fba_fee_detail: Optional[Dict[str, Any]] = None

    if fba_fee is None:
        # Auto-calculate FBA fee
        fba_detail = calculator.calculate_fba_fee(
            price=request.selling_price,
            weight_kg=request.weight_kg or 0.5,
            category=request.category or "health",
        )
        fba_fee = fba_detail["fba_fulfillment"]
        fba_fee_detail = fba_detail

    # Calculate base profit
    result = calculator.calculate_profit(
        selling_price=request.selling_price,
        manufacturing_cost=request.manufacturing_cost,
        packaging_cost=request.packaging_cost,
        fba_fee=fba_fee,
        ad_rate=request.ad_rate,
        target_sales=request.target_sales,
    )

    # Calculate scenarios
    base_params = {
        "selling_price": request.selling_price,
        "manufacturing_cost": request.manufacturing_cost,
        "packaging_cost": request.packaging_cost,
        "fba_fee": fba_fee,
        "ad_rate": request.ad_rate,
        "target_sales": request.target_sales,
    }
    scenarios = calculator.calculate_scenarios(base_params)

    return CalculateResponse(
        **result,
        fba_fee_detail=fba_fee_detail,
        scenarios=scenarios,
    )


@router.post("/save", response_model=SaveResponse)
async def save_simulation(
    request: SaveRequest, db: Session = Depends(get_db)
) -> SaveResponse:
    """Save a profit simulation to the database."""
    # Calculate profit metrics for saving
    result = calculator.calculate_profit(
        selling_price=request.selling_price,
        manufacturing_cost=request.manufacturing_cost,
        packaging_cost=request.packaging_cost,
        fba_fee=request.fba_fee,
        ad_rate=request.ad_rate,
        target_sales=request.target_sales,
    )

    simulation = ProfitSimulation(
        product_name=request.product_name,
        selling_price=request.selling_price,
        manufacturing_cost=request.manufacturing_cost,
        packaging_cost=request.packaging_cost,
        fba_fee=request.fba_fee,
        ad_rate=request.ad_rate,
        target_sales=request.target_sales,
        profit_per_unit=result["profit_per_unit"],
        profit_margin=result["profit_margin"],
        monthly_profit=result["monthly_profit"],
        roi=result["roi"],
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    return SaveResponse(
        id=simulation.id,
        product_name=simulation.product_name,
        profit_per_unit=simulation.profit_per_unit,
        profit_margin=simulation.profit_margin,
        monthly_profit=simulation.monthly_profit,
        roi=simulation.roi,
        created_at=simulation.created_at.isoformat(),
        message=f"Simulation '{request.product_name}' saved successfully.",
    )


@router.get("/history")
async def get_simulation_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get saved simulation history."""
    query = db.query(ProfitSimulation).order_by(
        ProfitSimulation.created_at.desc()
    )

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    items: List[Dict[str, Any]] = []
    for r in results:
        items.append({
            "id": r.id,
            "product_name": r.product_name,
            "selling_price": r.selling_price,
            "manufacturing_cost": r.manufacturing_cost,
            "packaging_cost": r.packaging_cost,
            "fba_fee": r.fba_fee,
            "ad_rate": r.ad_rate,
            "target_sales": r.target_sales,
            "profit_per_unit": r.profit_per_unit,
            "profit_margin": r.profit_margin,
            "monthly_profit": r.monthly_profit,
            "roi": r.roi,
            "created_at": r.created_at.isoformat(),
        })

    return {"total": total, "simulations": items}


@router.get("/{simulation_id}")
async def get_simulation(
    simulation_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get a specific saved simulation with full recalculated details."""
    simulation = (
        db.query(ProfitSimulation)
        .filter(ProfitSimulation.id == simulation_id)
        .first()
    )

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Recalculate full details
    result = calculator.calculate_profit(
        selling_price=simulation.selling_price,
        manufacturing_cost=simulation.manufacturing_cost,
        packaging_cost=simulation.packaging_cost,
        fba_fee=simulation.fba_fee,
        ad_rate=simulation.ad_rate,
        target_sales=simulation.target_sales,
    )

    base_params = {
        "selling_price": simulation.selling_price,
        "manufacturing_cost": simulation.manufacturing_cost,
        "packaging_cost": simulation.packaging_cost,
        "fba_fee": simulation.fba_fee,
        "ad_rate": simulation.ad_rate,
        "target_sales": simulation.target_sales,
    }
    scenarios = calculator.calculate_scenarios(base_params)

    return {
        "id": simulation.id,
        "product_name": simulation.product_name,
        "created_at": simulation.created_at.isoformat(),
        "calculation": result,
        "scenarios": scenarios,
    }


@router.delete("/{simulation_id}")
async def delete_simulation(
    simulation_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete a saved simulation."""
    simulation = (
        db.query(ProfitSimulation)
        .filter(ProfitSimulation.id == simulation_id)
        .first()
    )

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    product_name = simulation.product_name
    db.delete(simulation)
    db.commit()

    return {
        "status": "success",
        "message": f"Simulation '{product_name}' deleted successfully.",
    }
