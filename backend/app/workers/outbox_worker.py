from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, Mapping, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres.system import OutboxEvent

EventHandler = Callable[[OutboxEvent], Awaitable[None]]


async def claim_next_event(
    session: AsyncSession,
    topics: tuple[str, ...] | None = None,
) -> Optional[OutboxEvent]:
    """Atomically claim one due event so multiple workers do not process it twice."""
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(OutboxEvent)
        .where(
            OutboxEvent.processed.is_(False),
            OutboxEvent.topic.in_(topics) if topics else True,
            or_(OutboxEvent.status.is_(None), OutboxEvent.status == "PENDING"),
            or_(OutboxEvent.available_at.is_(None), OutboxEvent.available_at <= now),
        )
        .order_by(OutboxEvent.id)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    event = result.scalar_one_or_none()
    if event is None:
        return None

    event.status = "PROCESSING"
    event.attempt_count = (event.attempt_count or 0) + 1
    await session.commit()
    return event


async def process_next_event(
    session: AsyncSession,
    handlers: Mapping[str, EventHandler],
) -> Optional[str]:
    """Process one event and return its final status, if an event was available."""
    if not handlers:
        return None

    event = await claim_next_event(session, tuple(handlers))
    if event is None:
        return None

    try:
        handler = handlers.get(event.topic)
        if handler is None:
            raise ValueError(f"No handler registered for outbox topic: {event.topic}")
        await handler(event)
    except Exception as exc:
        result = await session.execute(select(OutboxEvent).where(OutboxEvent.id == event.id))
        current = result.scalar_one()
        current.last_error = str(exc)[:2000]
        if current.attempt_count >= current.max_attempts:
            current.status = "DEAD_LETTER"
        else:
            current.status = "PENDING"
            delay = min(2 ** max(current.attempt_count - 1, 0), 300)
            current.available_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        await session.commit()
        return current.status

    result = await session.execute(select(OutboxEvent).where(OutboxEvent.id == event.id))
    current = result.scalar_one()
    current.status = "PROCESSED"
    current.processed = True
    current.processed_at = datetime.now(timezone.utc)
    current.last_error = None
    await session.commit()
    return current.status
