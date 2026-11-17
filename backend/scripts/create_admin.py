import asyncio
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        stmt = select(User).where(User.email == "admin@smartcommerce.com")
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            print("Admin user already exists.")
            return
        
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@smartcommerce.com",
            full_name="System Administrator",
            password_hash=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        print("Created admin user: admin@smartcommerce.com / Admin@123")

if __name__ == "__main__":
    asyncio.run(main())
