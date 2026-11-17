from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import cast, Float, func
from app.models.postgres.catalog import Category, Brand, Product, ProductVariant, SellerOffer
from app.models.postgres.ai import Embedding
from app.schemas.catalog import CategoryCreate, BrandCreate, ProductCreate
import uuid

class CatalogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, category_in: CategoryCreate) -> Category:
        category = Category(**category_in.model_dump())
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def list_categories(self):
        result = await self.session.execute(select(Category))
        return result.scalars().all()

    async def create_brand(self, brand_in: BrandCreate) -> Brand:
        brand = Brand(**brand_in.model_dump())
        self.session.add(brand)
        await self.session.commit()
        await self.session.refresh(brand)
        return brand

    async def get_brand_by_name(self, name: str) -> Brand | None:
        result = await self.session.execute(select(Brand).where(Brand.name == name))
        return result.scalars().first()

    async def create_product_with_variants(self, product_in: ProductCreate) -> Product:
        product_data = product_in.model_dump(exclude={"variants"})
        product = Product(**product_data)
        
        variants = []
        for v_in in product_in.variants:
            v_data = v_in.model_dump()
            variant = ProductVariant(**v_data)
            variants.append(variant)
            
        product.variants = variants
        self.session.add(product)
        await self.session.commit()
        
        # Load relationships
        result = await self.session.execute(
            select(Product).options(selectinload(Product.variants)).where(Product.id == product.id)
        )
        return result.scalars().first()

    async def get_product(self, product_id: uuid.UUID) -> Product | None:
        result = await self.session.execute(
            select(Product).options(selectinload(Product.variants)).where(Product.id == product_id)
        )
        product = result.scalars().first()
        if product:
            price_result = await self.session.execute(
                select(func.min(SellerOffer.price)).where(
                    SellerOffer.variant_id.in_([variant.id for variant in product.variants]),
                    SellerOffer.is_active.is_(True),
                )
            )
            product.price = price_result.scalar_one_or_none()
        return product

    async def get_similar_products(self, product_id: uuid.UUID, limit: int = 4):
        product = await self.get_product(product_id)
        if not product:
            return []
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.variants))
            .where(
                Product.category_id == product.category_id,
                Product.id != product_id,
                Product.is_active.is_(True),
            )
            .limit(limit)
        )
        return result.scalars().all()

    async def list_products(self):
        result = await self.session.execute(
            select(Product).options(selectinload(Product.variants))
        )
        products = list(result.scalars().all())
        variant_ids = [variant.id for product in products for variant in product.variants]
        prices = {}
        if variant_ids:
            offer_result = await self.session.execute(
                select(SellerOffer.variant_id, func.min(SellerOffer.price))
                .where(SellerOffer.variant_id.in_(variant_ids), SellerOffer.is_active.is_(True))
                .group_by(SellerOffer.variant_id)
            )
            prices = dict(offer_result.all())
        for product in products:
            product.price = min(
                (prices[variant.id] for variant in product.variants if variant.id in prices),
                default=None,
            )
        return products

    async def search_products_by_vector(self, query_vector: list[float], limit: int = 5):
        # Join Product and Embedding to find nearest products based on cosine distance
        # We need to ensure we map back to the actual product owner of the embedding.
        stmt = (
            select(Product, Embedding.embedding.cosine_distance(query_vector).label("distance"))
            .join(Embedding, Product.id == Embedding.owner_id)
            .where(Embedding.owner_type == "product")
            .order_by("distance")
            .limit(limit)
            .options(selectinload(Product.variants))
        )
        result = await self.session.execute(stmt)
        # Returns a list of (Product, distance) tuples. We just want the products.
        products = []
        for row in result:
            products.append(row[0])
        return products
