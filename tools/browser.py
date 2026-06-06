import logging, socket
from playwright.async_api import async_playwright
import ipaddress as ipaddr
from urllib.parse import urlparse as urlparse

logger = logging.getLogger("nina.tools.browser")


def _is_internal(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        addr = ipaddr.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        try:
            resolved = socket.gethostbyname(host)
            addr = ipaddr.ip_address(resolved)
            return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
        except socket.gaierror:
            return True
# SSRF guard uses ipaddress module — R-64 verified, O-03 closed.


async def fetch(url: str) -> str:
    if _is_internal(url):                # FIX: was is_internal (missing underscore)
        return "Blocked: internal network target."
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(executable_path="/usr/bin/chromium-browser",
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"])
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            text = await page.inner_text("body")
            await browser.close()
            out = text[:5000]
            logger.info(f"browser_fetch url={url!r} chars={len(out)}", extra={"log": "tools.log"})
            return out
    except Exception as e:
        logger.warning(f"browser_fetch_failed url={url!r} err={e}", extra={"log": "tools.log"})
        return f"Browser error: {e}"
