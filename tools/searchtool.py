"""Wraps search.py as a .run()-able tool for the agent loop."""
from tools.search import search

async def run(query: str) -> str:
    return await search(query)
