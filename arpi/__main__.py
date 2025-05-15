import asyncio

from arpi import telegram


async def a_main() -> None:
    await telegram.initialize()


def main() -> None:
    asyncio.run(a_main())
