from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.postgres.auth import User, Role, UserRole
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: UUID | str) -> User | None:
        stmt = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user_create: UserCreate) -> User:
        hashed_password = get_password_hash(user_create.password)
        db_user = User(email=user_create.email, hashed_password=hashed_password)
        self.session.add(db_user)
        await self.session.flush()

        # Assign default 'customer' role
        role = await self.get_or_create_role("customer")
        user_role = UserRole(user_id=db_user.id, role_id=role.id)
        self.session.add(user_role)
        
        await self.session.commit()
        await self.session.refresh(db_user)
        return await self.get_user_by_id(db_user.id)

    async def get_or_create_role(self, role_name: str) -> Role:
        stmt = select(Role).where(Role.name == role_name)
        result = await self.session.execute(stmt)
        role = result.scalars().first()
        if not role:
            role = Role(name=role_name)
            self.session.add(role)
            await self.session.flush()
        return role

    async def assign_role(self, user_id: UUID | str, role_name: str) -> None:
        role = await self.get_or_create_role(role_name)
        
        # Check if already assigned
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            return
            
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.session.add(user_role)
        await self.session.commit()
