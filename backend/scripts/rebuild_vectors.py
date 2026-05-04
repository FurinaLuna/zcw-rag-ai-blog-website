import asyncio
import sys

sys.path.insert(0, ".")

from app.core.database import async_session_factory
from app.services.rag.sync import rebuild_all_vectors


async def main():
    async with async_session_factory() as db:
        result = await rebuild_all_vectors(db)
        print(f"Rebuild complete: {result}")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
