from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
from sqlalchemy import text

from contextlib import asynccontextmanager
from app.api import products, categories, auth, sellers, cart, orders, payments, inventory, bot, analytics, wishlist, coupons, shipping, returns
from app.core.metrics import metrics
from app.db.mongodb import connect_to_mongo, close_mongo_connection, db as mongodb_db
from app.db.redis import connect_to_redis, close_redis_connection, cache as redis_cache
from app.db.postgres import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    await connect_to_mongo()
    # Connect to Redis
    await connect_to_redis()
    
    yield
    
    # Close connections on shutdown
    await close_mongo_connection()
    await close_redis_connection()

app = FastAPI(
    title="SmartCommerce X API",
    description="Intelligent Database-centric E-Commerce Platform",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    metrics.record_request(request.method, request.url.path, response.status_code, duration)
    return response

@app.get("/metrics", tags=["Observability"])
async def get_prometheus_metrics():
    return Response(content=metrics.generate_prometheus_text(), media_type="text/plain; version=0.0.4; charset=utf-8")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(sellers.router, prefix="/api/sellers", tags=["Sellers"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(bot.router, prefix="/api", tags=["RAG Assistant"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["Wishlist"])
app.include_router(coupons.router, prefix="/api/coupons", tags=["Coupons"])
app.include_router(shipping.router, prefix="/api/shipping", tags=["Shipping"])
app.include_router(returns.router, prefix="/api/returns", tags=["Returns"])

# Keep the existing development routes stable while exposing the versioned
# contract for new clients and future breaking changes.
versioned_routers = (
    (products.router, "/products"),
    (categories.router, "/categories"),
    (auth.router, "/auth"),
    (sellers.router, "/sellers"),
    (cart.router, "/cart"),
    (orders.router, "/orders"),
    (payments.router, "/payments"),
    (inventory.router, "/inventory"),
    (bot.router, ""),
    (analytics.router, ""),
    (wishlist.router, "/wishlist"),
    (coupons.router, "/coupons"),
    (shipping.router, "/shipping"),
    (returns.router, "/returns"),
)
for router, route_prefix in versioned_routers:
    app.include_router(router, prefix=f"/api/v1{route_prefix}")

@app.get("/health")
async def health_check():
    health_status = {
        "status": "ok",
        "api": "healthy",
        "postgres": "unknown",
        "mongodb": "unknown",
        "redis": "unknown"
    }
    
    # Check Postgres
    try:
        async with engine.connect() as conn:
            health_status["postgres"] = "healthy"
    except Exception as e:
        health_status["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "error"
        
    # Check MongoDB
    try:
        if mongodb_db.client is not None:
            await mongodb_db.client.admin.command('ping')
            health_status["mongodb"] = "healthy"
        else:
            health_status["mongodb"] = "degraded: unavailable"
    except Exception as e:
        health_status["mongodb"] = f"unhealthy: {str(e)}"
        health_status["mongodb"] = "degraded: unavailable"
        
    # Check Redis
    try:
        if redis_cache.client is not None:
            await redis_cache.client.ping()
            health_status["redis"] = "healthy"
        else:
            health_status["redis"] = "degraded: unavailable"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["redis"] = "degraded: unavailable"
        
    return health_status


async def _component_health(component: str):
    started = time.perf_counter()
    try:
        if component == "db":
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        elif component == "mongodb":
            if mongodb_db.client is None:
                raise RuntimeError("MongoDB client is unavailable")
            await mongodb_db.client.admin.command("ping")
        elif component in {"redis", "events"}:
            if redis_cache.client is None:
                raise RuntimeError("Redis client is unavailable")
            await redis_cache.client.ping()
        elif component == "vector":
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        elif component == "ai":
            return {
                "component": component,
                "status": "DEGRADED",
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "detail": "No external AI provider is configured",
            }
        return {
            "component": component,
            "status": "HEALTHY",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:
        return {
            "component": component,
            "status": "DEGRADED",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "detail": str(exc),
        }


@app.get("/health/db")
async def database_health():
    return await _component_health("db")


@app.get("/health/mongodb")
async def mongodb_health():
    return await _component_health("mongodb")


@app.get("/health/redis")
async def redis_health():
    return await _component_health("redis")


@app.get("/health/vector")
async def vector_health():
    return await _component_health("vector")


@app.get("/health/ai")
async def ai_health():
    return await _component_health("ai")


@app.get("/health/events")
async def events_health():
    return await _component_health("events")
