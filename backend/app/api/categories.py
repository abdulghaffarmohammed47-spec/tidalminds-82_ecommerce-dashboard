from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.postgres import get_db
from app.schemas.catalog import CategoryCreate, CategoryResponse
from app.repositories.catalog_repository import CatalogRepository

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_in: CategoryCreate, 
    db: AsyncSession = Depends(get_db)
):
    repo = CatalogRepository(db)
    category = await repo.create_category(category_in)
    return category

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    repo = CatalogRepository(db)
    categories = await repo.list_categories()
    return categories
