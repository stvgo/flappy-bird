import asyncio

from src.game import Game


async def main() -> None:
    await Game().run()


if __name__ == "__main__":
    asyncio.run(main())
