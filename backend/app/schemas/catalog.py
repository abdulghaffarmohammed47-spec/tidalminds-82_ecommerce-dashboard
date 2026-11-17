from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Any, Dict
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    parent_id: Optional[UUID4] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: UUID4
    
    class Config:
        from_attributes = True

class BrandBase(BaseModel):
    name: str = Field(..., max_length=255)

class BrandCreate(BrandBase):
    pass

class BrandResponse(BrandBase):
    id: UUID4
    
    class Config:
        from_attributes = True

class ProductVariantBase(BaseModel):
    sku: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: UUID4
    product_id: UUID4
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_id: UUID4
    brand_id: UUID4
    is_active: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = Field(default_factory=list)

class ProductResponse(ProductBase):
    id: UUID4
    price: Optional[int] = None
    variants: List[ProductVariantResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
