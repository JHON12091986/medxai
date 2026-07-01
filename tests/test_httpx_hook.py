import httpx
import asyncio

async def add_header(request):
    if request.url.port == 8765:
        request.headers["X-NINA-ROLE"] = "agent"

async def main():
    client = httpx.AsyncClient(event_hooks={"request": [add_header]})
    # Mocking request to see headers
    req = client.build_request("GET", "http://localhost:8765/test")
    await add_header(req) # Hooks are applied during send, but we can test logic
    print("Port 8765:", req.headers.get("X-NINA-ROLE"))

    req2 = client.build_request("GET", "http://localhost:8000/test")
    await add_header(req2)
    print("Port 8000:", req2.headers.get("X-NINA-ROLE"))

asyncio.run(main())
