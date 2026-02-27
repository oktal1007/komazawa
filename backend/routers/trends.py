"""
Ingredient trends router for tracking supplement ingredient popularity.
Provides endpoints for viewing trends, generating AI reports,
and refreshing trend data.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import IngredientTrend, get_db
from backend.services.ai_analyzer import AIAnalyzer
from backend.services.scraper import WebScraper

router = APIRouter(prefix="/api/trends", tags=["trends"])

ai_analyzer = AIAnalyzer()
scraper = WebScraper()


# --- Pydantic Schemas ---


class IngredientTrendItem(BaseModel):
    """Schema for an ingredient trend entry."""

    id: int
    ingredient_name: str
    mention_count: Optional[int] = None
    growth_rate: Optional[float] = None
    market_size: Optional[float] = None
    week_date: Optional[str] = None


class TrendSummary(BaseModel):
    """Schema for a trend summary."""

    ingredient_name: str
    latest_mention_count: Optional[int] = None
    avg_growth_rate: Optional[float] = None
    latest_market_size: Optional[float] = None
    trend_direction: str = "stable"
    data_points: List[IngredientTrendItem]


class RefreshResponse(BaseModel):
    """Response schema for trend refresh."""

    status: str
    ingredients_updated: int
    message: str


# --- Demo Data Seeding ---


def _seed_demo_trends(db: Session) -> None:
    """Seed the database with realistic demo trend data if empty."""
    existing = db.query(IngredientTrend).count()
    if existing > 0:
        return

    ingredients = [
        {
            "name": "NMN（ニコチンアミドモノヌクレオチド）",
            "base_mentions": 8500,
            "growth": 34.5,
            "market_size": 285.0,
        },
        {
            "name": "エクオール",
            "base_mentions": 6200,
            "growth": 28.3,
            "market_size": 156.0,
        },
        {
            "name": "乳酸菌・ビフィズス菌",
            "base_mentions": 14200,
            "growth": 12.1,
            "market_size": 892.0,
        },
        {
            "name": "CBD（カンナビジオール）",
            "base_mentions": 4500,
            "growth": 45.2,
            "market_size": 78.0,
        },
        {
            "name": "クレアチン",
            "base_mentions": 7800,
            "growth": 18.7,
            "market_size": 234.0,
        },
        {
            "name": "コラーゲンペプチド",
            "base_mentions": 11500,
            "growth": 8.5,
            "market_size": 567.0,
        },
        {
            "name": "ビタミンD3",
            "base_mentions": 9800,
            "growth": 22.1,
            "market_size": 345.0,
        },
        {
            "name": "マグネシウム",
            "base_mentions": 7200,
            "growth": 31.4,
            "market_size": 198.0,
        },
        {
            "name": "ルテイン",
            "base_mentions": 5400,
            "growth": 15.3,
            "market_size": 123.0,
        },
        {
            "name": "GABA",
            "base_mentions": 6800,
            "growth": 19.8,
            "market_size": 167.0,
        },
        {
            "name": "アスタキサンチン",
            "base_mentions": 3200,
            "growth": 25.6,
            "market_size": 89.0,
        },
        {
            "name": "ウロリチン",
            "base_mentions": 1800,
            "growth": 68.3,
            "market_size": 23.0,
        },
    ]

    now = datetime.utcnow()
    for ingredient in ingredients:
        for week_offset in range(12):  # 12 weeks of data
            week_date = now - timedelta(weeks=week_offset)
            week_str = week_date.strftime("%Y-%m-%d")
            # Simulate growth over time
            growth_factor = 1 + (ingredient["growth"] / 100) * (
                (12 - week_offset) / 52
            )
            mention_count = int(ingredient["base_mentions"] * growth_factor)
            market_size = ingredient["market_size"] * growth_factor

            trend = IngredientTrend(
                ingredient_name=ingredient["name"],
                mention_count=mention_count,
                growth_rate=ingredient["growth"],
                market_size=round(market_size, 1),
                week_date=week_str,
            )
            db.add(trend)

    db.commit()


# --- Endpoints ---


@router.get("/ingredients")
async def get_ingredient_trends(
    weeks: int = Query(4, ge=1, le=52, description="Number of weeks to show"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get ingredient trend data for the specified number of weeks.
    Seeds demo data on first access if database is empty.
    """
    _seed_demo_trends(db)

    cutoff_date = (datetime.utcnow() - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

    trends = (
        db.query(IngredientTrend)
        .filter(IngredientTrend.week_date >= cutoff_date)
        .order_by(IngredientTrend.ingredient_name, IngredientTrend.week_date.desc())
        .all()
    )

    # Group by ingredient
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for t in trends:
        if t.ingredient_name not in grouped:
            grouped[t.ingredient_name] = []
        grouped[t.ingredient_name].append({
            "id": t.id,
            "mention_count": t.mention_count,
            "growth_rate": t.growth_rate,
            "market_size": t.market_size,
            "week_date": t.week_date,
        })

    # Build summaries
    summaries: List[Dict[str, Any]] = []
    for name, data_points in grouped.items():
        if not data_points:
            continue

        latest = data_points[0]
        oldest = data_points[-1] if len(data_points) > 1 else data_points[0]

        # Determine trend direction
        if latest["mention_count"] and oldest["mention_count"]:
            change = (
                (latest["mention_count"] - oldest["mention_count"])
                / oldest["mention_count"]
                * 100
            )
            if change > 5:
                direction = "up"
            elif change < -5:
                direction = "down"
            else:
                direction = "stable"
        else:
            direction = "stable"

        avg_growth = sum(
            dp["growth_rate"] for dp in data_points if dp["growth_rate"]
        ) / max(len(data_points), 1)

        summaries.append({
            "ingredient_name": name,
            "latest_mention_count": latest["mention_count"],
            "avg_growth_rate": round(avg_growth, 1),
            "latest_market_size": latest["market_size"],
            "trend_direction": direction,
            "data_points": data_points,
        })

    # Sort by latest mention count (most popular first)
    summaries.sort(
        key=lambda x: x.get("latest_mention_count", 0) or 0, reverse=True
    )

    return {
        "weeks": weeks,
        "total_ingredients": len(summaries),
        "trends": summaries,
    }


@router.get("/report")
async def get_trend_report(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get the latest AI-generated trend report.
    Generates a report based on current trend data using Claude AI.
    """
    _seed_demo_trends(db)

    # Gather current trend data for AI analysis
    trends = (
        db.query(IngredientTrend)
        .order_by(IngredientTrend.week_date.desc())
        .limit(100)
        .all()
    )

    trends_data: List[Dict[str, Any]] = []
    for t in trends:
        trends_data.append({
            "ingredient_name": t.ingredient_name,
            "mention_count": t.mention_count,
            "growth_rate": t.growth_rate,
            "market_size": t.market_size,
            "week_date": t.week_date,
        })

    report = await ai_analyzer.generate_trend_report(trends_data)

    return {"report": report, "data_points_analyzed": len(trends_data)}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_trends(
    db: Session = Depends(get_db),
) -> RefreshResponse:
    """
    Manually trigger a trend data refresh.
    In production, this would scrape live data.
    For demo, it adds a new week of simulated data.
    """
    # Get the latest entries for each ingredient
    latest_trends = (
        db.query(IngredientTrend)
        .order_by(IngredientTrend.week_date.desc())
        .all()
    )

    seen_ingredients: Dict[str, Dict[str, Any]] = {}
    for t in latest_trends:
        if t.ingredient_name not in seen_ingredients:
            seen_ingredients[t.ingredient_name] = {
                "mention_count": t.mention_count,
                "growth_rate": t.growth_rate,
                "market_size": t.market_size,
            }

    if not seen_ingredients:
        _seed_demo_trends(db)
        return RefreshResponse(
            status="success",
            ingredients_updated=12,
            message="Demo data seeded successfully.",
        )

    # Add new week data with simulated growth
    new_week = datetime.utcnow().strftime("%Y-%m-%d")
    updated = 0

    for name, data in seen_ingredients.items():
        import random

        growth_rate = data["growth_rate"] or 10
        weekly_growth = growth_rate / 52  # Approximate weekly growth
        noise = random.uniform(-2, 2)  # Add some randomness

        new_mentions = int(
            (data["mention_count"] or 1000) * (1 + (weekly_growth + noise) / 100)
        )
        new_market_size = (data["market_size"] or 100) * (
            1 + weekly_growth / 100
        )

        trend = IngredientTrend(
            ingredient_name=name,
            mention_count=new_mentions,
            growth_rate=growth_rate,
            market_size=round(new_market_size, 1),
            week_date=new_week,
        )
        db.add(trend)
        updated += 1

    db.commit()

    return RefreshResponse(
        status="success",
        ingredients_updated=updated,
        message=f"Updated {updated} ingredients with new weekly data.",
    )
