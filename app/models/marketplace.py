from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ProductCategory(str, enum.Enum):
    MT4_INDICATOR = "mt4_indicator"
    MT5_INDICATOR = "mt5_indicator"
    EXPERT_ADVISOR = "expert_advisor"
    CRYPTO_BOT = "crypto_bot"
    TRADING_COURSE = "trading_course"
    SCRIPT = "script"

class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class MarketplaceProduct(Base):
    __tablename__ = "marketplace_products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT)
    downloads_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    tags = Column(JSON, nullable=True)  # Array of tags
    features = Column(JSON, nullable=True)  # Array of features
    requirements = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    demo_file_path = Column(String, nullable=True)
    screenshots = Column(JSON, nullable=True)  # Array of screenshot URLs
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    seller = relationship("User", back_populates="marketplace_products")
    purchases = relationship("ProductPurchase", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")

class ProductPurchase(Base):
    __tablename__ = "product_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("marketplace_products.id"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    download_count = Column(Integer, default=0)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    product = relationship("MarketplaceProduct", back_populates="purchases")

class ProductReview(Base):
    __tablename__ = "product_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("marketplace_products.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    product = relationship("MarketplaceProduct", back_populates="reviews")