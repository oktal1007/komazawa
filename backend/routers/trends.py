"""Ingredient trends router."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.database import get_db, IngredientTrend
from backend.services.scraper import scrape_ingredient_trends
from backend.services.ai_analyzer import AIAnalyzer

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/ingredients")
async def get_ingredient_trends(weeks: int = 12, db: Session = Depends(get_db)):
    """Get ingredient trends for the specified number of weeks."""
    cutoff = datetime.utcnow() - timedelta(weeks=weeks)
    results = (
        db.query(IngredientTrend)
        .filter(IngredientTrend.week_date >= cutoff.date())
        .order_by(IngredientTrend.week_date.desc(), IngredientTrend.mention_count.desc())
        .all()
    )

    # If no data in DB, seed with demo data
    if not results:
        trends = await scrape_ingredient_trends()
        now = datetime.utcnow()
        for week_offset in range(min(weeks, 12)):
            week_date = (now - timedelta(weeks=week_offset)).date()
            for t in trends:
                # Simulate slight variation over weeks
                import random
                variation = random.uniform(0.85, 1.15)
                record = IngredientTrend(
                    ingredient_name=t["ingredient_name"],
                    mention_count=int(t["mention_count"] * variation),
                    growth_rate=t["growth_rate"],
                    market_size=t["market_size"],
                    week_date=week_date,
                )
                db.add(record)
        db.commit()

        results = (
            db.query(IngredientTrend)
            .filter(IngredientTrend.week_date >= cutoff.date())
            .order_by(IngredientTrend.week_date.desc(), IngredientTrend.mention_count.desc())
            .all()
        )

    return [
        {
            "id": r.id,
            "ingredient_name": r.ingredient_name,
            "mention_count": r.mention_count,
            "growth_rate": r.growth_rate,
            "market_size": r.market_size,
            "week_date": r.week_date.isoformat() if r.week_date else "",
        }
        for r in results
    ]


@router.get("/report")
async def get_trend_report(db: Session = Depends(get_db)):
    """Get latest AI-generated trend report."""
    # Get latest trend data
    results = (
        db.query(IngredientTrend)
        .order_by(IngredientTrend.week_date.desc(), IngredientTrend.mention_count.desc())
        .limit(50)
        .all()
    )

    trends_data = [
        {
            "ingredient_name": r.ingredient_name,
            "mention_count": r.mention_count,
            "growth_rate": r.growth_rate,
            "market_size": r.market_size,
        }
        for r in results
    ]

    analyzer = AIAnalyzer()
    report = await analyzer.generate_trend_report(trends_data)

    return report


@router.post("/refresh")
async def refresh_trends(db: Session = Depends(get_db)):
    """Manually trigger trend data refresh."""
    trends = await scrape_ingredient_trends()
    today = datetime.utcnow().date()

    for t in trends:
        # Check if already exists for today
        existing = (
            db.query(IngredientTrend)
            .filter(
                IngredientTrend.ingredient_name == t["ingredient_name"],
                IngredientTrend.week_date == today,
            )
            .first()
        )
        if existing:
            existing.mention_count = t["mention_count"]
            existing.growth_rate = t["growth_rate"]
            existing.market_size = t["market_size"]
        else:
            record = IngredientTrend(
                ingredient_name=t["ingredient_name"],
                mention_count=t["mention_count"],
                growth_rate=t["growth_rate"],
                market_size=t["market_size"],
                week_date=today,
            )
            db.add(record)

    db.commit()
    return {"status": "ok", "count": len(trends)}
