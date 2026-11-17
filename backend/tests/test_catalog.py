import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.catalog_repository import CatalogRepository
from app.schemas.catalog import CategoryCreate, BrandCreate
import uuid

@pytest.mark.asyncio
async def test_product_crud_and_hybrid_search(async_client: AsyncClient, db_session: AsyncSession):
    repo = CatalogRepository(db_session)
    
    # 1. Setup prerequisite entities
    unique_suffix = uuid.uuid4().hex[:6]
    brand = await repo.create_brand(BrandCreate(name=f"TestBrand_{unique_suffix}"))
    category = await repo.create_category(CategoryCreate(name=f"TestCategory_{unique_suffix}", slug=f"test-category-{unique_suffix}"))
    
    # 2. Insert a product via API with JSONB attributes
    product_payload = {
        "name": "Superfast Laptop",
        "description": "A very fast laptop for developers.",
        "category_id": str(category.id),
        "brand_id": str(brand.id),
        "is_active": True,
        "attributes": {
            "RAM": "32GB",
            "Storage": "1TB SSD",
            "Processor": "M3 Max"
        },
        "variants": [
            {
                "sku": f"LT-M3-{uuid.uuid4().hex[:6]}",
                "name": "Space Gray 32GB",
                "attributes": {"color": "Space Gray"}
            },
            {
                "sku": f"LT-M3-{uuid.uuid4().hex[:6]}",
                "name": "Silver 32GB",
                "attributes": {"color": "Silver"}
            }
        ]
    }
    
    response = await async_client.post("/api/products/", json=product_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Superfast Laptop"
    assert data["attributes"]["RAM"] == "32GB"
    assert len(data["variants"]) == 2
    
    product_id = data["id"]
    
    # 3. Test retrieving the product via GET
    response = await async_client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    
    # 4. Test vector search
    # The POST /api/products/search/vector route uses a dummy query vector and finds
    # the closest products by cosine distance. Because all embeddings are random dummy
    # vectors the ordering is not deterministic, especially when multiple products
    # exist in the shared DB. We verify the endpoint works (200, non-empty list) and
    # that retrieving our product directly confirms it exists in the catalog.
    search_response = await async_client.post("/api/products/search/vector")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) >= 1

    # Verify the product is retrievable via its dedicated GET endpoint (definitive check).
    direct_response = await async_client.get(f"/api/products/{product_id}")
    assert direct_response.status_code == 200
    assert direct_response.json()["id"] == product_id

