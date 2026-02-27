"""Review analysis router."""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db, ReviewAnalysis
from backend.services.spapi_client import SPAPIClient
from backend.services.ai_analyzer import AIAnalyzer

router = APIRouter(prefix="/api/review", tags=["review"])


class AnalyzeRequest(BaseModel):
    asin: str


@router.post("/analyze")
async def analyze_reviews(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze reviews for an ASIN using SP-API + Claude AI."""
    # Get reviews
    spapi = SPAPIClient()
    reviews = await spapi.get_reviews(req.asin)

    # Analyze with Claude AI
    analyzer = AIAnalyzer()
    analysis = await analyzer.analyze_reviews(reviews, req.asin)

    # Save to DB
    record = ReviewAnalysis(
        asin=req.asin,
        negative_summary=json.dumps(analysis.get("negative_categories", []), ensure_ascii=False),
        differentiation_points=json.dumps(analysis.get("differentiation_points", []), ensure_ascii=False),
        gaps=analysis.get("gap_analysis", ""),
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "asin": req.asin,
        "negative_categories": analysis.get("negative_categories", []),
        "gap_analysis": analysis.get("gap_analysis", ""),
        "differentiation_points": analysis.get("differentiation_points", []),
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "winning_report": analysis.get("winning_report", ""),
        "created_at": record.created_at.isoformat(),
    }


@router.get("/history")
async def get_review_history(db: Session = Depends(get_db)):
    """Get past review analyses."""
    results = (
        db.query(ReviewAnalysis)
        .order_by(ReviewAnalysis.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "asin": r.asin,
            "negative_summary": r.negative_summary,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in results
    ]


@router.get("/{analysis_id}")
async def get_review_detail(analysis_id: int, db: Session = Depends(get_db)):
    """Get specific review analysis."""
    record = db.query(ReviewAnalysis).filter(ReviewAnalysis.id == analysis_id).first()
    if not record:
        return {"error": "Not found"}

    negative_categories = []
    differentiation_points = []
    try:
        negative_categories = json.loads(record.negative_summary) if record.negative_summary else []
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        differentiation_points = json.loads(record.differentiation_points) if record.differentiation_points else []
    except (json.JSONDecodeError, TypeError):
        pass

    return {
        "id": record.id,
        "asin": record.asin,
        "negative_categories": negative_categories,
        "differentiation_points": differentiation_points,
        "gaps": record.gaps,
        "created_at": record.created_at.isoformat() if record.created_at else "",
    }
