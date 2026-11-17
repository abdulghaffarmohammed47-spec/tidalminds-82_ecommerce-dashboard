from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Initialize model at module level so it's loaded once during startup
MODEL_NAME = 'all-MiniLM-L6-v2'
logger.info(f"Loading embedding model {MODEL_NAME}...")
try:
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Embedding model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    model = None

def get_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding for the given text.
    """
    if not model:
        raise RuntimeError("Embedding model is not loaded.")
    # The model returns a numpy array, convert to list of floats for pgvector
    embedding = model.encode(text)
    return embedding.tolist()
