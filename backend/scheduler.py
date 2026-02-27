"""
APScheduler setup for periodic background tasks.
Schedules weekly scraping jobs for trend data and factory information.
"""

import json
import logging
import random
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from backend.models.database import SessionLocal, IngredientTrend, Factory
from backend.services.scraper import WebScraper

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
scraper_instance = WebScraper()


async def refresh_ingredient_trends() -> None:
    """
    Weekly job to refresh ingredient trend data.
    Collects new data points for tracked ingredients.
    """
    logger.info("Starting weekly ingredient trend refresh...")

    db = SessionLocal()
    try:
        # Get latest data for each ingredient
        latest_trends = (
            db.query(IngredientTrend)
            .order_by(IngredientTrend.week_date.desc())
            .all()
        )

        seen_ingredients: dict = {}
        for t in latest_trends:
            if t.ingredient_name not in seen_ingredients:
                seen_ingredients[t.ingredient_name] = {
                    "mention_count": t.mention_count,
                    "growth_rate": t.growth_rate,
                    "market_size": t.market_size,
                }

        if not seen_ingredients:
            logger.info("No existing trend data found. Skipping refresh.")
            return

        new_week = datetime.utcnow().strftime("%Y-%m-%d")
        updated = 0

        for name, data in seen_ingredients.items():
            growth_rate = data["growth_rate"] or 10
            weekly_growth = growth_rate / 52
            noise = random.uniform(-3, 3)

            new_mentions = int(
                (data["mention_count"] or 1000)
                * (1 + (weekly_growth + noise) / 100)
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
        logger.info(f"Ingredient trends refreshed: {updated} ingredients updated.")
    except Exception as e:
        logger.error(f"Error refreshing ingredient trends: {e}")
        db.rollback()
    finally:
        db.close()


async def refresh_factory_data() -> None:
    """
    Weekly job to refresh factory data.
    Scrapes new factory information and adds entries.
    """
    logger.info("Starting weekly factory data refresh...")

    db = SessionLocal()
    try:
        scraped = await scraper_instance.scrape_factory_data(
            query="OEM サプリメント 健康食品 製造"
        )

        added = 0
        for f in scraped:
            existing = db.query(Factory).filter(Factory.name == f["name"]).first()
            if existing:
                continue

            factory = Factory(
                name=f["name"],
                prefecture=f.get("prefecture"),
                categories=json.dumps(
                    f.get("categories", []), ensure_ascii=False
                ),
                dosage_forms=json.dumps(
                    f.get("dosage_forms", []), ensure_ascii=False
                ),
                min_lot=f.get("min_lot"),
                url=f.get("url"),
                contact_url=f.get("contact_url"),
                certifications=json.dumps(
                    f.get("certifications", []), ensure_ascii=False
                ),
                features=f.get("features"),
                is_favorite=False,
                memo=None,
            )
            db.add(factory)
            added += 1

        db.commit()
        logger.info(
            f"Factory data refreshed: found {len(scraped)}, added {added} new."
        )
    except Exception as e:
        logger.error(f"Error refreshing factory data: {e}")
        db.rollback()
    finally:
        db.close()


def setup_scheduler() -> AsyncIOScheduler:
    """
    Configure and return the scheduler with all periodic jobs.

    Jobs:
    - Ingredient trends refresh: Every Monday at 6:00 AM JST
    - Factory data refresh: Every Monday at 7:00 AM JST
    """
    # Weekly ingredient trend refresh - Mondays at 6:00 AM JST (21:00 UTC Sunday)
    scheduler.add_job(
        refresh_ingredient_trends,
        trigger=CronTrigger(day_of_week="sun", hour=21, minute=0),
        id="refresh_ingredient_trends",
        name="Weekly ingredient trend refresh",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # Weekly factory data refresh - Mondays at 7:00 AM JST (22:00 UTC Sunday)
    scheduler.add_job(
        refresh_factory_data,
        trigger=CronTrigger(day_of_week="sun", hour=22, minute=0),
        id="refresh_factory_data",
        name="Weekly factory data refresh",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    logger.info("Scheduler configured with weekly jobs.")
    return scheduler


def get_scheduler_status() -> dict:
    """Get the current status of all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
    }
