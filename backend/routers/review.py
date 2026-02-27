"""
Review analysis router for AI-powered product review analysis.
Provides endpoints for analyzing reviews, viewing analysis history,
and retrieving specific analysis results.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import ReviewAnalysis, get_db
from backend.services.ai_analyzer import AIAnalyzer
from backend.services.spapi_client import SPAPIClient

router = APIRouter(prefix="/api/review", tags=["review"])

spapi_client = SPAPIClient()
ai_analyzer = AIAnalyzer()


# --- Pydantic Schemas ---


class ReviewAnalyzeRequest(BaseModel):
    """Request schema for review analysis."""

    asin: str = Field(..., min_length=1, max_length=20, description="Amazon ASIN")
    max_reviews: int = Field(500, ge=1, le=1000, description="Maximum reviews to analyze")


class NegativeCategory(BaseModel):
    """Schema for a negative review category."""

    category: str
    count: int
    severity: str
    examples: List[str]


class GapAnalysisItem(BaseModel):
    """Schema for a gap analysis item."""

    gap: str
    frequency: str
    opportunity: str


class DifferentiationPoint(BaseModel):
    """Schema for a differentiation point."""

    point: str
    description: str
    priority: str


class StrengthItem(BaseModel):
    """Schema for a product strength."""

    strength: str
    mention_count: int


class WeaknessItem(BaseModel):
    """Schema for a product weakness."""

    weakness: str
    mention_count: int
    improvement_suggestion: str


class SentimentSummary(BaseModel):
    """Schema for overall sentiment summary."""

    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float
    summary: str


class ReviewAnalysisResponse(BaseModel):
    """Response schema for review analysis."""

    id: Optional[int] = None
    asin: str
    review_count: int
    negative_categories: List[NegativeCategory]
    gap_analysis: List[GapAnalysisItem]
    differentiation_points: List[DifferentiationPoint]
    strengths: List[StrengthItem]
    weaknesses: List[WeaknessItem]
    overall_sentiment: SentimentSummary
    created_at: Optional[str] = None


class ReviewHistoryItem(BaseModel):
    """Schema for review analysis history entry."""

    id: int
    asin: str
    negative_summary: Optional[str] = None
    differentiation_points: Optional[str] = None
    gaps: Optional[str] = None
    created_at: str


# --- Endpoints ---


@router.post("/analyze", response_model=ReviewAnalysisResponse)
async def analyze_reviews(
    request: ReviewAnalyzeRequest, db: Session = Depends(get_db)
) -> ReviewAnalysisResponse:
    """
    Analyze product reviews for a given ASIN.
    Fetches reviews via SP-API and analyzes them using Claude AI.
    Results are saved to the database.
    """
    # Fetch reviews
    reviews = await spapi_client.get_reviews(
        asin=request.asin, max_count=request.max_reviews
    )

    if not reviews:
        raise HTTPException(
            status_code=404, detail=f"No reviews found for ASIN: {request.asin}"
        )

    # Analyze with AI
    analysis = await ai_analyzer.analyze_reviews(reviews=reviews, asin=request.asin)

    if "error" in analysis:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {analysis['error']}",
        )

    # Save to database
    db_record = ReviewAnalysis(
        asin=request.asin,
        negative_summary=json.dumps(
            analysis.get("negative_categories", []), ensure_ascii=False
        ),
        differentiation_points=json.dumps(
            analysis.get("differentiation_points", []), ensure_ascii=False
        ),
        gaps=json.dumps(analysis.get("gap_analysis", []), ensure_ascii=False),
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return ReviewAnalysisResponse(
        id=db_record.id,
        asin=request.asin,
        review_count=len(reviews),
        negative_categories=[
            NegativeCategory(**nc)
            for nc in analysis.get("negative_categories", [])
        ],
        gap_analysis=[
            GapAnalysisItem(**ga) for ga in analysis.get("gap_analysis", [])
        ],
        differentiation_points=[
            DifferentiationPoint(**dp)
            for dp in analysis.get("differentiation_points", [])
        ],
        strengths=[
            StrengthItem(**s) for s in analysis.get("strengths", [])
        ],
        weaknesses=[
            WeaknessItem(**w) for w in analysis.get("weaknesses", [])
        ],
        overall_sentiment=SentimentSummary(
            **analysis.get(
                "overall_sentiment",
                {
                    "positive_ratio": 0,
                    "neutral_ratio": 0,
                    "negative_ratio": 0,
                    "summary": "",
                },
            )
        ),
        created_at=db_record.created_at.isoformat(),
    )


@router.get("/history")
async def get_review_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    asin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get past review analysis results with optional ASIN filter."""
    query = db.query(ReviewAnalysis).order_by(ReviewAnalysis.created_at.desc())

    if asin:
        query = query.filter(ReviewAnalysis.asin == asin)

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    items: List[Dict[str, Any]] = []
    for r in results:
        negative_cats = []
        try:
            negative_cats = json.loads(r.negative_summary) if r.negative_summary else []
        except json.JSONDecodeError:
            pass

        diff_points = []
        try:
            diff_points = json.loads(r.differentiation_points) if r.differentiation_points else []
        except json.JSONDecodeError:
            pass

        items.append({
            "id": r.id,
            "asin": r.asin,
            "negative_category_count": len(negative_cats),
            "differentiation_point_count": len(diff_points),
            "created_at": r.created_at.isoformat(),
            "summary": negative_cats[0].get("category", "") if negative_cats else "",
        })

    return {"total": total, "results": items}


@router.get("/{analysis_id}")
async def get_review_analysis(
    analysis_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get a specific review analysis by ID."""
    record = db.query(ReviewAnalysis).filter(ReviewAnalysis.id == analysis_id).first()

    if not record:
        raise HTTPException(
            status_code=404, detail=f"Analysis not found: {analysis_id}"
        )

    negative_categories: List[Dict[str, Any]] = []
    try:
        negative_categories = json.loads(record.negative_summary) if record.negative_summary else []
    except json.JSONDecodeError:
        pass

    differentiation_points: List[Dict[str, Any]] = []
    try:
        differentiation_points = json.loads(record.differentiation_points) if record.differentiation_points else []
    except json.JSONDecodeError:
        pass

    gaps: List[Dict[str, Any]] = []
    try:
        gaps = json.loads(record.gaps) if record.gaps else []
    except json.JSONDecodeError:
        pass

    return {
        "id": record.id,
        "asin": record.asin,
        "negative_categories": negative_categories,
        "differentiation_points": differentiation_points,
        "gaps": gaps,
        "created_at": record.created_at.isoformat(),
    }
