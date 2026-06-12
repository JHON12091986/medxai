"""
Legacy wrapper for the consolidated Jules engine.
Exposes run_orchestrator_cycle for crons/manager.py.
"""
import asyncio
import logging
from tools import jules

async def run_orchestrator_cycle(nina_os=None):
    """Triggers the unified orchestration loop."""
    await jules.orchestrate_cycle()

async def main():
    await run_orchestrator_cycle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
