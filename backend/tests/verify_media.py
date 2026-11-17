import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.models.user import User, UserRole
from app.core.mongo import get_mongo_db

async def verify_100_percent_media():
    async with AsyncSessionLocal() as session:
        # 1. Check users
        users = (await session.execute(select(User))).scalars().all()
        user_roles = {u.email: u.role for u in users}
        print(f"Total Users: {len(users)}")
        assert "customer@smartcommerce.dev" in user_roles, "Customer missing"
        assert "seller@smartcommerce.dev" in user_roles, "Seller missing"
        assert "admin@smartcommerce.dev" in user_roles, "Admin missing"
        print("Customer, Seller, and Admin accounts verified.")

        # 2. Check products
        products = (await session.execute(select(Product))).scalars().all()
        print(f"Total Products in PostgreSQL: {len(products)}")
        assert len(products) >= 150, f"Expected >= 150 products, got {len(products)}"
        
        all_360 = all(p.has_360_view for p in products)
        all_vid = all(p.has_video for p in products)
        print(f"PostgreSQL has_360_view=True for 100% products: {all_360}")
        print(f"PostgreSQL has_video=True for 100% products: {all_vid}")
        assert all_360 and all_vid, "Missing media flags in PostgreSQL"

        # 3. Check MongoDB product_multimedia
        mongo_db = get_mongo_db() if callable(get_mongo_db) else get_mongo_db
        count = await mongo_db.product_multimedia.count_documents({})
        print(f"Total MongoDB product_multimedia records: {count}")
        assert count == len(products), f"MongoDB count {count} != Postgres count {len(products)}"

        # 4. Validate 100% compliance across all documents
        cursor = mongo_db.product_multimedia.find({})
        checked = 0
        async for doc in cursor:
            sku = doc.get("sku", "UNKNOWN")

            # Gallery: >= 4 images, with primary image
            gallery = doc.get("gallery", [])
            assert len(gallery) >= 4, f"Product {sku} gallery has < 4 items (got {len(gallery)})"
            assert any(g.get("is_primary") for g in gallery), f"Product {sku} missing primary gallery image"

            # 360 View: enabled, exactly 24 frames, hotspots present
            view_360 = doc.get("view_360", {})
            assert view_360.get("enabled") is True, f"Product {sku} 360 view not enabled"
            frames = view_360.get("frames", [])
            assert len(frames) == 24, f"Product {sku} 360 view frames count is {len(frames)}, expected 24"
            assert len(view_360.get("hotspots", [])) > 0, f"Product {sku} missing hotspots"

            # Video Showcase: enabled, video_url, >= 3 chapters with timestamp_sec
            video = doc.get("video_showcase", {})
            assert video.get("enabled") is True, f"Product {sku} video not enabled"
            assert bool(video.get("video_url")), f"Product {sku} missing video_url"
            chapters = video.get("chapters", [])
            assert len(chapters) >= 3, f"Product {sku} has < 3 chapters"
            assert "timestamp_sec" in chapters[0], f"Product {sku} chapter missing timestamp_sec"

            checked += 1

        print(f"ALL {checked} PRODUCTS (100%) FULLY COMPLY WITH MANDATORY MULTIMEDIA GUARANTEE!")

if __name__ == "__main__":
    asyncio.run(verify_100_percent_media())
