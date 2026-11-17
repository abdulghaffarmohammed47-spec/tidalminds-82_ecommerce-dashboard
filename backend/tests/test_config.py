import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    ("database_url", "expected_url"),
    [
        ("postgres://user:pass@db:5432/shop", "postgresql+asyncpg://user:pass@db:5432/shop"),
        ("postgresql://user:pass@db:5432/shop", "postgresql+asyncpg://user:pass@db:5432/shop"),
    ],
)
def test_postgres_urls_use_asyncpg(database_url: str, expected_url: str) -> None:
    assert Settings(DATABASE_URL=database_url).DATABASE_URL == expected_url
