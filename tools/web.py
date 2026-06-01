import asyncio, logging, random
from duckduckgo_search import DDGS

logger = logging.getLogger("nina.tools.web")
UA_POOL = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14) Safari/605.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0) Chrome/123.0 Safari/537.36",
]

async def search(query: str, max_results: int = 5) -> str:
    for attempt in range(3):
        try:
            ua = random.choice(UA_POOL)
            # Run sync DDGS in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: list(DDGS(headers={"User-Agent": ua}, timeout=15)
                                 .text(query, max_results=max_results))
                ),
                timeout=20.0
            )
            # Validate each result has required fields
            valid = [r for r in results if r.get("title") and r.get("href") and r.get("body")]
            if not valid:
                logger.warning(f"web_search_empty query={query!r}", extra={"log":"tools.log"})
                return "No results found."
            out = "\n\n".join(
                f"**{r['title']}**\n{r['href']}\n{r['body']}" for r in valid
            )
            logger.info(f"web_search query={query!r} results={len(valid)}", extra={"log":"tools.log"})
            return out
        except asyncio.TimeoutError:
            logger.warning(f"web_search_timeout attempt={attempt+1} query={query!r}", extra={"log":"tools.log"})
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                return "Search timed out after 3 attempts."
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.warning(f"web_search_failed query={query!r} err={e}", extra={"log":"tools.log"})
                return f"Search failed: {e}"
