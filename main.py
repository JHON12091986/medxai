import asyncio
from core.nina import NinaOS

async def main():
    nina = NinaOS()
    await nina.start()
    await asyncio.Event().wait()   # keep alive forever

if __name__ == "__main__":
    asyncio.run(main())
