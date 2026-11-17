import asyncio
# pyrefly: ignore [missing-import]
import asyncpg

async def run():
    conn = await asyncpg.connect("postgresql://admin:admin123@postgres:5432/ecommerce_db")
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    await conn.close()
    print("DONE")

asyncio.run(run())
