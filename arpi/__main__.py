import asyncio

from arpi import flash, telegram


async def a_main() -> None:
    flash.copy("/Users/pavelmilosh/Downloads/Windows_11", "/Users/pavelmilosh/Downloads/KEK")
    flash.hash("/Users/pavelmilosh/Downloads/KEK")

    #await telegram.initialize()


def main() -> None:
    asyncio.run(a_main())

if __name__ == "__main__":
    main()