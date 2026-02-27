"""Market research router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db, MarketResearch
from backend.services.keepa_client import KeepaClient

router = APIRouter(prefix="/api/research", tags=["research"])


class SearchRequest(BaseModel):
    keyword: str
    category: Optional[str] = None


class MarketScore(BaseModel):
    total: int
    market_size: int
    competition: int
    price_range: int
    trend: int
    new_entrant: int


def calculate_market_score(products: list[dict]) -> dict:
    """Calculate market entry score (0-100) based on multiple factors."""
    if not products:
        return {"total": 0, "market_size": 0, "competition": 0, "price_range": 0, "trend": 0, "new_entrant": 0}

    total_revenue = sum(p.get("monthly_revenue", 0) for p in products)
    avg_reviews = sum(p.get("review_count", 0) for p in products) / len(products) if products else 0
    avg_rating = sum(p.get("rating", 0) for p in products) / len(products) if products else 0
    prices = [p.get("price", 0) for p in products if p.get("price", 0) > 0]
    avg_price = sum(prices) / len(prices) if prices else 0

    # Market size score: higher revenue = higher score
    if total_revenue > 50000000:
        market_size = 90
    elif total_revenue > 20000000:
        market_size = 75
    elif total_revenue > 5000000:
        market_size = 60
    else:
        market_size = 40

    # Competition score: fewer reviews = easier to compete (inverted)
    if avg_reviews < 100:
        competition = 85
    elif avg_reviews < 500:
        competition = 65
    elif avg_reviews < 2000:
        competition = 45
    else:
        competition = 25

    # Price range score: mid-range prices are ideal for margin
    if 1500 <= avg_price <= 4000:
        price_range = 80
    elif 1000 <= avg_price <= 6000:
        price_range = 60
    else:
        price_range = 40

    # Trend score (based on avg rating - higher rating suggests healthy market)
    if avg_rating >= 4.0:
        trend = 75
    elif avg_rating >= 3.5:
        trend = 60
    else:
        trend = 40

    # New entrant score
    new_products = [p for p in products if p.get("is_new", False)]
    new_ratio = len(new_products) / len(products) if products else 0
    if new_ratio >= 0.2:
        new_entrant = 80
    elif new_ratio >= 0.1:
        new_entrant = 65
    else:
        new_entrant = 45

    total = int((market_size + competition + price_range + trend + new_entrant) / 5)

    return {
        "total": total,
        "market_size": market_size,
        "competition": competition,
        "price_range": price_range,
        "trend": trend,
        "new_entrant": new_entrant,
    }


@router.post("/search")
async def search_market(req: SearchRequest, db: Session = Depends(get_db)):
    """Search market by keyword using Keepa API."""
    client = KeepaClient()
    products = await client.search_products(req.keyword, req.category)

    # Save to DB
    for p in products:
        record = MarketResearch(
            keyword=req.keyword,
            asin=p.get("asin", ""),
            title=p.get("title", ""),
            brand=p.get("brand", ""),
            price=p.get("price", 0),
            review_count=p.get("review_count", 0),
            rating=p.get("rating", 0),
            monthly_sales=p.get("monthly_sales", 0),
            monthly_revenue=p.get("monthly_revenue", 0),
            market_score=0,
            created_at=datetime.utcnow(),
        )
        db.add(record)
    db.commit()

    # Calculate market score
    score = calculate_market_score(products)

    # Update score in DB
    for record in db.query(MarketResearch).filter(MarketResearch.keyword == req.keyword).all():
        record.market_score = score["total"]
    db.commit()

    # Calculate summary stats
    prices = [p.get("price", 0) for p in products if p.get("price", 0) > 0]
    sorted_prices = sorted(prices)

    summary = {
        "total_products": len(products),
        "avg_price": int(sum(prices) / len(prices)) if prices else 0,
        "median_price": sorted_prices[len(sorted_prices) // 2] if sorted_prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "avg_rating": round(sum(p.get("rating", 0) for p in products) / len(products), 1) if products else 0,
        "total_monthly_revenue": sum(p.get("monthly_revenue", 0) for p in products),
        "fba_ratio": sum(1 for p in products if p.get("is_fba", False)) / len(products) if products else 0,
        "new_entrant_ratio": sum(1 for p in products if p.get("is_new", False)) / len(products) if products else 0,
    }

    # Map products to response format
    response_products = [
        {
            "id": 0,
            "keyword": req.keyword,
            "asin": p.get("asin", ""),
            "title": p.get("title", ""),
            "brand": p.get("brand", ""),
            "price": p.get("price", 0),
            "review_count": p.get("review_count", 0),
            "rating": p.get("rating", 0),
            "monthly_sales": p.get("monthly_sales", 0),
            "monthly_revenue": p.get("monthly_revenue", 0),
            "market_score": score["total"],
            "created_at": datetime.utcnow().isoformat(),
        }
        for p in products
    ]

    return {
        "products": response_products,
        "market_score": score,
        "summary": summary,
    }


@router.get("/history")
async def get_research_history(db: Session = Depends(get_db)):
    """Get past research results."""
    results = (
        db.query(MarketResearch)
        .order_by(MarketResearch.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": r.id,
            "keyword": r.keyword,
            "asin": r.asin,
            "title": r.title,
            "brand": r.brand,
            "price": r.price,
            "review_count": r.review_count,
            "rating": r.rating,
            "monthly_sales": r.monthly_sales,
            "monthly_revenue": r.monthly_revenue,
            "market_score": r.market_score,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in results
    ]


@router.get("/product/{asin}")
async def get_product_details(asin: str):
    """Get detailed product analysis."""
    client = KeepaClient()
    details = await client.get_product_details(asin)
    return details
