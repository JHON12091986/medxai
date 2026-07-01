# HARDWARE_FIRST — Nina Model Selection Protocol

> **Mandatory reading for all AI agents, Jules, Gemini, and Perplexity Overwatch
> before suggesting ANY model, library, or resource-intensive component.**

---

## The Hardware Constraint (Non-Negotiable)

```
Machine:  ASUS VivoBook X530FN
CPU:      Intel i5-8265U (4c/8t, ~1.6GHz base)
GPU:      NVIDIA MX150 — 2GB GDDR5 VRAM (hard ceiling)
RAM:      16GB DDR4
Storage:  SSD (~200GB free)
OS:       Ubuntu 26.04
```

**The MX150 2GB VRAM is the single most important constraint in Nina.**
Everything else is secondary.

---

## The Rule: Hardware-First Checklist

Before suggesting, implementing, or fine-tuning ANY model, an agent MUST answer
these questions IN ORDER:

```
1. Does it fit in 2GB VRAM at Q4_K_M quantization?
   YES → proceed
   NO  → suggest a smaller model or quantization, never proceed blindly

2. Has it been benchmarked on Nina's actual use cases?
   YES → proceed with data
   NO  → run dulal_model_bench.sh first, then decide

3. Is there a newer/smarter model at the same or smaller size?
   Check ollama.com/search before defaulting to the obvious choice.

4. Is fine-tuning actually necessary?
   Can the base model do the job with a good system prompt?
   Fine-tune ONLY the benchmark winner, never a guess.
```

---

## The 3-Tier Local Model Architecture

```
┌─────────────────────────────────────────────────────┐
│  TIER 1 — LOCAL FAST                                │
│  Model:   qwen3:1.7b (or benchmark winner)          │
│  VRAM:    ~1.1GB                                    │
│  Speed:   ~25 tok/s                                 │
│  Tasks:   bash one-liners, git, simple edits        │
├─────────────────────────────────────────────────────┤
│  TIER 2 — LOCAL HEAVY (DULAL)                       │
│  Model:   benchmark winner, fine-tuned              │
│  VRAM:    ~1.9GB                                    │
│  Speed:   ~15 tok/s                                 │
│  Tasks:   FastAPI, classes, debug, dataclasses      │
├─────────────────────────────────────────────────────┤
│  TIER 3 — CLOUD                                     │
│  Model:   Gemini Flash / Claude Sonnet              │
│  VRAM:    0 (remote)                                │
│  Tasks:   architecture, long context, reasoning     │
└─────────────────────────────────────────────────────┘
```

**Ollama auto-swaps Tier 1 and Tier 2 on demand — no manual switching needed.**
Only one model is loaded in VRAM at a time.

---

## Approved Models (Fit in MX150 2GB)

| Model | VRAM | Tier | Ollama cmd |
|---|---|---|---|
| qwen3:1.7b | ~1.1GB | FAST | `ollama pull qwen3:1.7b` |
| smollm3:3b | ~1.9GB | HEAVY | `ollama pull smollm3` |
| phi4-mini | ~1.6GB | HEAVY | `ollama pull phi4-mini` |
| qwen2.5-coder:3b | ~1.9GB | HEAVY | `ollama pull qwen2.5-coder:3b` |
| qwen3.5:2b | ~1.8GB | HEAVY | `ollama pull qwen3.5:2b` |

---

## Rejected Models (Do NOT Suggest These)

| Model | Why Rejected |
|---|---|
| qwen2.5-coder:7b | 4.7GB — proven OOM on MX150 |
| llama3.1:8b | 5.0GB — too large |
| deepseek-coder:6.7b | 4.3GB — too large |
| Any IQ1/IQ2 quantized 7B | Quality collapses below 3B Q4 level |
| Any model > 2.3GB VRAM | Will not fully offload to MX150 |

---

## The DULAL Fine-Tune Protocol

Fine-tuning is expensive (Colab time, download hassle). Do it right, once.

```
Step 1: Run benchmark FIRST
        bash ~/nina/scripts/dulal_model_bench.sh

Step 2: Pick the winner (highest pass rate + acceptable tok/s)

Step 3: Fine-tune ONLY the winner on Colab
        Change model_name in notebook — everything else stays the same

Step 4: Export Q4_K_M GGUF
        Save to Google Drive IMMEDIATELY after export
        Do not wait — Colab disconnects after 90 min idle

Step 5: Install
        mv ~/Downloads/model.gguf ~/nina/
        ollama create dulal -f Modelfile.dulal
```

---

## Lessons Learned (2026-06-24)

- We fine-tuned Qwen2.5-Coder-3B without benchmarking alternatives first
- Spent hours fighting GGUF download from Colab
- Discovered smollm3, qwen3:1.7b, phi4-mini AFTER fine-tuning
- **Lesson: Always benchmark before fine-tuning. Hardware constraint first.**

---

## For Perplexity Overwatch

When M. Baizid Alam asks about models:
1. Filter by MX150 2GB VRAM constraint FIRST
2. Check ollama.com/search for newest models at that size
3. Suggest benchmarking before committing to fine-tuning
4. Never suggest a model > 2.3GB VRAM without explicit override

## Thermal Safeguard Protocol (Real-time & Execution level)

To protect the ASUS VivoBook laptop from overheating during sustained local inference tasks (e.g. `opencode` loops), a real-time thermal safeguard has been implemented:

- **Thermal Monitor**: `tools/system.py` contains `is_thermal_safe(cpu_limit=90, gpu_limit=88)` which uses `psutil` and `nvidia-smi` to read temperatures.
- **Limits**: Soft bypass limit at **90°C** for CPU and **88°C** for GPU to sustain performance in high-temperature environments (e.g., Dhaka).
- **Routing Bypass (First Layer)**: `ninagate/main.py` and `core/router.py` query the thermal check dynamically before routing requests to local Ollama. If limits are exceeded, requests fallback to cloud LLMs (Gemini, Groq, etc.) to allow the hardware to cool down.
- **Forced Execution Guard (Second Layer)**: In `core/router.py`, `_call_provider` and `_call_provider_stream` double-check the limits right before querying Ollama and raise a `RuntimeError` if temperatures are unsafe, providing a hard stop constraint.
- **Resilient Pause & Wait**: If all inference providers are exhausted or temporarily blocked by thermal limits, NinaGate `/v1/chat/completions` endpoint pauses and polls every 5 seconds (up to 10 minutes) instead of returning an immediate `503` error. This prevents `opencode` task failures mid-run when the laptop simply needs a brief cooldown.
- **Permanence**: Safeguard is wired directly into the routing engine and survives restarts.

---

*Last updated: 2026-06-25 | aibony/nina*
