"""Profit simulator router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db, ProfitSimulation
from backend.services.profit_calculator import (
    calculate_profit,
    calculate_scenarios,
    calculate_fba_fee,
)

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


class CalculateRequest(BaseModel):
    product_name: str = ""
    selling_price: int
    manufacturing_cost: int
    packaging_cost: int
    fba_fee: int
    ad_rate: float
    target_sales: int


class SaveRequest(BaseModel):
    product_name: str = ""
    selling_price: int
    manufacturing_cost: int
    packaging_cost: int
    fba_fee: int
    ad_rate: float
    target_sales: int
    profit_per_unit: int
    profit_margin: float
    monthly_profit: int
    annual_profit: Optional[int] = None
    breakeven_units: Optional[int] = None
    roi: float
    payback_months: Optional[float] = None
    scenarios: Optional[dict] = None


@router.post("/calculate")
async def calculate(req: CalculateRequest):
    """Calculate profit for given parameters."""
    result = calculate_profit(
        selling_price=req.selling_price,
        manufacturing_cost=req.manufacturing_cost,
        packaging_cost=req.packaging_cost,
        fba_fee=req.fba_fee,
        ad_rate=req.ad_rate,
        target_sales=req.target_sales,
    )

    scenarios = calculate_scenarios(
        selling_price=req.selling_price,
        manufacturing_cost=req.manufacturing_cost,
        packaging_cost=req.packaging_cost,
        fba_fee=req.fba_fee,
        ad_rate=req.ad_rate,
        target_sales=req.target_sales,
    )

    return {
        **result,
        "scenarios": scenarios,
    }


@router.post("/save")
async def save_simulation(req: SaveRequest, db: Session = Depends(get_db)):
    """Save simulation result to DB."""
    record = ProfitSimulation(
        product_name=req.product_name,
        selling_price=req.selling_price,
        manufacturing_cost=req.manufacturing_cost,
        packaging_cost=req.packaging_cost,
        fba_fee=req.fba_fee,
        ad_rate=req.ad_rate,
        target_sales=req.target_sales,
        profit_per_unit=req.profit_per_unit,
        profit_margin=req.profit_margin,
        monthly_profit=req.monthly_profit,
        roi=req.roi,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id}


@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Get saved simulations."""
    results = (
        db.query(ProfitSimulation)
        .order_by(ProfitSimulation.created_at.desc())
        .limit(50)
        .all()
    )

    items = []
    for r in results:
        # Recalculate full results for display
        full_result = calculate_profit(
            selling_price=r.selling_price,
            manufacturing_cost=r.manufacturing_cost,
            packaging_cost=r.packaging_cost,
            fba_fee=r.fba_fee,
            ad_rate=r.ad_rate,
            target_sales=r.target_sales,
        )
        scenarios = calculate_scenarios(
            selling_price=r.selling_price,
            manufacturing_cost=r.manufacturing_cost,
            packaging_cost=r.packaging_cost,
            fba_fee=r.fba_fee,
            ad_rate=r.ad_rate,
            target_sales=r.target_sales,
        )
        items.append({
            "id": r.id,
            "product_name": r.product_name or "",
            "selling_price": r.selling_price,
            "manufacturing_cost": r.manufacturing_cost,
            "packaging_cost": r.packaging_cost,
            "fba_fee": r.fba_fee,
            "ad_rate": r.ad_rate,
            "target_sales": r.target_sales,
            **full_result,
            "scenarios": scenarios,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })

    return items


@router.get("/{simulation_id}")
async def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get specific simulation."""
    r = db.query(ProfitSimulation).filter(ProfitSimulation.id == simulation_id).first()
    if not r:
        return {"error": "Not found"}

    full_result = calculate_profit(
        selling_price=r.selling_price,
        manufacturing_cost=r.manufacturing_cost,
        packaging_cost=r.packaging_cost,
        fba_fee=r.fba_fee,
        ad_rate=r.ad_rate,
        target_sales=r.target_sales,
    )
    scenarios = calculate_scenarios(
        selling_price=r.selling_price,
        manufacturing_cost=r.manufacturing_cost,
        packaging_cost=r.packaging_cost,
        fba_fee=r.fba_fee,
        ad_rate=r.ad_rate,
        target_sales=r.target_sales,
    )

    return {
        "id": r.id,
        "product_name": r.product_name or "",
        "selling_price": r.selling_price,
        "manufacturing_cost": r.manufacturing_cost,
        "packaging_cost": r.packaging_cost,
        "fba_fee": r.fba_fee,
        "ad_rate": r.ad_rate,
        "target_sales": r.target_sales,
        **full_result,
        "scenarios": scenarios,
        "created_at": r.created_at.isoformat() if r.created_at else "",
    }


@router.delete("/{simulation_id}")
async def delete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Delete a simulation."""
    record = db.query(ProfitSimulation).filter(ProfitSimulation.id == simulation_id).first()
    if not record:
        return {"error": "Not found"}
    db.delete(record)
    db.commit()
    return {"ok": True}


@router.post("/fba-fee")
async def estimate_fba_fee(price: int, weight_kg: float = 0.5, category: str = "health"):
    """Estimate FBA fee."""
    fee = calculate_fba_fee(price, weight_kg, category)
    return {"fba_fee": fee}
