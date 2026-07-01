#!/usr/bin/env bash
# =============================================================================
# hw_probe.sh — Nina Hardware Capability Report
# 1-click: CPU ISA flags + iGPU + dGPU + RAM + Bus Speed + CUDA caps
# Usage: sudo bash ~/nina/scripts/hw_probe.sh
# =============================================================================
# NOTE: intentionally NO set -euo pipefail — grep -c returning 0 would abort

BOLD=$(tput bold   2>/dev/null || printf '')
RESET=$(tput sgr0  2>/dev/null || printf '')
CYAN=$(tput setaf 6 2>/dev/null || printf '')
GREEN=$(tput setaf 2 2>/dev/null || printf '')
YELLOW=$(tput setaf 3 2>/dev/null || printf '')
RED=$(tput setaf 1 2>/dev/null || printf '')

section() { echo; echo "${CYAN}${BOLD}══ $1 ══${RESET}"; }
row()     { printf "  ${GREEN}%-32s${RESET} %s\n" "$1" "$2"; }
warn()    { echo "  ${YELLOW}⚠  $1${RESET}"; }
ok()      { echo "  ${GREEN}✓  $1${RESET}"; }
miss()    { echo "  ${RED}✗  $1${RESET}"; }

echo
echo "${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
echo "${BOLD}║   NINA Hardware Probe — $(date '+%Y-%m-%d %H:%M')        ║${RESET}"
echo "${BOLD}╚══════════════════════════════════════════════════╝${RESET}"

# ── CPU ───────────────────────────────────────────────────────────────────────
section "CPU"
CPU_MODEL=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)
PHYSICAL_CORES=$(grep '^cpu cores' /proc/cpuinfo | head -1 | awk '{print $NF}')
LOGICAL_CORES=$(nproc)
CPU_ARCH=$(uname -m)
MIN_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq 2>/dev/null \
           | awk '{printf "%.0f MHz", $1/1000}')
MAX_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null \
           | awk '{printf "%.0f MHz", $1/1000}')
CUR_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null \
           | awk '{printf "%.0f MHz", $1/1000}')
CPU_GOVERNOR=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "N/A")
L3_CACHE=$(grep -m1 'cache size' /proc/cpuinfo | cut -d: -f2 | xargs 2>/dev/null || echo "N/A")

row "Model"           "$CPU_MODEL"
row "Architecture"    "$CPU_ARCH"
row "Physical cores"  "$PHYSICAL_CORES"
row "Logical threads" "$LOGICAL_CORES"
row "Freq (min/max)"  "${MIN_FREQ:-N/A} / ${MAX_FREQ:-N/A}"
row "Freq (current)"  "${CUR_FREQ:-N/A}"
row "Governor"        "$CPU_GOVERNOR"
row "L3 Cache"        "$L3_CACHE"

[ "$CPU_GOVERNOR" = "powersave" ] && \
  warn "Governor='powersave' — throttled! Fix: echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"

# ── CPU INSTRUCTION SETS ──────────────────────────────────────────────────────
section "CPU Instruction Sets"
FLAGS=$(grep -m1 '^flags' /proc/cpuinfo | cut -d: -f2)

check_flag() {
  local label="$1"; shift
  local found=0
  for f in "$@"; do
    echo "$FLAGS" | grep -qw "$f" && found=1 && break
  done
  if [ "$found" = "1" ]; then
    printf "  ${GREEN}✓${RESET} %-18s" "$label"
  else
    printf "  ${RED}✗${RESET} %-18s" "$label"
  fi
}

echo
echo "  ${BOLD}── x87 / Base ──────────────────────────────────────────${RESET}"
printf "  "; check_flag "FPU"        fpu;       check_flag "CMOV"       cmov;      echo
printf "  "; check_flag "CMPXCHG16B" cx16;      check_flag "POPCNT"     popcnt;    echo

echo "  ${BOLD}── SIMD / Vector ───────────────────────────────────────${RESET}"
printf "  "; check_flag "MMX"        mmx;       check_flag "SSE"        sse;       echo
printf "  "; check_flag "SSE2"       sse2;      check_flag "SSE3"       pni;       echo
printf "  "; check_flag "SSSE3"      ssse3;     check_flag "SSE4.1"     sse4_1;    echo
printf "  "; check_flag "SSE4.2"     sse4_2;    check_flag "AVX"        avx;       echo
printf "  "; check_flag "AVX2"       avx2;      check_flag "AVX-512F"   avx512f;   echo
printf "  "; check_flag "FMA3"       fma;       check_flag "F16C"       f16c;      echo

echo "  ${BOLD}── Security / Crypto ───────────────────────────────────${RESET}"
printf "  "; check_flag "AES-NI"     aes;       check_flag "SHA"        sha_ni;    echo
printf "  "; check_flag "RDRAND"     rdrand;    check_flag "RDSEED"     rdseed;    echo
printf "  "; check_flag "PCLMULQDQ"  pclmulqdq; check_flag "VAES"       vaes;      echo

echo "  ${BOLD}── Virt / Other ────────────────────────────────────────${RESET}"
printf "  "; check_flag "VMX (VT-x)" vmx;       check_flag "SMEP"       smep;      echo
printf "  "; check_flag "SMAP"       smap;      check_flag "RDTSCP"     rdtscp;    echo
printf "  "; check_flag "LAHF-LM"    lahf_lm;   check_flag "HYPERVISOR" hypervisor; echo

echo
echo "  ${BOLD}→ LLM inference relevance:${RESET}"
if echo "$FLAGS" | grep -qw avx512f; then
  ok "AVX-512 present — llama.cpp AVX512 kernel (fastest CPU path)"
elif echo "$FLAGS" | grep -qw avx2; then
  ok "AVX2 present — llama.cpp AVX2 kernel (good)"
elif echo "$FLAGS" | grep -qw avx; then
  warn "AVX only (no AVX2) — inference slower, consider GPU offload"
else
  warn "No AVX — very slow CPU inference, GPU offload strongly recommended"
fi
echo "$FLAGS" | grep -qw fma   && ok "FMA3 present — fused multiply-add improves GEMM throughput"
echo "$FLAGS" | grep -qw f16c  && ok "F16C present — hardware FP16↔FP32 conversion (helps quantized models)"
echo "$FLAGS" | grep -qw aes   && ok "AES-NI present — hardware AES acceleration"

# ── RAM ───────────────────────────────────────────────────────────────────────
section "RAM"
TOTAL_RAM_KB=$(grep MemTotal    /proc/meminfo | awk '{print $2}')
AVAIL_RAM_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$(awk "BEGIN {printf \"%.1f GB\", ${TOTAL_RAM_KB}/1048576}")
AVAIL_RAM_GB=$(awk "BEGIN {printf \"%.1f GB\", ${AVAIL_RAM_KB}/1048576}")
SWAP_TOTAL=$(grep SwapTotal /proc/meminfo | awk '{printf "%.1f GB", $2/1048576}')
SWAP_FREE=$( grep SwapFree  /proc/meminfo | awk '{printf "%.1f GB", $2/1048576}')

row "Total RAM"     "$TOTAL_RAM_GB"
row "Available RAM" "$AVAIL_RAM_GB"
row "Swap total"    "$SWAP_TOTAL"
row "Swap free"     "$SWAP_FREE"

# dmidecode block — isolated, never aborts script
if command -v dmidecode &>/dev/null; then
  DMI_OUT=$(dmidecode -t memory 2>/dev/null || true)
  RAM_TYPE=$(echo "$DMI_OUT"  | grep -i '^\s*Type:'  \
    | grep -v 'Unknown\|Error\|Detail\|Correction'   \
    | head -1 | awk '{print $NF}' || true)
  RAM_SPEED=$(echo "$DMI_OUT" \
    | grep -i 'Configured Memory Speed\|Configured Clock Speed' \
    | grep -v 'Unknown\|0 MT' | head -1 \
    | awk '{print $(NF-1), $NF}' | xargs 2>/dev/null || true)
  # grep -c returns exit 1 when count=0, so use || true
  RAM_SLOTS=$(echo "$DMI_OUT" | grep -c 'Size:.*GB\|Size:.*MB' || true)
  row "RAM Type"    "${RAM_TYPE:-N/A}"
  row "RAM Speed"   "${RAM_SPEED:-N/A}"
  row "Slots used"  "${RAM_SLOTS:-N/A}"
else
  warn "dmidecode not found — install: sudo apt install dmidecode"
fi

TOTAL_GB_NUM=$(awk "BEGIN {printf \"%.0f\", ${TOTAL_RAM_KB}/1048576}")
if   [ "$TOTAL_GB_NUM" -ge 16 ]; then BUS_EST="~42 GB/s (DDR4-2666 dual-ch est.)"
elif [ "$TOTAL_GB_NUM" -ge 8  ]; then BUS_EST="~38 GB/s (DDR4-2400 dual-ch est.)"
else                                   BUS_EST="~25 GB/s (DDR3/single-ch est.)"
fi
row "Bus bandwidth" "$BUS_EST"

AVAIL_GB=$(awk "BEGIN {printf \"%.1f\", ${AVAIL_RAM_KB}/1048576}")
echo
echo "  ${BOLD}→ Model fit (current free RAM = ${AVAIL_GB} GB):${RESET}"
awk -v a="$AVAIL_GB" 'BEGIN {
  printf "    7B  Q4_K_M (~4.1 GB):  "
  if (a+0 > 5.5) printf "\033[32m✓ fits  (%.1f GB headroom)\033[0m\n", a-4.1
  else            printf "\033[33m⚠ tight (%.1f GB headroom)\033[0m\n", a-4.1
  printf "    3B  Q4_K_M (~2.0 GB):  "
  if (a+0 > 3.0) printf "\033[32m✓ fits  (%.1f GB headroom)\033[0m\n", a-2.0
  else            printf "\033[31m✗ insufficient\033[0m\n"
  printf "    1.5B Q4_K_M (~1.0 GB): "
  if (a+0 > 1.5) printf "\033[32m✓ fits  (%.1f GB headroom)\033[0m\n", a-1.0
  else            printf "\033[31m✗ insufficient\033[0m\n"
}'

# ── iGPU ──────────────────────────────────────────────────────────────────────
section "iGPU (Intel Integrated)"
IGPU_NAME=$(lspci 2>/dev/null | grep -i 'VGA\|Display\|3D' | grep -i intel \
            | head -1 | cut -d: -f3 | xargs 2>/dev/null || echo "Not detected")
IGPU_DRIVER="N/A"; IGPU_FREQ_MAX="N/A"; IGPU_FREQ_CUR="N/A"
if [ -d /sys/class/drm/card0 ]; then
  IGPU_DRIVER=$(grep DRIVER /sys/class/drm/card0/device/uevent 2>/dev/null \
                | cut -d= -f2 || echo "N/A")
  IGPU_FREQ_MAX=$(cat /sys/class/drm/card0/gt_max_freq_mhz 2>/dev/null || echo "N/A")
  IGPU_FREQ_CUR=$(cat /sys/class/drm/card0/gt_cur_freq_mhz 2>/dev/null || echo "N/A")
fi
row "Model"    "${IGPU_NAME:-Not detected}"
row "Driver"   "$IGPU_DRIVER"
row "Max freq" "${IGPU_FREQ_MAX} MHz"
row "Cur freq" "${IGPU_FREQ_CUR} MHz"

if command -v clinfo &>/dev/null; then
  CL_DEVS=$(clinfo 2>/dev/null | grep -c 'Device Name' || true)
  row "OpenCL devices" "${CL_DEVS:-0} found"
else
  warn "clinfo not installed — sudo apt install clinfo"
fi
echo "  ${BOLD}→ Ollama:${RESET} iGPU not used for inference (no CUDA/ROCm on Intel i915)."

# ── dGPU ──────────────────────────────────────────────────────────────────────
section "dGPU (NVIDIA Discrete)"
DGPU_NAME=$(lspci 2>/dev/null | grep -i 'VGA\|Display\|3D' | grep -i nvidia \
            | head -1 | cut -d: -f3 | xargs 2>/dev/null || echo "")

if command -v nvidia-smi &>/dev/null; then
  DGPU_FULLNAME=$(nvidia-smi --query-gpu=name            --format=csv,noheader 2>/dev/null || echo "${DGPU_NAME:-N/A}")
  DGPU_DRIVER=$(  nvidia-smi --query-gpu=driver_version  --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_VRAM=$(    nvidia-smi --query-gpu=memory.total    --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_VRAM_FREE=$(nvidia-smi --query-gpu=memory.free   --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_VRAM_USED=$(nvidia-smi --query-gpu=memory.used   --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_TEMP=$(    nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_UTIL=$(    nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_CUDA=$(    nvidia-smi --query-gpu=compute_cap     --format=csv,noheader 2>/dev/null || echo "N/A")
  DGPU_POWER=$(   nvidia-smi --query-gpu=power.draw      --format=csv,noheader 2>/dev/null || echo "N/A")

  row "Model"       "$DGPU_FULLNAME"
  row "Driver"      "$DGPU_DRIVER"
  row "CUDA cap"    "$DGPU_CUDA"
  row "VRAM total"  "$DGPU_VRAM"
  row "VRAM free"   "$DGPU_VRAM_FREE"
  row "VRAM used"   "$DGPU_VRAM_USED"
  row "Temp"        "${DGPU_TEMP}°C"
  row "Utilization" "$DGPU_UTIL"
  row "Power draw"  "$DGPU_POWER"

  # CUDA capability matrix
  section "CUDA / GPU Instruction Sets"
  CUDA_CAP_RAW=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | tr -d '.' || echo "0")
  CUDA_CAP_NUM="${CUDA_CAP_RAW:-0}"
  echo "  CUDA Compute Capability: ${BOLD}${DGPU_CUDA}${RESET}"
  echo
  awk -v cap="$CUDA_CAP_NUM" 'BEGIN {
    def = "\033[31m✗ no\033[0m"
    yn  = "\033[32m✓ yes\033[0m"
    printf "  %-30s %s\n", "Tensor Cores (INT8/FP16):", (cap+0>=70) ? yn" (sm_"cap")" : def" (need sm_70+)"
    printf "  %-30s %s\n", "BF16 Tensor Cores:",        (cap+0>=80) ? yn" (sm_"cap")" : def" (need sm_80+)"
    printf "  %-30s %s\n", "FP8 (Ada/Hopper):",         (cap+0>=89) ? yn" (sm_"cap")" : def" (need sm_89+)"
    printf "  %-30s %s\n", "Unified Memory:",            (cap+0>=30) ? yn : def
    printf "  %-30s %s\n", "Cooperative Groups:",        (cap+0>=60) ? yn : def
    printf "  %-30s %s\n", "Dynamic Parallelism:",       (cap+0>=35) ? yn : def
    printf "  %-30s %s\n", "CUDA Graphs:",               (cap+0>=60) ? yn : def
    printf "  %-30s %s\n", "Flash Attention 2:",         (cap+0>=80) ? yn" (sm_80+)" : "\033[33m⚠ partial/slow (need sm_80+)\033[0m"
    printf "  %-30s %s\n", "INT4 / NF4 quant (GGUF):",  (cap+0>=61) ? yn : "\033[33m⚠ limited\033[0m"
  }'

  echo
  if command -v nvcc &>/dev/null; then
    NVCC_VER=$(nvcc --version 2>/dev/null | grep release | awk '{print $5}' | tr -d , || echo "N/A")
    ok "CUDA toolkit: nvcc $NVCC_VER"
  else
    warn "nvcc not found — CUDA toolkit not installed (Ollama doesn't need it, but torch/training does)"
  fi

  PY_CUDA=$(python3 -c "import torch; print('yes' if torch.cuda.is_available() else 'no')" 2>/dev/null || echo "no")
  if [ "$PY_CUDA" = "yes" ]; then
    TORCH_VER=$(python3 -c "import torch; print(torch.version.cuda)" 2>/dev/null || echo "N/A")
    ok "PyTorch CUDA available — cuda $TORCH_VER"
  else
    warn "PyTorch CUDA not available (pip install torch --index-url https://download.pytorch.org/whl/cu121)"
  fi

  # VRAM fit
  VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | xargs || echo "0")
  echo
  echo "  ${BOLD}→ Ollama GPU offload (num_gpu):${RESET}"
  awk -v vram="$VRAM_MB" 'BEGIN {
    printf "    7B  Q4 (~4100 MB VRAM):  "
    if   (vram+0 >= 4100) printf "\033[32m✓ full offload   → num_gpu 99\033[0m\n"
    else if (vram+0 >= 2048) printf "\033[33m⚠ partial        → num_gpu ~18\033[0m\n"
    else                  printf "\033[31m✗ CPU only       → num_gpu 0\033[0m\n"
    printf "    3B  Q4 (~2000 MB VRAM):  "
    if   (vram+0 >= 2000) printf "\033[32m✓ full offload   → num_gpu 99\033[0m\n"
    else                  printf "\033[31m✗ CPU only       → num_gpu 0\033[0m\n"
    printf "    1.5B Q4 (~1000 MB VRAM): "
    if   (vram+0 >= 1000) printf "\033[32m✓ full offload   → num_gpu 99\033[0m\n"
    else                  printf "\033[31m✗ insufficient\033[0m\n"
  }'

else
  # nvidia-smi not found — still show what lspci sees
  if [ -n "$DGPU_NAME" ]; then
    row "Model (lspci)" "$DGPU_NAME"
    warn "nvidia-smi not found — NVIDIA drivers not installed"
    warn "Install: sudo ubuntu-drivers autoinstall  OR  sudo apt install nvidia-driver-535"
  else
    echo "  No NVIDIA dGPU detected via lspci."
    echo "  (This machine uses CPU-only inference via Ollama.)"
  fi
fi

# ── Ollama Runtime ────────────────────────────────────────────────────────────
section "Ollama Runtime"
if command -v ollama &>/dev/null; then
  OLLAMA_VER=$(ollama --version 2>/dev/null || echo "N/A")
  row "Ollama version" "$OLLAMA_VER"
  if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    row "Status" "${GREEN}● running${RESET}"
    LOADED=$(curl -sf http://localhost:11434/api/ps 2>/dev/null \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print(', '.join(m['name'] for m in d.get('models',[])) or 'none')" \
      2>/dev/null || echo "N/A")
    row "Loaded models" "$LOADED"
    AVAIL_MODELS=$(curl -sf http://localhost:11434/api/tags 2>/dev/null \
      | python3 -c "
import json,sys
d=json.load(sys.stdin)
ms=[m['name'] for m in d.get('models',[])]
print(', '.join(ms[:6]) + ('...' if len(ms)>6 else ''))
" 2>/dev/null || echo "N/A")
    row "Available" "$AVAIL_MODELS"
    if curl -sf http://localhost:11434/api/tags 2>/dev/null | grep -q dulal; then
      row "DULAL model" "${GREEN}✓ ready${RESET}"
    else
      row "DULAL model" "${RED}✗ not built${RESET}"
      warn "Build: ollama create dulal -f ~/nina/Modelfile.dulal"
    fi
  else
    row "Status" "${RED}✗ not running${RESET}"
    warn "Start: systemctl --user start ollama"
  fi
else
  warn "Ollama not installed — https://ollama.com/download"
fi

# ── DULAL Summary ─────────────────────────────────────────────────────────────
section "DULAL Recommended Modelfile Params"
echo
printf "  ${BOLD}%-20s${RESET} ${GREEN}%s${RESET}\n" "num_thread"  "${PHYSICAL_CORES}       # physical cores only"
printf "  ${BOLD}%-20s${RESET} ${GREEN}%s${RESET}\n" "num_batch"   "512     # fits i5-8265U L3 (6 MB)"
printf "  ${BOLD}%-20s${RESET} ${GREEN}%s${RESET}\n" "num_ctx"     "16384   # safe with ${TOTAL_RAM_GB} RAM"
printf "  ${BOLD}%-20s${RESET} ${GREEN}%s${RESET}\n" "num_predict" "2048"

if command -v nvidia-smi &>/dev/null; then
  VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | xargs || echo "0")
  awk -v vram="$VRAM_MB" 'BEGIN {
    if   (vram+0 >= 4100) val="99    # full GPU offload"
    else if (vram+0 >= 2048) val="18    # partial GPU offload"
    else                  val="0     # CPU only"
    printf "  \033[1m%-20s\033[0m \033[32m%s\033[0m\n", "num_gpu", val
  }'
else
  printf "  ${BOLD}%-20s${RESET} ${YELLOW}%s${RESET}\n" "num_gpu" "0     # no nvidia-smi detected"
fi

echo
echo "${BOLD}════════════════════════════════════════════════════${RESET}"
echo "  Done. Paste params above into Modelfile.dulal"
echo "  then: ${BOLD}ollama create dulal -f ~/nina/Modelfile.dulal${RESET}"
echo "${BOLD}════════════════════════════════════════════════════${RESET}"
echo
