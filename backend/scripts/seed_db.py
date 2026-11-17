import asyncio
import sys
import os

# Add the backend directory to the sys path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.mongo import db as mongo_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.product import Category, Product, ProductEmbedding, Inventory
from app.core.embeddings import get_embedding

async def seed():
    print("Starting database seeding...")
    db = SessionLocal()
    
    try:
        # 1. Create Users
        admin_user = db.query(User).filter(User.email == "admin@smartcommerce.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@smartcommerce.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Admin",
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Created admin user.")

        seller_user = db.query(User).filter(User.email == "seller@smartcommerce.com").first()
        if not seller_user:
            seller_user = User(
                email="seller@smartcommerce.com",
                hashed_password=get_password_hash("seller123"),
                full_name="Tech Seller",
                role=UserRole.SELLER
            )
            db.add(seller_user)
            db.commit()
            db.refresh(seller_user)
            print("Created seller user.")

        # 2. Create Categories
        categories = ["Laptops", "Smartphones", "Audio"]
        category_objects = {}
        for cat_name in categories:
            cat = db.query(Category).filter(Category.name == cat_name).first()
            if not cat:
                cat = Category(name=cat_name, description=f"High quality {cat_name}")
                db.add(cat)
                db.commit()
                db.refresh(cat)
            category_objects[cat_name] = cat
        print("Created categories.")

        # 3. Create Products, Inventory, Embeddings, and Mongo metadata
        products_data = [
            {
                "name": "Titanium Pro Book 16",
                "description": "A high-performance laptop for gaming and programming. Features an incredible display and blazing fast processor.",
                "price": 2499.99,
                "category": "Laptops",
                "stock": 50,
                "specs": {"cpu": "Intel Core i9", "ram": "32GB", "gpu": "RTX 4080", "battery_life": "10 hours"},
                "tags": ["gaming", "programming", "high-performance", "laptop"]
            },
            {
                "name": "UltraSlim Air 13",
                "description": "Lightweight and portable laptop perfect for students and professionals on the go. Great battery life.",
                "price": 1099.99,
                "category": "Laptops",
                "stock": 100,
                "specs": {"cpu": "M-Series", "ram": "16GB", "gpu": "Integrated", "battery_life": "18 hours"},
                "tags": ["portable", "student", "business", "laptop"]
            },
            {
                "name": "Quantum Phone 15 Pro",
                "description": "The latest flagship smartphone with an advanced camera system and titanium body. Great for photography.",
                "price": 999.99,
                "category": "Smartphones",
                "stock": 200,
                "specs": {"screen": "6.7 inch OLED", "camera": "48MP Triple", "storage": "256GB"},
                "tags": ["smartphone", "photography", "flagship", "mobile"]
            },
            {
                "name": "SonicBuds Pro",
                "description": "Active noise cancelling wireless earbuds with spatial audio. Perfect for commuting and gym.",
                "price": 249.99,
                "category": "Audio",
                "stock": 150,
                "specs": {"type": "In-ear", "battery": "6 hours (24 with case)", "anc": "Yes"},
                "tags": ["earbuds", "wireless", "audio", "gym", "music"]
            },
            {
                "name": "Studio Over-Ear Headphones",
                "description": "Professional grade over-ear headphones with lossless audio support. Perfect for audiophiles and mixing.",
                "price": 349.99,
                "category": "Audio",
                "stock": 40,
                "specs": {"type": "Over-ear", "battery": "30 hours", "impedance": "32 Ohm"},
                "tags": ["headphones", "audiophile", "music", "studio"]
            }
        ]

        for p_data in products_data:
            existing_product = db.query(Product).filter(Product.name == p_data["name"]).first()
            if not existing_product:
                # Insert Postgres Product
                prod = Product(
                    name=p_data["name"],
                    description=p_data["description"],
                    price=p_data["price"],
                    category_id=category_objects[p_data["category"]].id,
                    seller_id=seller_user.id
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)

                # Insert Inventory
                inv = Inventory(
                    product_id=prod.id,
                    current_stock=p_data["stock"],
                    reorder_threshold=10
                )
                db.add(inv)

                # Insert Embedding
                combined_text = f"{prod.name}. {prod.description}. Category: {p_data['category']}."
                embedding_vector = get_embedding(combined_text)
                
                prod_emb = ProductEmbedding(
                    product_id=prod.id,
                    embedding=embedding_vector
                )
                db.add(prod_emb)
                db.commit()

                # Insert Mongo Metadata
                await mongo_db.product_metadata.update_one(
                    {"_id": str(prod.id)},
                    {"$set": {
                        "brand": "SmartBrand",
                        "specifications": p_data["specs"],
                        "tags": p_data["tags"]
                    }},
                    upsert=True
                )
                print(f"Created product: {p_data['name']}")

        print("Seeding completed successfully!")
    
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed())
