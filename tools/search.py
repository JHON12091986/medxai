"""NINA v12 — Search tool. Tavily → Serper → DuckDuckGo fallback chain."""
import logging, os, re, httpx
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("nina.tools.search")

TAVILY_KEY = os.getenv("TAVILY_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")


def _clean_query(query: str) -> str:
    """Strip LLM artifact junk that gets passed in as the query string."""
    # Remove anything after a newline (agent sometimes appends step markers)
    query = query.split("\n")[0].strip()
    # Remove leading/trailing quotes, brackets
    query = re.sub(r'^["\'\[\]]+|["\'\[\]]+$', "", query).strip()
    # Truncate to 300 chars max (Tavily/Serper limit)
    return query[:300]


async def search(query: str, max_results: int = 5) -> str:
    query = _clean_query(query)
    if not query:
        return "Search failed: empty query."

    if TAVILY_KEY:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post("https://api.tavily.com/search",
                    json={"api_key": TAVILY_KEY, "query": query, "max_results": max_results, "include_answer": True})
                r.raise_for_status()
                d = r.json()
                answer = d.get("answer", "")
                results = "\n".join(f"{x['title']}\n{x['url']}\n{x.get('content','')[:300]}" for x in d.get("results", []))
                out = f"Answer: {answer}\n\n{results}" if answer else results
                logger.info(f"tavily_search query={query!r} results={len(d.get('results',[]))}", extra={"log": "tools.log", "tool_name": "search"})
                return out
        except Exception as e:
            logger.warning(f"tavily_failed {e}")

    if SERPER_KEY:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post("https://google.serper.dev/search",
                    headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                    json={"q": query, "num": max_results})
                r.raise_for_status()
                d = r.json()
                items = d.get("organic", [])
                out = "\n".join(f"{x['title']}\n{x['link']}\n{x.get('snippet','')}" for x in items)
                logger.info(f"serper_search query={query!r} results={len(items)}", extra={"log": "tools.log", "tool_name": "search"})
                return out or "No results."
        except Exception as e:
            logger.warning(f"serper_failed {e}")

    try:
        from duckduckgo_search import DDGS
        import random
        ua = random.choice(["Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0", "Mozilla/5.0 (Windows NT 10.0) Firefox/125.0"])
        with DDGS(headers={"User-Agent": ua}, timeout=15) as ddgs:
            # v6+: keywords= is a required named argument
            ddg_results: list[dict[str, str]] = list(ddgs.text(keywords=query, max_results=max_results))
        out = "\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in ddg_results)
        logger.info(f"ddg_search query={query!r} results={len(ddg_results)}", extra={"log": "tools.log", "tool_name": "search"})
        return out or "No results."
    except Exception as e:
        logger.warning(f"ddg_failed {e}")
        return f"Search failed: {e}"


async def run(query: str) -> str:
    """Agent interface for search tool."""
    return await search(query)
