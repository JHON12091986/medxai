import asyncio, json, logging
from pathlib import Path

logger = logging.getLogger("nina.tools.gputuner")
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
                extra={"log":"tools.log", "tool_name": "gputuner"})
    return f"GPU tuned — LOCALFAST: {fast_layers} layers, LOCALHEAVY: {heavy_layers} layers ({free_mb}MB free VRAM)"
