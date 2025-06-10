from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from ..models.marketplace import (
    MarketplaceProduct, ProductPurchase, ProductReview,
    ProductCategory, ProductStatus
)

class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(
        self,
        title: str,
        description: str,
        category: ProductCategory,
        price: float,
        seller_id: int
    ) -> MarketplaceProduct:
        db_product = MarketplaceProduct(
            title=title,
            description=description,
            category=category,
            price=price,
            seller_id=seller_id
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def get_products(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[ProductCategory] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None
    ) -> List[MarketplaceProduct]:
        query = self.db.query(MarketplaceProduct).filter(
            MarketplaceProduct.status == ProductStatus.APPROVED
        )
        
        if category:
            query = query.filter(MarketplaceProduct.category == category)
        
        if min_price is not None:
            query = query.filter(MarketplaceProduct.price >= min_price)
        
        if max_price is not None:
            query = query.filter(MarketplaceProduct.price <= max_price)
        
        if search:
            query = query.filter(
                or_(
                    MarketplaceProduct.title.ilike(f"%{search}%"),
                    MarketplaceProduct.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(MarketplaceProduct.created_at)).offset(skip).limit(limit).all()
    
    def get_product_by_id(self, product_id: int) -> Optional[MarketplaceProduct]:
        return self.db.query(MarketplaceProduct).filter(
            and_(
                MarketplaceProduct.id == product_id,
                MarketplaceProduct.status == ProductStatus.APPROVED
            )
        ).first()
    
    def purchase_product(self, product_id: int, user_id: int) -> Optional[ProductPurchase]:
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Check if already purchased
        existing_purchase = self.db.query(ProductPurchase).filter(
            and_(
                ProductPurchase.product_id == product_id,
                ProductPurchase.user_id == user_id
            )
        ).first()
        
        if existing_purchase:
            return existing_purchase
        
        purchase = ProductPurchase(
            product_id=product_id,
            user_id=user_id,
            amount_paid=product.price
        )
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        
        # Update download count
        product.downloads_count += 1
        self.db.commit()
        
        return purchase
    
    def get_user_purchases(self, user_id: int) -> List[ProductPurchase]:
        return self.db.query(ProductPurchase).filter(
            ProductPurchase.user_id == user_id
        ).order_by(desc(ProductPurchase.purchased_at)).all()
    
    def create_product_review(
        self,
        product_id: int,
        user_id: int,
        rating: int,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Optional[ProductReview]:
        # Check if user purchased the product
        purchase = self.db.query(ProductPurchase).filter(
            and_(
                ProductPurchase.product_id == product_id,
                ProductPurchase.user_id == user_id
            )
        ).first()
        
        if not purchase:
            return None
        
        # Check if already reviewed
        existing_review = self.db.query(ProductReview).filter(
            and_(
                ProductReview.product_id == product_id,
                ProductReview.user_id == user_id
            )
        ).first()
        
        if existing_review:
            return None
        
        review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            title=title,
            content=content,
            is_verified_purchase=True
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        # Update product rating
        self._update_product_rating(product_id)
        
        return review
    
    def _update_product_rating(self, product_id: int):
        reviews = self.db.query(ProductReview).filter(
            ProductReview.product_id == product_id
        ).all()
        
        if reviews:
            average_rating = sum(review.rating for review in reviews) / len(reviews)
            product = self.get_product_by_id(product_id)
            product.rating_average = average_rating
            product.rating_count = len(reviews)
            self.db.commit()