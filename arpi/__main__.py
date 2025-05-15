import os
import asyncio

from arpi import telegram


async def a_main() -> None:
    if not os.path.exists("logs"):
        os.mkdir("logs")
    await telegram.initialize()


def main() -> None:
    asyncio.run(a_main())
