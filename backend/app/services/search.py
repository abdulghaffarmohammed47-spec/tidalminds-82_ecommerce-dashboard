import uuid
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres.ai import Embedding

class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_dummy_embedding_for_product(self, product_id: uuid.UUID):
        """
        Generates a random 1536-dimensional vector for a product to simulate an embedding.
        Used for S1 verification of pgvector integration.
        """
        # Generate a random 1536-d vector.
        dummy_vector = [random.uniform(-1, 1) for _ in range(1536)]
        
        # Normalize the vector (optional but good practice for cosine similarity)
        magnitude = sum(x**2 for x in dummy_vector) ** 0.5
        normalized_vector = [x / magnitude for x in dummy_vector]

        embedding = Embedding(
            owner_type="product",
            owner_id=product_id,
            chunk_index=0,
            content="Dummy product description for semantic search testing.",
            embedding=normalized_vector,
            visibility="public",
            version=1
        )
        self.session.add(embedding)
        await self.session.commit()
        return normalized_vector

    def get_dummy_query_vector(self) -> list[float]:
        # Generate a random 1536-d vector to act as our "text query" embedding.
        dummy_vector = [random.uniform(-1, 1) for _ in range(1536)]
        magnitude = sum(x**2 for x in dummy_vector) ** 0.5
        normalized_vector = [x / magnitude for x in dummy_vector]
        return normalized_vector

    async def vector_search_products(self, query_vector: list[float], limit: int = 5):
        from sqlalchemy import select
        from app.models.postgres.catalog import Product

        # Search for closest embeddings where owner_type is product.
        # `<=>` is cosine distance in pgvector
        stmt = (
            select(Product, Embedding.embedding.cosine_distance(query_vector).label("distance"))
            .join(Embedding, Embedding.owner_id == Product.id)
            .where(Embedding.owner_type == "product")
            .where(Product.is_active == True)
            .order_by("distance")
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        # return list of tuples (Product, distance)
        return result.all()
