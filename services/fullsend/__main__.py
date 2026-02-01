"""Entry point for running FULLSEND listener as a module."""

from .listener import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
