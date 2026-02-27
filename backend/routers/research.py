"""
Market research router for keyword-based product research.
Provides endpoints for searching products, viewing history,
and getting detailed product analysis with market scoring.
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import MarketResearch, get_db
from backend.services.keepa_client import KeepaClient

router = APIRouter(prefix="/api/research", tags=["research"])

keepa_client = KeepaClient()


# --- Pydantic Schemas ---


class SearchRequest(BaseModel):
    """Request schema for market research search."""

    keyword: str = Field(..., min_length=1, max_length=200, description="Search keyword")
    category: Optional[str] = Field(None, description="Product category filter")


class ProductResult(BaseModel):
    """Schema for a single product result."""

    asin: str
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    review_count: Optional[int] = None
    rating: Optional[float] = None
    monthly_sales: Optional[int] = None
    monthly_revenue: Optional[float] = None
    market_score: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class SearchResponse(BaseModel):
    """Response schema for market research search."""

    keyword: str
    total_products: int
    market_score: float
    market_summary: Dict[str, Any]
    products: List[ProductResult]


class ResearchHistoryItem(BaseModel):
    """Schema for a research history entry."""

    id: int
    keyword: str
    asin: str
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    review_count: Optional[int] = None
    rating: Optional[float] = None
    monthly_sales: Optional[int] = None
    monthly_revenue: Optional[float] = None
    market_score: Optional[float] = None
    created_at: datetime


# --- Market Scoring ---


def calculate_market_score(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate a 0-100 market score based on multiple factors.

    Factors:
    - Market size (total monthly revenue)
    - Competition intensity (number of strong competitors)
    - Price range (accessibility)
    - Trend (average sales growth)
    - New entrant success rate (how well lower-ranked products perform)
    """
    if not products:
        return {"score": 0, "factors": {}}

    # Market size score (0-25 points)
    total_revenue = sum(p.get("monthly_revenue", 0) for p in products)
    avg_revenue = total_revenue / len(products)
    if avg_revenue >= 10_000_000:
        size_score = 25
    elif avg_revenue >= 5_000_000:
        size_score = 20
    elif avg_revenue >= 1_000_000:
        size_score = 15
    elif avg_revenue >= 500_000:
        size_score = 10
    else:
        size_score = 5

    # Competition intensity score (0-25 points, lower competition = higher score)
    high_review_count = sum(
        1 for p in products if (p.get("review_count", 0) or 0) > 1000
    )
    competition_ratio = high_review_count / max(len(products), 1)
    if competition_ratio < 0.2:
        competition_score = 25
    elif competition_ratio < 0.4:
        competition_score = 20
    elif competition_ratio < 0.6:
        competition_score = 15
    elif competition_ratio < 0.8:
        competition_score = 10
    else:
        competition_score = 5

    # Price range score (0-20 points)
    prices = [p.get("price", 0) for p in products if p.get("price")]
    if prices:
        avg_price = sum(prices) / len(prices)
        price_range = max(prices) - min(prices)
        # Sweet spot: average price between 1500-4000 JPY
        if 1500 <= avg_price <= 4000:
            price_score = 20
        elif 1000 <= avg_price <= 5000:
            price_score = 15
        elif 500 <= avg_price <= 8000:
            price_score = 10
        else:
            price_score = 5
    else:
        avg_price = 0
        price_range = 0
        price_score = 5

    # Trend score (0-15 points)
    avg_sales = sum(p.get("monthly_sales", 0) for p in products) / max(
        len(products), 1
    )
    if avg_sales >= 3000:
        trend_score = 15
    elif avg_sales >= 1500:
        trend_score = 12
    elif avg_sales >= 500:
        trend_score = 8
    else:
        trend_score = 4

    # New entrant success rate (0-15 points)
    # Check if products with fewer reviews still have decent sales
    new_products = [
        p
        for p in products
        if (p.get("review_count", 0) or 0) < 500 and (p.get("monthly_sales", 0) or 0) > 100
    ]
    new_entrant_ratio = len(new_products) / max(len(products), 1)
    if new_entrant_ratio >= 0.3:
        entrant_score = 15
    elif new_entrant_ratio >= 0.2:
        entrant_score = 12
    elif new_entrant_ratio >= 0.1:
        entrant_score = 8
    else:
        entrant_score = 4

    total_score = (
        size_score + competition_score + price_score + trend_score + entrant_score
    )

    return {
        "score": min(100, total_score),
        "factors": {
            "market_size": {
                "score": size_score,
                "max": 25,
                "total_revenue": round(total_revenue, 0),
                "avg_revenue": round(avg_revenue, 0),
            },
            "competition": {
                "score": competition_score,
                "max": 25,
                "strong_competitors": high_review_count,
                "competition_ratio": round(competition_ratio, 2),
            },
            "price_range": {
                "score": price_score,
                "max": 20,
                "avg_price": round(avg_price, 0),
                "range": round(price_range, 0),
            },
            "trend": {
                "score": trend_score,
                "max": 15,
                "avg_monthly_sales": round(avg_sales, 0),
            },
            "new_entrant_success": {
                "score": entrant_score,
                "max": 15,
                "successful_new_products": len(new_products),
                "ratio": round(new_entrant_ratio, 2),
            },
        },
    }


# --- Endpoints ---


@router.post("/search", response_model=SearchResponse)
async def search_market(
    request: SearchRequest, db: Session = Depends(get_db)
) -> SearchResponse:
    """
    Perform keyword-based market research.
    Searches products via Keepa API, calculates market scores,
    and saves results to the database.
    """
    products = await keepa_client.search_products(
        keyword=request.keyword, category=request.category
    )

    market_data = calculate_market_score(products)

    # Save each product to the database
    for product in products:
        db_record = MarketResearch(
            keyword=request.keyword,
            asin=product.get("asin", ""),
            title=product.get("title", ""),
            brand=product.get("brand"),
            price=product.get("price"),
            review_count=product.get("review_count"),
            rating=product.get("rating"),
            monthly_sales=product.get("monthly_sales"),
            monthly_revenue=product.get("monthly_revenue"),
            market_score=market_data["score"],
        )
        db.add(db_record)

    db.commit()

    product_results = [
        ProductResult(
            asin=p.get("asin", ""),
            title=p.get("title", ""),
            brand=p.get("brand"),
            price=p.get("price"),
            review_count=p.get("review_count"),
            rating=p.get("rating"),
            monthly_sales=p.get("monthly_sales"),
            monthly_revenue=p.get("monthly_revenue"),
            market_score=market_data["score"],
            category=p.get("category"),
            image_url=p.get("image_url"),
        )
        for p in products
    ]

    return SearchResponse(
        keyword=request.keyword,
        total_products=len(products),
        market_score=market_data["score"],
        market_summary=market_data["factors"],
        products=product_results,
    )


@router.get("/history")
async def get_research_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get past research results with optional keyword filter."""
    query = db.query(MarketResearch).order_by(MarketResearch.created_at.desc())

    if keyword:
        query = query.filter(MarketResearch.keyword.contains(keyword))

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    # Group by keyword and created_at (approximate grouping by search session)
    grouped: Dict[str, Dict[str, Any]] = {}
    for r in results:
        key = f"{r.keyword}_{r.created_at.strftime('%Y%m%d%H%M')}"
        if key not in grouped:
            grouped[key] = {
                "keyword": r.keyword,
                "market_score": r.market_score,
                "created_at": r.created_at.isoformat(),
                "product_count": 0,
                "products": [],
            }
        grouped[key]["product_count"] += 1
        grouped[key]["products"].append({
            "id": r.id,
            "asin": r.asin,
            "title": r.title,
            "brand": r.brand,
            "price": r.price,
            "review_count": r.review_count,
            "rating": r.rating,
            "monthly_sales": r.monthly_sales,
            "monthly_revenue": r.monthly_revenue,
        })

    return {
        "total": total,
        "results": list(grouped.values()),
    }


@router.get("/product/{asin}")
async def get_product_analysis(
    asin: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed product analysis for a specific ASIN."""
    details = await keepa_client.get_product_details(asin)

    # Fetch any saved research data
    saved = (
        db.query(MarketResearch)
        .filter(MarketResearch.asin == asin)
        .order_by(MarketResearch.created_at.desc())
        .first()
    )

    result: Dict[str, Any] = {
        "asin": asin,
        "details": details,
        "saved_data": None,
    }

    if saved:
        result["saved_data"] = {
            "keyword": saved.keyword,
            "market_score": saved.market_score,
            "monthly_sales": saved.monthly_sales,
            "monthly_revenue": saved.monthly_revenue,
            "created_at": saved.created_at.isoformat(),
        }

    return result
