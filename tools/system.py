import time
import logging
import subprocess
import psutil

logger = logging.getLogger("nina.tools.system")

from typing import Optional, Dict
async def get_temps() -> dict:
    temps: Dict[str, Optional[float]] = {"cpu": None, "gpu": None}
    try:
        st = psutil.sensors_temperatures()
        core = st.get("coretemp") or st.get("k10temp") or st.get("cpu_thermal") or []
        if core:
            temps["cpu"] = int(max(s.current for s in core))
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        temps["gpu"] = int(r.stdout.strip())
    except Exception:
        pass
    return temps

async def get_ram_used_gb() -> float:
    return psutil.virtual_memory().used / 1e9


async def get_vram_used_mb() -> int:
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        return int(r.stdout.strip())
    except Exception:
        return 0

async def get_disk_used_pct() -> float:
    return psutil.disk_usage("/").percent

async def get_status(config) -> str:
    vm   = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu  = psutil.cpu_percent(interval=1)

    up_secs = int(time.time() - psutil.boot_time())
    hrs     = up_secs // 3600
    mins    = (up_secs % 3600) // 60

    top5 = sorted(
        psutil.process_iter(["pid", "name", "memory_info"]),
        key=lambda p: p.info["memory_info"].rss if p.info["memory_info"] else 0,
        reverse=True
    )[:5]

    temps = await get_temps()
    ctemp = f"{temps['cpu']}°C" if temps["cpu"] else "N/A"
    gtemp = f"{temps['gpu']}°C" if temps["gpu"] else "N/A"

    lines = [
        f"RAM   {vm.used/1e9:.1f}/{vm.total/1e9:.0f}GB ({vm.percent:.0f}%)",
        f"Disk  {disk.used/1e9:.0f}/{disk.total/1e9:.0f}GB ({disk.percent:.0f}%)",
        f"CPU   {cpu:.0f}%  |  Thermal CPU:{ctemp} GPU:{gtemp}",
        f"Up    {hrs}h {mins}m",
        "Top processes:",
    ]

    for p in top5:
        try:
            mb = p.info["memory_info"].rss / 1e6 if p.info["memory_info"] else 0
            lines.append(f"  {p.info['pid']:>6}  {p.info['name']:<22} {mb:.0f}MB")
        except Exception:
            pass

    return "\n".join(lines)


# GPU tuning — merged from gputuner.py (COHERE-01)
import asyncio, json
from pathlib import Path

GPU_CONFIG = Path("data/gpuconfig.json")

async def tune() -> str:
    """Probe MX150 VRAM and determine stable layer counts for both models."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        free_mb = int(stdout.decode().strip())
    except (OSError, ValueError, asyncio.TimeoutError):
        # Fallback to mock metric when nvidia-smi is unavailable or fails
        free_mb = 0

    # qwen2.5:1.5b Q4_K_M ~1.0GB → fits fully (28 layers)
    # qwen2.5:7b   Q4_K_M ~4.3GB → partial offload based on free VRAM
    fast_layers  = 28
    heavy_layers = max(0, min(12, int((free_mb - 200) / 300)))  # conservative

    cfg = {"localfast_layers": fast_layers, "localheavy_layers": heavy_layers, "free_vram_mb": free_mb}
    GPU_CONFIG.write_text(json.dumps(cfg, indent=2))
    logger.info(f"gputuner fast={fast_layers} heavy={heavy_layers} free_vram={free_mb}MB",
                extra={"log":"tools.log", "tool_name": "system"})
    return f"GPU tuned — LOCALFAST: {fast_layers} layers, LOCALHEAVY: {heavy_layers} layers ({free_mb}MB free VRAM)"