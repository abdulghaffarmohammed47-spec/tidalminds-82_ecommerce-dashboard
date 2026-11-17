import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models.postgres.system import OutboxEvent
from app.workers.outbox_worker import process_next_event


@pytest.mark.asyncio
async def test_outbox_worker_processes_event(db_session):
    topic = f"TestEvent-{uuid.uuid4()}"
    event = OutboxEvent(
        topic=topic,
        payload={"event_id": str(uuid.uuid4())},
    )
    db_session.add(event)
    await db_session.commit()

    handled = []

    async def handler(received):
        handled.append(received.payload["event_id"])

    assert await process_next_event(db_session, {topic: handler}) == "PROCESSED"
    stored = await db_session.scalar(select(OutboxEvent).where(OutboxEvent.id == event.id))

    assert handled == [event.payload["event_id"]]
    assert stored.processed is True
    assert stored.status == "PROCESSED"
    assert stored.processed_at is not None


@pytest.mark.asyncio
async def test_outbox_worker_dead_letters_after_max_attempts(db_session):
    topic = f"AlwaysFails-{uuid.uuid4()}"
    event = OutboxEvent(
        topic=topic,
        payload={"reason": "test"},
        max_attempts=1,
        available_at=datetime.now(timezone.utc),
    )
    db_session.add(event)
    await db_session.commit()

    async def handler(_event):
        raise RuntimeError("downstream unavailable")

    assert await process_next_event(db_session, {topic: handler}) == "DEAD_LETTER"
    stored = await db_session.scalar(select(OutboxEvent).where(OutboxEvent.id == event.id))

    assert stored.processed is False
    assert stored.status == "DEAD_LETTER"
    assert stored.attempt_count == 1
    assert stored.last_error == "downstream unavailable"
