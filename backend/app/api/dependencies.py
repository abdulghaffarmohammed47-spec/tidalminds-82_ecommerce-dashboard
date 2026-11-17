from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple

from app.core.config import settings
from app.db.postgres import get_db
from app.repositories.user_repository import UserRepository
from app.models.postgres.auth import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    repo = UserRepository(session)
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        user_roles = [ur.role.name for ur in user.roles]
        for role in self.allowed_roles:
            if role in user_roles:
                return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )

async def get_optional_current_user(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)),
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    try:
        return await get_current_user(token, session)
    except HTTPException:
        return None

async def get_cart_id(
    user: Optional[User] = Depends(get_optional_current_user),
    x_session_id: Optional[str] = Header(None)
) -> Tuple[str, bool]:
    """
    Returns (cart_id, is_guest)
    """
    if user:
        return str(user.id), False
    if x_session_id:
        return x_session_id, True
    raise HTTPException(status_code=400, detail="Must provide authentication or X-Session-ID header")
