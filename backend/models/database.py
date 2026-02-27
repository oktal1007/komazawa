"""
SQLAlchemy models and database configuration for OEM Product Research Dashboard.
Uses SQLite as the database backend.
"""

from datetime import datetime
from typing import Generator

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    DateTime,
    Date,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./oem_research.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class MarketResearch(Base):
    """Market research results from keyword searches."""

    __tablename__ = "market_research"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    keyword: str = Column(String(255), nullable=False, index=True)
    asin: str = Column(String(20), nullable=False, index=True)
    title: str = Column(String(500), nullable=False)
    brand: str = Column(String(255), nullable=True)
    price: float = Column(Float, nullable=True)
    review_count: int = Column(Integer, nullable=True)
    rating: float = Column(Float, nullable=True)
    monthly_sales: int = Column(Integer, nullable=True)
    monthly_revenue: float = Column(Float, nullable=True)
    market_score: float = Column(Float, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class ReviewAnalysis(Base):
    """AI-powered review analysis results."""

    __tablename__ = "review_analysis"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asin: str = Column(String(20), nullable=False, index=True)
    negative_summary: str = Column(Text, nullable=True)
    differentiation_points: str = Column(Text, nullable=True)
    gaps: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class Factory(Base):
    """OEM factory information."""

    __tablename__ = "factories"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)
    prefecture: str = Column(String(50), nullable=True)
    categories: str = Column(Text, nullable=True)  # JSON string
    dosage_forms: str = Column(Text, nullable=True)  # JSON string
    min_lot: int = Column(Integer, nullable=True)
    url: str = Column(String(500), nullable=True)
    contact_url: str = Column(String(500), nullable=True)
    certifications: str = Column(Text, nullable=True)  # JSON string
    features: str = Column(Text, nullable=True)
    is_favorite: bool = Column(Boolean, default=False, nullable=False)
    memo: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class IngredientTrend(Base):
    """Weekly ingredient trend tracking data."""

    __tablename__ = "ingredient_trends"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ingredient_name: str = Column(String(255), nullable=False, index=True)
    mention_count: int = Column(Integer, nullable=True)
    growth_rate: float = Column(Float, nullable=True)
    market_size: float = Column(Float, nullable=True)
    week_date = Column(Date, nullable=True)


class ProfitSimulation(Base):
    """Saved profit simulation results."""

    __tablename__ = "profit_simulations"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_name: str = Column(String(255), nullable=False)
    selling_price: float = Column(Float, nullable=False)
    manufacturing_cost: float = Column(Float, nullable=False)
    packaging_cost: float = Column(Float, nullable=False)
    fba_fee: float = Column(Float, nullable=False)
    ad_rate: float = Column(Float, nullable=False)
    target_sales: int = Column(Integer, nullable=False)
    profit_per_unit: float = Column(Float, nullable=True)
    profit_margin: float = Column(Float, nullable=True)
    monthly_profit: float = Column(Float, nullable=True)
    roi: float = Column(Float, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
