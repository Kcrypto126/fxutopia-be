from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database import get_db
from ...models.user import User
from ...models.marketplace import ProductCategory, ProductStatus
from ...core.deps import get_current_active_user, get_current_admin_user
from ...services.marketplace_service import MarketplaceService

router = APIRouter()

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
    title: str,
    description: str,
    category: ProductCategory,
    price: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create marketplace product"""
    marketplace_service = MarketplaceService(db)
    return marketplace_service.create_product(
        title=title,
        description=description,
        category=category,
        price=price,
        seller_id=current_user.id
    )

@router.get("/products")
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[ProductCategory] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get marketplace products"""
    marketplace_service = MarketplaceService(db)
    return marketplace_service.get_products(
        skip=skip,
        limit=limit,
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search
    )

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    marketplace_service = MarketplaceService(db)
    product = marketplace_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products/{product_id}/purchase")
async def purchase_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Purchase a product"""
    marketplace_service = MarketplaceService(db)
    purchase = marketplace_service.purchase_product(product_id, current_user.id)
    if not purchase:
        raise HTTPException(status_code=400, detail="Purchase failed")
    return purchase

@router.get("/my-purchases")
async def get_my_purchases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's purchases"""
    marketplace_service = MarketplaceService(db)
    return marketplace_service.get_user_purchases(current_user.id)

@router.post("/products/{product_id}/review")
async def create_product_review(
    product_id: int,
    rating: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create product review"""
    marketplace_service = MarketplaceService(db)
    review = marketplace_service.create_product_review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        title=title,
        content=content
    )
    if not review:
        raise HTTPException(status_code=400, detail="Unable to create review")
    return review