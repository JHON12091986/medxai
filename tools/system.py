import time
import logging
import subprocess
import psutil

logger = logging.getLogger("nina.tools.system")

from typing import Optional, Dict
async def get_temps() -> dict:
    temps: Dict[str, Optional[int]] = {"cpu": None, "gpu": None}
    try:
        st = psutil.sensors_temperatures()
        core = st.get("coretemp") or st.get("k10temp") or st.get("cpu_thermal") or []
        if core:
            temps["cpu"] = max(s.current for s in core)
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
