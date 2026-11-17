import asyncio
import time
import uuid
import sys
import os

# Add /app to sys.path so it works locally if executed
sys.path.append("/app")

from app.core.database import AsyncSessionLocal
from app.services.search import SearchService, get_embedding_model
from app.models.product import Product, ProductVariant, Category, ProductEmbedding
from app.models.inventory import Inventory
from app.services.inventory import InventoryService

class MockMongoDb:
    class _MockCollection:
        async def find_one(self, query):
            return {}
    product_multimedia = _MockCollection()
    product_metadata = _MockCollection()

async def evaluate_latency():
    print("\n--- PHASE 3: PERFORMANCE EVALUATION ---")
    
    cat_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    var_id = uuid.uuid4()
    
    # Pre-warm model
    model = get_embedding_model()
    if not model:
        print("Model failed to load.")
        return

    # Seed data
    async with AsyncSessionLocal() as session:
        cat = Category(id=cat_id, name="Test Cat", slug=f"test-{uuid.uuid4().hex}")
        p = Product(id=prod_id, category_id=cat_id, sku=f"SKU-{uuid.uuid4().hex}", title="Test Product", slug=f"test-p-{uuid.uuid4().hex}", brand="Test", base_price=10.0, is_active=True)
        v = ProductVariant(id=var_id, product_id=prod_id, sku=f"VAR-{uuid.uuid4().hex}", title="Var", price_override=10.0)
        inv = Inventory(id=uuid.uuid4(), variant_id=var_id, on_hand=1000, reserved=0)
        
        vec = model.encode(p.title).tolist()
        emb = ProductEmbedding(product_id=prod_id, embedding=vec)
        
        session.add_all([cat, p, v, inv, emb])
        await session.commit()

    # Measure Transaction Latency
    async with AsyncSessionLocal() as session:
        start_time = time.time()
        # Simulate a checkout flow deducting stock
        await InventoryService.reserve_stock(session, var_id, 1)
        await session.commit()
        tx_latency = (time.time() - start_time) * 1000
        print(f"Transaction Latency (Checkout Flow + DB Lock): {tx_latency:.2f} ms")

    # Measure Search Retrieval
    async with AsyncSessionLocal() as session:
        start_time = time.time()
        # Simulate hybrid search
        res = await SearchService.search_semantic(session, MockMongoDb(), "Test", limit=5)
        search_latency = (time.time() - start_time) * 1000
        print(f"Search Retrieval Latency (pgvector Cosine Distance): {search_latency:.2f} ms")

if __name__ == "__main__":
    asyncio.run(evaluate_latency())
