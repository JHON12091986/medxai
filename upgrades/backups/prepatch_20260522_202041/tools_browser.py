import asyncio, logging
from playwright.async_api import async_playwright

logger = logging.getLogger("nina.tools.browser")
import ipaddress as _ipaddr
from urllib.parse import urlparse as _urlparse

def _is_internal(url: str) -> bool:
    try:
        host = _urlparse(url).hostname or ""
        addr = _ipaddr.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        return host.lower() in ("localhost",)


async def fetch(url: str) -> str:
    if any(b in url for b in BLOCKED):
        return "Blocked: internal network target."
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=["--disable-gpu","--no-sandbox","--disable-dev-shm-usage"])
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            text = await page.inner_text("body")
            await browser.close()
            out = text[:5000]
            logger.info(f"browser_fetch url={url!r} chars={len(out)}", extra={"log":"tools.log"})
            return out
    except Exception as e:
        logger.warning(f"browser_fetch_failed url={url!r} err={e}", extra={"log":"tools.log"})
        return f"Browser error: {e}"
