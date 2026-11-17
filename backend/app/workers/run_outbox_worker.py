import asyncio
import json
import logging

from app.db.postgres import async_session_maker
from app.db.redis import cache, close_redis_connection, connect_to_redis
from app.workers.outbox_worker import process_next_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def publish_order_created(event):
    if cache.client is None:
        raise RuntimeError("Redis event stream is unavailable")
    await cache.client.xadd(
        "smartcommerce:events",
        {
            "topic": event.topic,
            "payload": json.dumps(event.payload),
            "event_id": str(event.id),
        },
    )


async def run() -> None:
    await connect_to_redis()
    try:
        handlers = {"OrderCreated": publish_order_created}
        while True:
            async with async_session_maker() as session:
                status = await process_next_event(session, handlers)
                if status:
                    logger.info("Outbox event finished with status=%s", status)
            await asyncio.sleep(1 if status is None else 0)
    finally:
        await close_redis_connection()


if __name__ == "__main__":
    asyncio.run(run())
