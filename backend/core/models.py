from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy import Column, String, Integer, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid
from typing import Optional



Base = declarative_base()

class GadgetProduct(BaseModel):
    """Data Contract for gadgetph.com"""
    title: str
    price: str = "0"  # String allows "75,990" or "Check Site"
    currency: str = "PHP"
    address: Optional[str] = "Shopee PH"
    listing_url: Optional[HttpUrl] = None
    
# --- DATABASE MODELS (SQLAlchemy) ---
class ScrapedRecord(Base):
    """The final product stored in PostgreSQL"""
    __tablename__ = "scraped_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, index=True) # For Multi-tenancy
    project_id = Column(String, index=True)
    source_url = Column(String, nullable=False)
    # JSONB field allows the machine to be 'Universal' (Amazon, Real Estate, etc.)
    payload = Column(JSON, nullable=False) 
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- VALIDATION SCHEMAS (Pydantic) ---
class PropertyListing(BaseModel):
    """
    Example 'Data Contract' for a Real Estate client.
    If the scraper misses a field, Pydantic raises a ValidationError.
    """
    title: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    address: str
    listing_url: HttpUrl
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class AmazonProduct(BaseModel):
    """Example 'Data Contract' for an E-commerce client."""
    asin: str
    product_name: str
    price_string: str
    stock_status: bool

