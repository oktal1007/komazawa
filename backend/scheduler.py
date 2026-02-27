"""APScheduler setup for weekly automated scraping jobs."""

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def weekly_trend_scrape():
    """Run weekly ingredient trend scraping."""
    import asyncio
    from backend.services.scraper import scrape_ingredient_trends
    from backend.models.database import SessionLocal, IngredientTrend

    async def _run():
        trends = await scrape_ingredient_trends()
        db = SessionLocal()
        try:
            today = datetime.utcnow().date()
            for t in trends:
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
            logger.info(f"Weekly trend scrape completed: {len(trends)} ingredients")
        finally:
            db.close()

    asyncio.run(_run())


def setup_scheduler():
    """Set up scheduled jobs."""
    # Weekly trend scraping - every Monday at 6:00 AM JST (21:00 UTC Sunday)
    scheduler.add_job(
        weekly_trend_scrape,
        trigger=CronTrigger(day_of_week="sun", hour=21, minute=0),
        id="weekly_trend_scrape",
        name="Weekly Ingredient Trend Scrape",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with weekly trend scrape job")


def shutdown_scheduler():
    """Shutdown scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
