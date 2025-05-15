import asyncio

from arpi import telegram


async def main() -> None:
    await telegram.initialize()


if __name__ == "__main__":
    asyncio.run(main())
