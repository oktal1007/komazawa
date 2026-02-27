"""OEM factory database router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db, Factory
from backend.services.scraper import scrape_factory_data

router = APIRouter(prefix="/api/factories", tags=["factories"])


class FactoryCreate(BaseModel):
    name: str
    prefecture: str
    categories: str
    dosage_forms: str
    min_lot: int = 1000
    url: str = ""
    contact_url: str = ""
    certifications: str = ""
    features: str = ""


class FactoryUpdate(BaseModel):
    name: Optional[str] = None
    prefecture: Optional[str] = None
    categories: Optional[str] = None
    dosage_forms: Optional[str] = None
    min_lot: Optional[int] = None
    url: Optional[str] = None
    contact_url: Optional[str] = None
    certifications: Optional[str] = None
    features: Optional[str] = None


class MemoUpdate(BaseModel):
    memo: str


def factory_to_dict(f: Factory) -> dict:
    return {
        "id": f.id,
        "name": f.name,
        "prefecture": f.prefecture,
        "categories": f.categories or "",
        "dosage_forms": f.dosage_forms or "",
        "min_lot": f.min_lot or 0,
        "url": f.url or "",
        "contact_url": f.contact_url or "",
        "certifications": f.certifications or "",
        "features": f.features or "",
        "is_favorite": f.is_favorite or False,
        "memo": f.memo or "",
        "created_at": f.created_at.isoformat() if f.created_at else "",
    }


@router.get("")
async def list_factories(
    category: Optional[str] = None,
    prefecture: Optional[str] = None,
    certification: Optional[str] = None,
    keyword: Optional[str] = None,
    favorite_only: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List factories with filters."""
    query = db.query(Factory)

    # If no factories in DB, seed with demo data
    if query.count() == 0:
        demo_factories = await scrape_factory_data()
        for f in demo_factories:
            record = Factory(
                name=f["name"],
                prefecture=f["prefecture"],
                categories=f["categories"],
                dosage_forms=f["dosage_forms"],
                min_lot=f["min_lot"],
                url=f["url"],
                contact_url=f["contact_url"],
                certifications=f["certifications"],
                features=f["features"],
                is_favorite=False,
                memo="",
                created_at=datetime.utcnow(),
            )
            db.add(record)
        db.commit()
        query = db.query(Factory)

    if category:
        query = query.filter(Factory.categories.contains(category))
    if prefecture:
        query = query.filter(Factory.prefecture == prefecture)
    if certification:
        query = query.filter(Factory.certifications.contains(certification))
    if keyword:
        query = query.filter(
            Factory.name.contains(keyword)
            | Factory.features.contains(keyword)
            | Factory.categories.contains(keyword)
            | Factory.dosage_forms.contains(keyword)
        )
    if favorite_only:
        query = query.filter(Factory.is_favorite == True)

    factories = query.order_by(Factory.name).all()
    return [factory_to_dict(f) for f in factories]


@router.get("/compare")
async def compare_factories(
    ids: list[int] = Query(...),
    db: Session = Depends(get_db),
):
    """Compare multiple factories."""
    factories = db.query(Factory).filter(Factory.id.in_(ids)).all()
    return [factory_to_dict(f) for f in factories]


@router.get("/{factory_id}")
async def get_factory(factory_id: int, db: Session = Depends(get_db)):
    """Get factory details."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        return {"error": "Not found"}
    return factory_to_dict(factory)


@router.post("")
async def create_factory(data: FactoryCreate, db: Session = Depends(get_db)):
    """Add a factory manually."""
    factory = Factory(
        name=data.name,
        prefecture=data.prefecture,
        categories=data.categories,
        dosage_forms=data.dosage_forms,
        min_lot=data.min_lot,
        url=data.url,
        contact_url=data.contact_url,
        certifications=data.certifications,
        features=data.features,
        is_favorite=False,
        memo="",
        created_at=datetime.utcnow(),
    )
    db.add(factory)
    db.commit()
    db.refresh(factory)
    return factory_to_dict(factory)


@router.put("/{factory_id}")
async def update_factory(
    factory_id: int, data: FactoryUpdate, db: Session = Depends(get_db)
):
    """Update factory information."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        return {"error": "Not found"}

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(factory, field, value)

    db.commit()
    db.refresh(factory)
    return factory_to_dict(factory)


@router.put("/{factory_id}/favorite")
async def toggle_favorite(factory_id: int, db: Session = Depends(get_db)):
    """Toggle factory favorite status."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        return {"error": "Not found"}

    factory.is_favorite = not factory.is_favorite
    db.commit()
    db.refresh(factory)
    return factory_to_dict(factory)


@router.put("/{factory_id}/memo")
async def update_memo(
    factory_id: int, data: MemoUpdate, db: Session = Depends(get_db)
):
    """Update factory memo."""
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        return {"error": "Not found"}

    factory.memo = data.memo
    db.commit()
    db.refresh(factory)
    return factory_to_dict(factory)


@router.post("/scrape")
async def trigger_scrape(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Trigger factory scraping."""
    factories = await scrape_factory_data(query)
    count = 0
    for f in factories:
        existing = db.query(Factory).filter(Factory.name == f["name"]).first()
        if not existing:
            record = Factory(
                name=f["name"],
                prefecture=f["prefecture"],
                categories=f["categories"],
                dosage_forms=f["dosage_forms"],
                min_lot=f["min_lot"],
                url=f["url"],
                contact_url=f["contact_url"],
                certifications=f["certifications"],
                features=f["features"],
                is_favorite=False,
                memo="",
                created_at=datetime.utcnow(),
            )
            db.add(record)
            count += 1
    db.commit()
    return {"status": "ok", "new_factories": count}
