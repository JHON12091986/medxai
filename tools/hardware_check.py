import os
import re
import subprocess
import json
import platform
import time # Added import
from typing import Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import core.observability
    EMIT_AVAILABLE = True
except ImportError:
    EMIT_AVAILABLE = False


def get_cpu_info() -> Dict[str, Any]:
    cpu_info = {"brand": "Unknown", "cores": 0, "avx2": False, "avx512": False}
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo_content = f.read()

            # Brand
            brand_match = re.search(r"model name\s*:\s*(.*)", cpuinfo_content, re.IGNORECASE)
            if brand_match:
                cpu_info["brand"] = brand_match.group(1).strip()

            # Cores
            cores_match = re.findall(r"cpu cores\s*:\s*(\d+)", cpuinfo_content)
            if cores_match:
                cpu_info["cores"] = int(cores_match[0])

            # AVX flags
            flags_match = re.search(r"flags\s*:\s*(.*)", cpuinfo_content)
            if flags_match:
                flags = flags_match.group(1).split()
                cpu_info["avx2"] = "avx2" in flags
                cpu_info["avx512"] = "avx512" in flags
        except Exception:
            pass
    return cpu_info

def get_gpu_info() -> Dict[str, Any]:
    gpu_info = {"name": "None", "vram_total_gb": 0, "utilization_percent": 0}
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True, timeout=5
        )
        output = result.stdout.strip().split("\n")[0]
        name, vram_total, utilization = [x.strip() for x in output.split(",")]
        
        gpu_info["name"] = name
        gpu_info["vram_total_gb"] = int(vram_total) // 1024 # Convert MB to GB
        gpu_info["utilization_percent"] = int(utilization)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass # nvidia-smi not found or GPU not available/active
    return gpu_info

def get_ram_info() -> Dict[str, Any]:
    ram_info = {"total_gb": 0, "available_gb": 0}
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            ram_info["total_gb"] = round(mem.total / (1024**3), 2)
            ram_info["available_gb"] = round(mem.available / (1024**3), 2)
        except Exception:
            pass
    return ram_info

def get_ollama_env() -> Dict[str, Any]:
    return {"ollama_num_gpu": os.environ.get("OLLAMA_NUM_GPU", "Not Set")}

def get_llama_cpp_info() -> Dict[str, Any]:
    llama_cpp_info = {"installed": False, "cuda_support": False}
    try:
        import llama_cpp
        llama_cpp_info["installed"] = True
        # Checking for CUDA support in llama_cpp-python is not straightforward programmatically
        # without trying to load a model.
        # A common indicator might be the wheel name (e.g., llama_cpp_python_cuda)
        # or checking the __version__ string if it contains 'cu' or 'cuda'.
        # For simplicity, we'll assume if it's installed and not explicitly marked as CPU-only,
        # it *might* have CUDA support if a CUDA-enabled wheel was installed.
        # A more robust check would involve `llama_cpp.llama_supports_gpu_offload()`,
        # but this requires specific versions and can be tricky.
        # For now, a heuristic: if `cuda` is in the package name or installed locally.

        # A more reliable way: check if `LLAMA_CPP_PYTHON_CMAKE_ARGS` env var was set during install
        if os.environ.get("LLAMA_CPP_PYTHON_CMAKE_ARGS") and "cuda" in os.environ["LLAMA_CPP_PYTHON_CMAKE_ARGS"].lower():
             llama_cpp_info["cuda_support"] = True
        # Alternatively, check for the presence of a CUDA-enabled wheel string
        # This is a heuristic and might not be universally accurate.
        elif any("cuda" in p.name.lower() for p in psutil.Process(os.getpid()).cmdline() if "pip" in p.name.lower()):
             llama_cpp_info["cuda_support"] = True
        elif hasattr(llama_cpp, "llama_supports_gpu_offload") and llama_cpp.llama_supports_gpu_offload():
             llama_cpp_info["cuda_support"] = True
    except ImportError:
        pass
    except Exception:
        pass # Handle other potential issues with llama_cpp module
    return llama_cpp_info


def generate_report() -> Dict[str, Any]:
    report = {
        "timestamp": os.path.getmtime(__file__), # This will be the creation/modification time of the script. Not ideal.
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "ram": get_ram_info(),
        "ollama_env": get_ollama_env(),
        "llama_cpp": get_llama_cpp_info()
    }
    return report

def print_report(report: Dict[str, Any]):
    print("\n--- NINA Hardware Readiness Report ---")
    print(f"Timestamp: {time.ctime(report['timestamp'])}")
    
    cpu = report["cpu"]
    print("\n--- CPU ---")
    print(f"  Brand: {cpu['brand']}")
    print(f"  Cores: {cpu['cores']}")
    print(f"  AVX2 Support: {'✅' if cpu['avx2'] else '❌'}")
    print(f"  AVX512 Support: {'✅' if cpu['avx512'] else '❌'}")

    gpu = report["gpu"]
    print("\n--- GPU ---")
    print(f"  Name: {gpu['name']}")
    print(f"  VRAM Total: {gpu['vram_total_gb']} GB")
    print(f"  Utilization: {gpu['utilization_percent']}%")

    ram = report["ram"]
    print("\n--- RAM ---")
    print(f"  Total: {ram['total_gb']} GB")
    print(f"  Available: {ram['available_gb']} GB")

    ollama_env = report["ollama_env"]
    print("\n--- Ollama Environment ---")
    print(f"  OLLAMA_NUM_GPU: {ollama_env['ollama_num_gpu']}")

    llama_cpp = report["llama_cpp"]
    print("\n--- Llama-cpp-python ---")
    print(f"  Installed: {'✅' if llama_cpp['installed'] else '❌'}")
    print(f"  CUDA Support: {'✅' if llama_cpp['cuda_support'] else '❌'}")
    print("\n------------------------------------\n")

if __name__ == "__main__":
    report = generate_report()
    print_report(report)
    if EMIT_AVAILABLE:
        core.observability.emit("hardware_report", report)
    else:
        print("Warning: core.observability.emit not available. Cannot emit telemetry.")