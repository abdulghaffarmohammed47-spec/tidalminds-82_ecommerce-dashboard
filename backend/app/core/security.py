import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from app.core.redis import redis_client

# Argon2id with bcrypt fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str, jti: Optional[str] = None) -> Tuple[str, str]:
    """
    Creates a sliding refresh token with unique JTI.
    Returns (encoded_jwt, jti).
    """
    token_jti = jti or str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "jti": token_jti,
        "exp": expire,
        "type": "refresh"
    }
    encoded = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded, token_jti

async def store_refresh_token(user_id: str, jti: str):
    """Register active refresh token JTI in Redis with 7-day TTL"""
    key = f"refresh_token:{user_id}:{jti}"
    ttl_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.set(key, "active", ex=ttl_seconds)

async def is_refresh_token_valid(user_id: str, jti: str) -> bool:
    """Validate that refresh token JTI exists in Redis and is not revoked"""
    key = f"refresh_token:{user_id}:{jti}"
    val = await redis_client.get(key)
    if val != "active":
        return False
    # Check blacklist
    revoked = await redis_client.get(f"revoked_token:{jti}")
    return revoked is None

async def revoke_refresh_token(user_id: str, jti: str):
    """Revoke refresh token and add to revocation blacklist"""
    await redis_client.delete(f"refresh_token:{user_id}:{jti}")
    # Blacklist for 7 days
    ttl_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.set(f"revoked_token:{jti}", "revoked", ex=ttl_seconds)
