#!/usr/bin/env python3
"""
Seed All Data — Full Seeder with Embeddings
============================================
This is the COMPREHENSIVE Python seeder that:
  1. Seeds all SQL data (categories, users, products, orders)
  2. Generates REAL 384-dimensional embeddings for each product
     using the all-MiniLM-L6-v2 sentence-transformer model
  3. Inserts the embeddings into the product_embeddings table
  4. Populates MongoDB with product specifications
  5. Primes the Redis cache with trending product scores

Usage:
    cd backend
    pip install sentence-transformers asyncpg motor redis
    # Installed versions: sentence-transformers>=6.0, asyncpg>=0.31, motor>=3.7, redis>=8.0
    python ../scripts/seed_all.py

Environment variables (override defaults):
    DATABASE_URL    postgresql://user:pass@localhost:5432/smartcommerce
    MONGO_URL       mongodb://localhost:27017
    REDIS_URL       redis://localhost:6379
"""

import asyncio
import os
import sys
import json
import uuid
import random
from pathlib import Path
from typing import List, Dict, Any

# ── Dependency check ────────────────────────────────────────────────────────
try:
    import asyncpg
    from sentence_transformers import SentenceTransformer
    import motor.motor_asyncio
    import redis.asyncio as aioredis
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install sentence-transformers asyncpg motor redis")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────
DB_URL    = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smartcommerce")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

PROJECT_ROOT = Path(__file__).parent.parent

# Embedding model — same one used by the search service
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ── Sample MongoDB product specifications ────────────────────────────────────
# These mirror the seed products in 02_seed_products.sql
PRODUCT_SPECS: Dict[str, Dict[str, Any]] = {
    "b0000000-0000-0000-0000-000000000001": {  # Dell XPS 15
        "processor": "Intel Core i9-13900H",
        "ram": "32GB DDR5",
        "storage": "1TB NVMe SSD",
        "display": "15.6-inch OLED 3.5K 120Hz",
        "gpu": "NVIDIA RTX 4070",
        "battery": "86Wh, Up to 10 hrs",
        "weight": "1.86 kg",
        "os": "Windows 11 Pro",
        "ports": ["2x Thunderbolt 4", "USB-A 3.0", "SD Card", "3.5mm audio"],
        "warranty": "1 year on-site",
        "highlights": ["4K OLED display", "NVIDIA RTX 4070", "Thin & light premium design"]
    },
    "b0000000-0000-0000-0000-000000000007": {  # Sony WH-1000XM5
        "driver_size": "30mm",
        "frequency_response": "4Hz - 40,000Hz",
        "noise_cancellation": "Dual Noise Sensor Technology",
        "battery_life": "30 hours (ANC on)",
        "quick_charge": "3 hours playback from 3-min charge",
        "connectivity": "Bluetooth 5.2, NFC, 3.5mm",
        "call_features": "4 beamforming microphones, AI-powered noise reduction",
        "weight": "250g",
        "foldable": False,
        "compatible_apps": ["Sony Headphones Connect (iOS/Android)"],
        "highlights": ["Best-in-class ANC", "30-hour battery", "8 mics for crystal-clear calls"]
    },
    "b0000000-0000-0000-0000-000000000012": {  # PS5
        "cpu": "AMD Zen 2 8-core 3.5GHz",
        "gpu": "AMD RDNA 2 10.28 TFLOPS",
        "storage": "825GB Custom NVMe SSD",
        "memory": "16GB GDDR6",
        "optical_drive": "Ultra HD Blu-ray",
        "resolution": "Up to 8K",
        "frame_rate": "Up to 120fps",
        "ray_tracing": True,
        "controller": "DualSense with haptic feedback",
        "highlights": ["Ray tracing", "4K 120fps gaming", "DualSense haptic controller"]
    },
}

# ── Helper text for embeddings (richer than just the title) ─────────────────
PRODUCT_EMBEDDING_TEXTS = {
    "b0000000-0000-0000-0000-000000000001": "Dell XPS 15 gaming laptop Intel Core i9 32GB RAM NVIDIA RTX 4070 OLED display",
    "b0000000-0000-0000-0000-000000000002": "Apple MacBook Pro 14 inch M3 Pro chip 18GB unified memory professional laptop",
    "b0000000-0000-0000-0000-000000000003": "ASUS ROG Strix gaming laptop AMD Ryzen 9 NVIDIA RTX 4080 144Hz high performance",
    "b0000000-0000-0000-0000-000000000004": "Samsung Galaxy S24 Ultra 5G smartphone AI camera 200MP titanium frame pen",
    "b0000000-0000-0000-0000-000000000005": "Apple iPhone 15 Pro Max 256GB titanium USB-C A17 Pro chip camera system",
    "b0000000-0000-0000-0000-000000000006": "Google Pixel 8 Pro AI photography Tensor G3 chip 7 years update guarantee",
    "b0000000-0000-0000-0000-000000000007": "Sony WH-1000XM5 wireless over-ear headphones industry leading noise cancelling 30 hours battery",
    "b0000000-0000-0000-0000-000000000008": "Bose QuietComfort 45 Bluetooth wireless noise cancelling headphones comfortable audio",
    "b0000000-0000-0000-0000-000000000009": "Apple AirPods Pro 2nd generation active noise cancellation spatial audio adaptive transparency",
    "b0000000-0000-0000-0000-000000000010": "Apple Watch Series 9 GPS fitness tracker heart rate ECG blood oxygen smartwatch",
    "b0000000-0000-0000-0000-000000000011": "Samsung Galaxy Watch 6 Classic health monitoring rotating bezel Wear OS 4",
    "b0000000-0000-0000-0000-000000000012": "Sony PlayStation 5 gaming console 4K 120fps ray tracing DualSense haptic controller",
    "b0000000-0000-0000-0000-000000000013": "Microsoft Xbox Series X gaming console 1TB quick resume 4K gaming Game Pass",
    "b0000000-0000-0000-0000-000000000014": "Nike Dri-FIT men training sports t-shirt moisture wicking gym workout shirt",
    "b0000000-0000-0000-0000-000000000015": "Adidas Essentials 3-Stripes tracksuit joggers athletic sportswear comfortable",
    "b0000000-0000-0000-0000-000000000016": "Nike Air Max 270 running shoes men lightweight breathable cushioning athletic",
    "b0000000-0000-0000-0000-000000000017": "Adidas Ultraboost 23 running shoes responsive Boost midsole energy return Primeknit",
    "b0000000-0000-0000-0000-000000000018": "Kore PVC adjustable dumbbells 10kg gym home workout strength training beginner",
    "b0000000-0000-0000-0000-000000000019": "Manduka PRO yoga mat thick non-slip 6mm premium professional studio pilates",
    "b0000000-0000-0000-0000-000000000020": "Wildcraft Trailblazer 45L trekking backpack waterproof outdoor hiking camping",
}


# ── Core seeder ─────────────────────────────────────────────────────────────

async def seed_embeddings(conn: asyncpg.Connection) -> None:
    """Generates and inserts real 384-dim embeddings for all seeded products."""
    print("\n🤖 Generating Product Embeddings...")
    print("   Loading all-MiniLM-L6-v2 (first run downloads ~90MB)...")

    model = SentenceTransformer(EMBEDDING_MODEL)
    print("   ✓ Model loaded.")

    product_ids = list(PRODUCT_EMBEDDING_TEXTS.keys())
    texts = [PRODUCT_EMBEDDING_TEXTS[pid] for pid in product_ids]

    print(f"   Encoding {len(texts)} products...")
    embeddings = model.encode(texts, normalize_embeddings=True)
    print(f"   ✓ Embeddings generated (shape: {embeddings.shape})")

    # Insert into PostgreSQL
    inserted = 0
    for product_id, embedding in zip(product_ids, embeddings):
        vec_str = "[" + ",".join(f"{x:.8f}" for x in embedding.tolist()) + "]"
        await conn.execute("""
            INSERT INTO product_embeddings (product_id, embedding)
            VALUES ($1, $2::vector)
            ON CONFLICT (product_id) DO UPDATE SET embedding = EXCLUDED.embedding;
        """, uuid.UUID(product_id), vec_str)
        inserted += 1

    print(f"   ✓ Inserted {inserted} embeddings into product_embeddings table.")


async def seed_mongodb(mongo_url: str) -> None:
    """Seeds product specifications into MongoDB."""
    print("\n📄 Seeding MongoDB Product Specs...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=3000)
        db = client["smartcommerce"]
        collection = db["product_specs"]

        for product_id, specs in PRODUCT_SPECS.items():
            specs["_id"] = product_id
            specs["product_id"] = product_id
            await collection.replace_one(
                {"_id": product_id},
                specs,
                upsert=True
            )

        count = await collection.count_documents({})
        print(f"   ✓ MongoDB: {count} product spec documents.")
        client.close()
    except Exception as exc:
        print(f"   ⚠ MongoDB unavailable (skipping): {exc}")


async def seed_redis(redis_url: str, conn: asyncpg.Connection) -> None:
    """Seeds Redis with initial trending scores for all products."""
    print("\n⚡ Seeding Redis Trending Scores...")
    try:
        r = aioredis.from_url(redis_url, decode_responses=True)

        # Fetch all product IDs from PostgreSQL
        rows = await conn.fetch("SELECT id, rating_avg, review_count FROM products WHERE is_active = TRUE;")

        for row in rows:
            # Trending score = rating * log(review_count + 1) * random noise
            import math
            score = float(row["rating_avg"]) * math.log(float(row["review_count"]) + 1) * (0.8 + random.random() * 0.4)
            await r.zadd("trending:products", {str(row["id"]): round(score, 4)})

        count = await r.zcard("trending:products")
        print(f"   ✓ Redis: {count} products in trending:products ZSET.")
        await r.aclose()
    except Exception as exc:
        print(f"   ⚠ Redis unavailable (skipping): {exc}")


async def run_sql_seeds(conn: asyncpg.Connection) -> None:
    """Runs the SQL seed files via asyncpg (idempotent)."""
    print("\n🗄️  Running SQL Seed Files...")
    seed_dir = PROJECT_ROOT / "database" / "seed"
    for filename in ["01_seed_reference_data.sql", "02_seed_products.sql", "03_seed_users_and_orders.sql"]:
        path = seed_dir / filename
        if path.exists():
            sql = path.read_text(encoding="utf-8")
            # Strip lines the psql client handles but asyncpg doesn't
            lines = [l for l in sql.splitlines() if not l.strip().startswith("\\")]
            try:
                await conn.execute("\n".join(lines))
                print(f"   ✓ {filename}")
            except Exception as exc:
                print(f"   ⚠ {filename}: {exc}")


async def main() -> None:
    print("🌱 SmartCommerce AI — Full Database Seeder")
    print(f"   PostgreSQL: {DB_URL.split('@')[-1]}")
    print(f"   MongoDB   : {MONGO_URL}")
    print(f"   Redis     : {REDIS_URL}")

    # Connect to PostgreSQL
    try:
        conn = await asyncpg.connect(DB_URL)
    except Exception as exc:
        print(f"\n❌ Cannot connect to PostgreSQL: {exc}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is correct.")
        sys.exit(1)

    try:
        await run_sql_seeds(conn)
        await seed_embeddings(conn)
        await seed_mongodb(MONGO_URL)
        await seed_redis(REDIS_URL, conn)

        print("\n✅ Seeding complete! Your SmartCommerce AI database is ready.")
        print("\n   Next steps:")
        print("   1. cd backend && uvicorn app.main:app --reload")
        print("   2. Open http://localhost:8000/docs to test the API")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
