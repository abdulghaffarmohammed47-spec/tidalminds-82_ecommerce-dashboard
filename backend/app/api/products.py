from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.postgres import get_db
from app.schemas.catalog import ProductCreate, ProductResponse, BrandCreate, BrandResponse
from app.repositories.catalog_repository import CatalogRepository
from app.services.search import SearchService

router = APIRouter()


def product_response(product) -> ProductResponse:
    response = ProductResponse.model_validate(product)
    response.price = getattr(product, "price", None)
    return response

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_in: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    repo = CatalogRepository(db)
    product = await repo.create_product_with_variants(product_in)
    
    # For S1 Verification: Automatically generate a dummy embedding for semantic search
    search_service = SearchService(db)
    await search_service.generate_dummy_embedding_for_product(product.id)
    
    return product_response(product)

@router.post("/brands", response_model=BrandResponse)
async def create_brand(
    brand_in: BrandCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = CatalogRepository(db)
    brand = await repo.create_brand(brand_in)
    return brand

@router.get("/", response_model=List[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    repo = CatalogRepository(db)
    products = await repo.list_products()
    return [product_response(product) for product in products]

@router.get("/{product_id}/similar", response_model=List[ProductResponse])
async def get_similar_products(product_id: uuid.UUID, limit: int = 4, db: AsyncSession = Depends(get_db)):
    repo = CatalogRepository(db)
    products = await repo.get_similar_products(product_id, limit=min(max(limit, 1), 20))
    return [product_response(product) for product in products]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = CatalogRepository(db)
    product = await repo.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_response(product)

@router.post("/search/vector", response_model=List[ProductResponse])
async def vector_search(db: AsyncSession = Depends(get_db)):
    """
    Simulates a hybrid search. We generate a dummy query vector,
    and find the closest products using pgvector.
    """
    repo = CatalogRepository(db)
    search_service = SearchService(db)
    
    query_vector = search_service.get_dummy_query_vector()
    products = await repo.search_products_by_vector(query_vector, limit=5)
    
    return [product_response(product) for product in products]
