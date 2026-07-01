"""core/mcp_client.py — Model Context Protocol (MCP) client for NINA vNext.

Provides a standardised MCP client that:
  - Connects to MCP servers via stdio (subprocess) or HTTP
  - Discovers and caches available tools from the server
  - Executes tool calls via JSON-RPC 2.0
  - Wraps existing NINA tools as MCP-compatible adapters
  - Provides a unified call() interface used by ReActEngine

Protocol: MCP 2024-11-05 (https://modelcontextprotocol.io/spec)

Transports:
  stdio  — launch MCP server as subprocess (local tools)
  http   — HTTP POST JSON-RPC to MCP server endpoint

Design rules:
  - All calls fail open: errors return MCPResult(success=False), never raise.
  - Tool registry cached at connect time, refreshed on demand.
  - Existing NINA tools registered as local adapters (no network).
  - call() accepts both MCP tool names and legacy NINA tool names.

Usage:
    from core.mcp_client import MCPClient
    client = MCPClient()
    client.register_local_tool("web_search", my_search_fn)
    result = await client.call("web_search", {"query": "NINA AI"})

    # Connect to external MCP server
    await client.connect_stdio(["npx", "-y", "@modelcontextprotocol/server-filesystem"])
    tools = await client.list_tools()
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

log = logging.getLogger("nina.mcp")

MCP_PROTOCOL_VERSION = "2024-11-05"
DEFAULT_TIMEOUT_S    = 30


@dataclass
class MCPTool:
    name:         str
    description:  str  = ""
    input_schema: dict = field(default_factory=dict)
    server:       str  = "local"

    def summary(self) -> str:
        return f"[{self.server}] {self.name}: {self.description[:80]}"


@dataclass
class MCPResult:
    success: bool
    content: Any  = None
    error:   str  = ""
    tool:    str  = ""
    server:  str  = ""

    def text(self) -> str:
        """Return content as plain text."""
        if not self.success:
            return f"[MCP Error] {self.error}"
        if isinstance(self.content, str):
            return self.content
        if isinstance(self.content, list):
            parts = []
            for item in self.content:
                if isinstance(item, dict):
                    parts.append(item.get("text") or json.dumps(item)[:200])
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return json.dumps(self.content, ensure_ascii=False)[:500]


class MCPError(Exception):
    pass


class MCPClient:
    """Unified MCP client + local tool adapter registry."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT_S):
        self.timeout = timeout
        self._local_tools:   dict[str, Callable[..., Awaitable[Any]]] = {}
        self._tool_registry: dict[str, MCPTool] = {}
        self._connections:   dict[str, Any] = {}

    # ── local tool registration ────────────────────────────────────────

    def register_local_tool(
        self,
        name: str,
        fn: Callable[..., Awaitable[Any]],
        description: str = "",
        input_schema: dict | None = None,
    ) -> None:
        """Register an existing async NINA tool as an MCP-compatible adapter."""
        self._local_tools[name] = fn
        self._tool_registry[name] = MCPTool(
            name=name,
            description=description or f"NINA local tool: {name}",
            input_schema=input_schema or {},
            server="local",
        )
        log.debug("mcp: registered local tool '%s'", name)

    def register_nina_tools(self, tools_module: Any) -> int:
        """Auto-register all public async callables from a NINA tools module.

        Returns number of tools registered.
        """
        count = 0
        for name in dir(tools_module):
            if name.startswith("_"):
                continue
            fn = getattr(tools_module, name)
            if callable(fn) and asyncio.iscoroutinefunction(fn):
                self.register_local_tool(name, fn)
                count += 1
        log.info("mcp: auto-registered %d NINA tools", count)
        return count

    # ── MCP server connections ─────────────────────────────────────────

    async def connect_stdio(
        self, cmd: list[str], server_name: str = ""
    ) -> list[MCPTool]:
        """Connect to an MCP server via stdio subprocess."""
        name = server_name or cmd[0].split("/")[-1]
        try:
            conn = _StdioConnection(cmd, name, self.timeout)
            await conn.start()
            tools = await conn.list_tools()
            self._connections[name] = conn
            for t in tools:
                self._tool_registry[t.name] = t
            log.info("mcp: connected stdio '%s' — %d tools", name, len(tools))
            return tools
        except Exception as exc:
            log.error("mcp: connect_stdio '%s' failed: %s", name, exc)
            return []

    async def connect_http(
        self, url: str, server_name: str = ""
    ) -> list[MCPTool]:
        """Connect to an MCP server via HTTP."""
        name = server_name or url.rstrip("/").split("/")[-1]
        try:
            conn = _HttpConnection(url, name, self.timeout)
            tools = await conn.list_tools()
            self._connections[name] = conn
            for t in tools:
                self._tool_registry[t.name] = t
            log.info("mcp: connected http '%s' — %d tools", name, len(tools))
            return tools
        except Exception as exc:
            log.error("mcp: connect_http '%s' failed: %s", name, exc)
            return []

    # ── unified call interface ─────────────────────────────────────────

    async def call(
        self,
        tool_name: str,
        arguments: dict | None = None,
        *,
        task: str = "",
    ) -> MCPResult:
        """Call a tool by name. Tries local first, then connected servers."""
        args = arguments or {}
        if tool_name in self._local_tools:
            return await self._call_local(tool_name, args, task)
        tool = self._tool_registry.get(tool_name)
        if tool and tool.server in self._connections:
            return await self._call_remote(tool_name, args, tool.server)
        for server_name, conn in self._connections.items():
            try:
                result = await conn.call_tool(tool_name, args)
                return MCPResult(success=True, content=result,
                                 tool=tool_name, server=server_name)
            except Exception:
                continue
        return MCPResult(
            success=False,
            error=f"Tool '{tool_name}' not found in local registry or any MCP server",
            tool=tool_name,
        )

    async def list_tools(self, server: str | None = None) -> list[MCPTool]:
        """List all available tools (local + connected servers)."""
        tools = list(self._tool_registry.values())
        return [t for t in tools if t.server == server] if server else tools

    async def disconnect_all(self) -> None:
        """Close all server connections."""
        for conn in self._connections.values():
            try:
                await conn.stop()
            except Exception:
                pass
        self._connections.clear()
        log.info("mcp: all connections closed")

    # ── internals ──────────────────────────────────────────────────────

    async def _call_local(
        self, name: str, args: dict, task: str
    ) -> MCPResult:
        fn = self._local_tools[name]
        try:
            if args:
                result = await asyncio.wait_for(fn(**args), timeout=self.timeout)
            else:
                result = await asyncio.wait_for(
                    fn(task) if task else fn(), timeout=self.timeout
                )
            return MCPResult(success=True, content=result, tool=name, server="local")
        except asyncio.TimeoutError:
            return MCPResult(success=False,
                             error=f"Timeout after {self.timeout}s", tool=name)
        except Exception as exc:
            log.warning("mcp: local tool '%s' error: %s", name, exc)
            return MCPResult(success=False, error=str(exc), tool=name)

    async def _call_remote(
        self, tool_name: str, args: dict, server_name: str
    ) -> MCPResult:
        conn = self._connections[server_name]
        try:
            result = await conn.call_tool(tool_name, args)
            return MCPResult(success=True, content=result,
                             tool=tool_name, server=server_name)
        except Exception as exc:
            log.warning("mcp: remote '%s' on '%s' error: %s",
                        tool_name, server_name, exc)
            return MCPResult(success=False, error=str(exc),
                             tool=tool_name, server=server_name)


# ── transport implementations ──────────────────────────────────────────

class _StdioConnection:
    """MCP server connected via stdio subprocess."""

    def __init__(self, cmd: list[str], name: str, timeout: int):
        self.cmd = cmd; self.name = name; self.timeout = timeout
        self._proc = None; self._req_id = 0

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await self._rpc("initialize", {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "clientInfo": {"name": "nina", "version": "vnext"},
            "capabilities": {},
        })
        await self._rpc("notifications/initialized", {}, notify=True)

    async def list_tools(self) -> list[MCPTool]:
        result = await self._rpc("tools/list", {})
        return [
            MCPTool(
                name=t.get("name", ""),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema") or {},
                server=self.name,
            )
            for t in (result.get("tools") or [])
        ]

    async def call_tool(self, name: str, arguments: dict) -> Any:
        result = await self._rpc("tools/call", {"name": name, "arguments": arguments})
        return result.get("content") or result

    async def stop(self) -> None:
        if self._proc:
            self._proc.terminate()
            await self._proc.wait()

    async def _rpc(
        self, method: str, params: dict, notify: bool = False
    ) -> dict:
        self._req_id += 1
        payload: dict = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            payload["id"] = self._req_id
        line = json.dumps(payload) + "\n"
        self._proc.stdin.write(line.encode())
        await self._proc.stdin.drain()
        if notify:
            return {}
        raw = await asyncio.wait_for(
            self._proc.stdout.readline(), timeout=self.timeout
        )
        resp = json.loads(raw.decode().strip())
        if "error" in resp:
            raise MCPError(f"MCP RPC error: {resp['error']}")
        return resp.get("result") or {}


class _HttpConnection:
    """MCP server connected via HTTP POST JSON-RPC."""

    def __init__(self, url: str, name: str, timeout: int):
        self.url = url.rstrip("/"); self.name = name; self.timeout = timeout
        self._req_id = 0

    async def list_tools(self) -> list[MCPTool]:
        result = await self._rpc("tools/list", {})
        return [
            MCPTool(
                name=t.get("name", ""),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema") or {},
                server=self.name,
            )
            for t in (result.get("tools") or [])
        ]

    async def call_tool(self, name: str, arguments: dict) -> Any:
        result = await self._rpc("tools/call", {"name": name, "arguments": arguments})
        return result.get("content") or result

    async def stop(self) -> None:
        pass

    async def _rpc(self, method: str, params: dict) -> dict:
        import aiohttp
        self._req_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id":      self._req_id,
            "method":  method,
            "params":  params,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                data = await resp.json()
                if "error" in data:
                    raise MCPError(f"MCP HTTP error: {data['error']}")
                return data.get("result") or {}
