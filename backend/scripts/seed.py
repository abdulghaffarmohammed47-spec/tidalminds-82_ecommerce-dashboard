import asyncio
import uuid
import sys
import os
import random
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from faker import Faker

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
# pyrefly: ignore [missing-import]
from app.models.user import User
# pyrefly: ignore [missing-import]
from app.models.seller import Seller, SellerProduct
# pyrefly: ignore [missing-import]
from app.models.product import Category, Brand, Product, ProductVariant, ProductEmbedding
# pyrefly: ignore [missing-import]
from app.models.inventory import Warehouse, Inventory
from app.core.mongo import get_mongo_db
from app.core.security import get_password_hash

# Try to import SentenceTransformer for vector embeddings (IDE parsing fix)
try:
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: SentenceTransformer not loaded for seed: {e}")
    embed_model = None

fake = Faker()
Faker.seed(42)
random.seed(42)

async def seed_db():
    async with AsyncSessionLocal() as db:
        print("Clearing existing PostgreSQL data...")
        await db.execute(text("TRUNCATE TABLE inventory_movements, order_items, orders, inventory, seller_products, product_variants, product_embeddings, products, brands, categories, sellers, addresses, users CASCADE"))
        await db.commit()

        print("Creating Users...")
        # Create Admin
        admin_id = uuid.uuid4()
        admin_user = User(
            id=admin_id,
            email="admin@smartcommerce.com",
            password_hash=get_password_hash("admin123"),
            full_name="System Admin",
            is_active=True
        )
        db.add(admin_user)
        
        # Create Customers
        customers = []
        for _ in range(50):
            cust = User(
                id=uuid.uuid4(),
                email=fake.unique.email(),
                password_hash=get_password_hash("password123"),
                full_name=fake.name(),
                is_active=True
            )
            customers.append(cust)
            db.add(cust)
            
        await db.flush()
        
        print("Creating Sellers...")
        sellers = []
        seller_users = []
        for _ in range(10):
            seller_user = User(
                id=uuid.uuid4(),
                email=f"seller_{fake.unique.word()}@smartcommerce.com",
                password_hash=get_password_hash("seller123"),
                full_name=fake.company(),
                is_active=True
            )
            seller_users.append(seller_user)
            db.add(seller_user)
            await db.flush()
            
            seller = Seller(
                id=uuid.uuid4(),
                user_id=seller_user.id,
                name=seller_user.full_name,
                description=fake.catch_phrase(),
                rating_avg=round(random.uniform(3.5, 5.0), 2)
            )
            sellers.append(seller)
            db.add(seller)
            
        await db.flush()

        print("Creating Warehouses...")
        warehouses = []
        for _ in range(5):
            wh = Warehouse(
                id=uuid.uuid4(),
                name=f"Warehouse {fake.city()}",
                location=fake.address()
            )
            warehouses.append(wh)
            db.add(wh)
        await db.flush()

        print("Creating Categories...")
        categories = []
        cat_names = ["Electronics", "Computers", "Smart Home", "Audio", "Wearables", "Gaming", "Cameras", "Accessories"]
        for name in cat_names:
            cat = Category(
                id=uuid.uuid4(),
                name=name,
                slug=name.lower().replace(" ", "-")
            )
            categories.append(cat)
            db.add(cat)
        await db.flush()
        
        print("Creating Brands...")
        brands = []
        for _ in range(20):
            brand_name = fake.company()
            brand = Brand(
                id=uuid.uuid4(),
                name=brand_name,
                slug=brand_name.lower().replace(" ", "-").replace(",", "")
            )
            brands.append(brand)
            db.add(brand)
        await db.flush()

        print("Generating 500 Products...")
        products = []
        mongo_metadata_list = []
        
        for i in range(500):
            if i % 100 == 0:
                print(f"Generated {i} products...")
                await db.flush()
                
            prod_id = uuid.uuid4()
            cat = random.choice(categories)
            brand = random.choice(brands)
            
            product_name = f"{brand.name} {fake.word().capitalize()} {fake.word().capitalize()}"
            base_price = round(random.uniform(10.0, 2000.0), 2)
            
            description = fake.paragraph(nb_sentences=5)
            
            # Compute embedding
            embedding_vector = None
            if embed_model is not None:
                text_to_embed = f"{product_name} {description} {cat.name} {brand.name}"
                embedding_vector = embed_model.encode(text_to_embed).tolist()

            product = Product(
                id=prod_id,
                sku=f"SKU-{fake.unique.random_number(digits=8)}",
                category_id=cat.id,
                brand_id=brand.id,
                title=product_name,
                slug=f"{product_name.lower().replace(' ', '-')}-{fake.unique.random_number(digits=4)}",
                base_price=base_price,
                rating_avg=round(random.uniform(3.0, 5.0), 2),
                review_count=random.randint(0, 500)
            )
            db.add(product)
            await db.flush()
            
            if embedding_vector:
                db.add(ProductEmbedding(product_id=prod_id, embedding=embedding_vector))

            # Create 1-3 Variants
            for v in range(random.randint(1, 3)):
                variant_id = uuid.uuid4()
                variant = ProductVariant(
                    id=variant_id,
                    product_id=prod_id,
                    sku=f"{product.sku}-V{v}",
                    title=f"{product.title} Variant {v+1}",
                    attributes={"color": fake.color_name(), "size": random.choice(["S", "M", "L", "XL"])},
                    price_override=round(base_price * random.uniform(0.9, 1.2), 2)
                )
                db.add(variant)
                await db.flush()
                
                # Add Inventory
                wh = random.choice(warehouses)
                seller = random.choice(sellers)
                
                inventory = Inventory(
                    id=uuid.uuid4(),
                    variant_id=variant_id,
                    warehouse_id=wh.id,
                    seller_id=seller.id,
                    on_hand=random.randint(10, 500),
                    reserved=0
                )
                db.add(inventory)

            # Assign product to 1-2 sellers
            for s in random.sample(sellers, k=random.randint(1, 2)):
                sp = SellerProduct(
                    id=uuid.uuid4(),
                    seller_id=s.id,
                    product_id=prod_id,
                    price=round(base_price * random.uniform(0.95, 1.05), 2)
                )
                db.add(sp)

            # Prepare Mongo Document
            mongo_metadata_list.append({
                "product_id": str(prod_id),
                "full_description": description,
                "specifications": {
                    "weight": f"{round(random.uniform(0.1, 5.0), 2)} kg",
                    "dimensions": f"{random.randint(5, 50)}x{random.randint(5, 50)}x{random.randint(5, 50)} cm",
                    "material": fake.word(),
                    "warranty": f"{random.randint(1, 3)} years"
                }
            })

        await db.commit()
        print(f"Inserted 500 products into PostgreSQL.")

    print("Connecting to MongoDB...")
    mongo_db = get_mongo_db() if callable(get_mongo_db) else get_mongo_db
    
    print("Clearing existing MongoDB metadata...")
    await mongo_db.product_metadata.delete_many({})
    
    print("Inserting enriched MongoDB metadata...")
    for i in range(0, len(mongo_metadata_list), 100):
        await mongo_db.product_metadata.insert_many(mongo_metadata_list[i:i+100])
        
    print(f"Inserted {len(mongo_metadata_list)} documents into MongoDB.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_db())
