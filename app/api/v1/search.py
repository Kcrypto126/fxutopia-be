from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ...database import get_db
from ...utils.search import SearchService

router = APIRouter()

@router.get("/")
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Number of results per content type"),
    content_types: Optional[List[str]] = Query(None, description="Content types to search"),
    db: Session = Depends(get_db)
):
    """Global search across all content types"""
    search_service = SearchService(db)
    return search_service.global_search(q, limit, content_types)

@router.get("/posts")
async def search_posts(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Search community posts"""
    search_service = SearchService(db)
    return search_service.search_posts(q, limit)

@router.get("/articles")
async def search_articles(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Search educational articles"""
    search_service = SearchService(db)
    return search_service.search_articles(q, limit)

@router.get("/products")
async def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Search marketplace products"""
    search_service = SearchService(db)
    return search_service.search_products(q, limit)