from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class RoleRead(BaseModel):
    name: str
    
    class Config:
        from_attributes = True

class UserRead(UserBase):
    id: UUID
    roles: List[str] = []

    @field_validator('roles', mode='before')
    @classmethod
    def extract_role_names(cls, v):
        if not v:
            return []
        # If it's already a list of strings, just return it
        if all(isinstance(r, str) for r in v):
            return v
        # Otherwise, assume it's a list of UserRole ORM objects
        return [ur.role.name for ur in v if hasattr(ur, 'role') and ur.role]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
