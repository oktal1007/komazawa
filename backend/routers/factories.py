"""
Factory management router for OEM factory data.
Provides endpoints for listing, filtering, adding, updating,
comparing, and scraping factory information.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import Factory, get_db
from backend.services.scraper import WebScraper

router = APIRouter(prefix="/api/factories", tags=["factories"])

scraper = WebScraper()


# --- Pydantic Schemas ---


class FactoryCreate(BaseModel):
    """Schema for creating a new factory."""

    name: str = Field(..., min_length=1, max_length=255)
    prefecture: Optional[str] = Field(None, max_length=50)
    categories: Optional[List[str]] = None
    dosage_forms: Optional[List[str]] = None
    min_lot: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = Field(None, max_length=500)
    contact_url: Optional[str] = Field(None, max_length=500)
    certifications: Optional[List[str]] = None
    features: Optional[str] = None
    memo: Optional[str] = None


class FactoryUpdate(BaseModel):
    """Schema for updating a factory."""

    name: Optional[str] = Field(None, max_length=255)
    prefecture: Optional[str] = Field(None, max_length=50)
    categories: Optional[List[str]] = None
    dosage_forms: Optional[List[str]] = None
    min_lot: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = Field(None, max_length=500)
    contact_url: Optional[str] = Field(None, max_length=500)
    certifications: Optional[List[str]] = None
    features: Optional[str] = None
    memo: Optional[str] = None


class FavoriteToggle(BaseModel):
    """Schema for toggling favorite status."""

    is_favorite: bool


class MemoUpdate(BaseModel):
    """Schema for updating memo."""

    memo: str


class FactoryResponse(BaseModel):
    """Response schema for factory data."""

    id: int
    name: str
    prefecture: Optional[str] = None
    categories: Optional[List[str]] = None
    dosage_forms: Optional[List[str]] = None
    min_lot: Optional[str] = None
    url: Optional[str] = None
    contact_url: Optional[str] = None
    certifications: Optional[List[str]] = None
    features: Optional[str] = None
    is_favorite: bool = False
    memo: Optional[str] = None
    created_at: str


class ScrapeRequest(BaseModel):
    """Request schema for factory scraping."""

    query: str = Field(
        "OEM サプリメント 製造",
        description="Search query for scraping",
    )


class ScrapeResponse(BaseModel):
    """Response schema for scrape results."""

    status: str
    factories_found: int
    factories_added: int
    message: str


# --- Helper Functions ---


def _factory_to_response(factory: Factory) -> Dict[str, Any]:
    """Convert a Factory ORM object to a response dict."""
    categories: Optional[List[str]] = None
    if factory.categories:
        try:
            categories = json.loads(factory.categories)
        except json.JSONDecodeError:
            categories = [factory.categories]

    dosage_forms: Optional[List[str]] = None
    if factory.dosage_forms:
        try:
            dosage_forms = json.loads(factory.dosage_forms)
        except json.JSONDecodeError:
            dosage_forms = [factory.dosage_forms]

    certifications: Optional[List[str]] = None
    if factory.certifications:
        try:
            certifications = json.loads(factory.certifications)
        except json.JSONDecodeError:
            certifications = [factory.certifications]

    return {
        "id": factory.id,
        "name": factory.name,
        "prefecture": factory.prefecture,
        "categories": categories,
        "dosage_forms": dosage_forms,
        "min_lot": factory.min_lot,
        "url": factory.url,
        "contact_url": factory.contact_url,
        "certifications": certifications,
        "features": factory.features,
        "is_favorite": factory.is_favorite,
        "memo": factory.memo,
        "created_at": factory.created_at.isoformat(),
    }


def _seed_demo_factories(db: Session) -> None:
    """Seed the database with demo factory data if empty."""
    existing = db.query(Factory).count()
    if existing > 0:
        return

    mock_data = WebScraper()._get_mock_factory_data()
    for f in mock_data:
        factory = Factory(
            name=f["name"],
            prefecture=f.get("prefecture"),
            categories=json.dumps(f.get("categories", []), ensure_ascii=False),
            dosage_forms=json.dumps(f.get("dosage_forms", []), ensure_ascii=False),
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

    db.commit()


# --- Endpoints ---


@router.get("")
async def list_factories(
    category: Optional[str] = Query(None, description="Filter by category"),
    prefecture: Optional[str] = Query(None, description="Filter by prefecture"),
    certification: Optional[str] = Query(None, description="Filter by certification"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    favorite_only: bool = Query(False, description="Show only favorites"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    List factories with optional filters.
    Seeds demo data on first access if database is empty.
    """
    _seed_demo_factories(db)

    query = db.query(Factory).order_by(Factory.is_favorite.desc(), Factory.name)

    if favorite_only:
        query = query.filter(Factory.is_favorite == True)

    if prefecture:
        query = query.filter(Factory.prefecture == prefecture)

    if category:
        query = query.filter(Factory.categories.contains(category))

    if certification:
        query = query.filter(Factory.certifications.contains(certification))

    if keyword:
        query = query.filter(
            (Factory.name.contains(keyword))
            | (Factory.features.contains(keyword))
            | (Factory.categories.contains(keyword))
        )

    total = query.count()
    factories = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "factories": [_factory_to_response(f) for f in factories],
    }


@router.get("/compare")
async def compare_factories(
    ids: str = Query(..., description="Comma-separated factory IDs"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Compare multiple factories by their IDs."""
    try:
        factory_ids = [int(id_str.strip()) for id_str in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid factory IDs format")

    if len(factory_ids) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 factories required for comparison"
        )

    if len(factory_ids) > 5:
        raise HTTPException(
            status_code=400, detail="Maximum 5 factories can be compared"
        )

    factories = db.query(Factory).filter(Factory.id.in_(factory_ids)).all()

    if len(factories) != len(factory_ids):
        raise HTTPException(status_code=404, detail="One or more factories not found")

    comparison: List[Dict[str, Any]] = []
    for f in factories:
        data = _factory_to_response(f)
        comparison.append(data)

    # Generate comparison summary
    all_certs: Dict[str, List[str]] = {}
    for f_data in comparison:
        for cert in f_data.get("certifications", []) or []:
            if cert not in all_certs:
                all_certs[cert] = []
            all_certs[cert].append(f_data["name"])

    all_forms: Dict[str, List[str]] = {}
    for f_data in comparison:
        for form in f_data.get("dosage_forms", []) or []:
            if form not in all_forms:
                all_forms[form] = []
            all_forms[form].append(f_data["name"])

    return {
        "factories": comparison,
        "comparison_summary": {
            "certification_matrix": all_certs,
            "dosage_form_matrix": all_forms,
            "factory_count": len(comparison),
        },
    }


@router.get("/{factory_id}")
async def get_factory(
    factory_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed information for a specific factory."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    return _factory_to_response(factory)


@router.post("")
async def create_factory(
    data: FactoryCreate, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Add a new factory manually."""
    factory = Factory(
        name=data.name,
        prefecture=data.prefecture,
        categories=json.dumps(data.categories or [], ensure_ascii=False),
        dosage_forms=json.dumps(data.dosage_forms or [], ensure_ascii=False),
        min_lot=data.min_lot,
        url=data.url,
        contact_url=data.contact_url,
        certifications=json.dumps(data.certifications or [], ensure_ascii=False),
        features=data.features,
        is_favorite=False,
        memo=data.memo,
    )
    db.add(factory)
    db.commit()
    db.refresh(factory)

    return _factory_to_response(factory)


@router.put("/{factory_id}")
async def update_factory(
    factory_id: int, data: FactoryUpdate, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update an existing factory."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field in ("categories", "dosage_forms", "certifications"):
            if value is not None:
                setattr(factory, field, json.dumps(value, ensure_ascii=False))
        else:
            setattr(factory, field, value)

    db.commit()
    db.refresh(factory)

    return _factory_to_response(factory)


@router.put("/{factory_id}/favorite")
async def toggle_favorite(
    factory_id: int, data: FavoriteToggle, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Toggle favorite status for a factory."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    factory.is_favorite = data.is_favorite
    db.commit()
    db.refresh(factory)

    return _factory_to_response(factory)


@router.put("/{factory_id}/memo")
async def update_memo(
    factory_id: int, data: MemoUpdate, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update memo for a factory."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    factory.memo = data.memo
    db.commit()
    db.refresh(factory)

    return _factory_to_response(factory)


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_factories(
    request: ScrapeRequest, db: Session = Depends(get_db)
) -> ScrapeResponse:
    """
    Trigger factory data scraping.
    Scrapes OEM factory information and adds new entries to the database.
    """
    scraped_data = await scraper.scrape_factory_data(query=request.query)

    added = 0
    for f in scraped_data:
        # Check if factory already exists by name
        existing = db.query(Factory).filter(Factory.name == f["name"]).first()
        if existing:
            continue

        factory = Factory(
            name=f["name"],
            prefecture=f.get("prefecture"),
            categories=json.dumps(f.get("categories", []), ensure_ascii=False),
            dosage_forms=json.dumps(f.get("dosage_forms", []), ensure_ascii=False),
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

    return ScrapeResponse(
        status="success",
        factories_found=len(scraped_data),
        factories_added=added,
        message=f"Found {len(scraped_data)} factories, added {added} new entries.",
    )
