from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.models.marketplace import ProductCategory, ProductStatus

class MarketplaceProductBase(BaseModel):
    title: str
    description: str
    category: ProductCategory
    price: float
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v

class MarketplaceProductCreate(MarketplaceProductBase):
    pass

class MarketplaceProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[ProductStatus] = None

class MarketplaceProductInDB(MarketplaceProductBase):
    id: int
    seller_id: int
    status: ProductStatus
    downloads_count: int
    rating_average: float
    rating_count: int
    tags: Optional[List[str]]
    features: Optional[List[str]]
    requirements: Optional[str]
    file_path: Optional[str]
    demo_file_path: Optional[str]
    screenshots: Optional[List[str]]
    video_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True