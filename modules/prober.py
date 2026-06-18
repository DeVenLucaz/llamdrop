import os
import urllib.request
import subprocess
import time
from benchmarks import parse_tps_from_output
from config import load_config, save_config

DUMMY_MODEL_URL = "https://huggingface.co/QuantFactory/tinyllama-15M-alpaca-finetuned-GGUF/resolve/main/tinyllama-15M-alpaca-finetuned.Q4_K_M.gguf"
DUMMY_MODEL_PATH = os.path.expanduser("~/.llamdrop/models/.dummy_benchmark.gguf")

def download_dummy_model():
    if os.path.exists(DUMMY_MODEL_PATH):
        return True
    try:
        os.makedirs(os.path.dirname(DUMMY_MODEL_PATH), exist_ok=True)
        print("  Downloading 15M parameter micro-benchmark model (10MB)...")
        req = urllib.request.Request(DUMMY_MODEL_URL, headers={'User-Agent': 'llamdrop/0.1'})
        with urllib.request.urlopen(req) as response, open(DUMMY_MODEL_PATH, 'wb') as out_file:
            out_file.write(response.read())
        return True
    except Exception as e:
        print(f"  Failed to download dummy model: {e}")
        return False

def run_probe(device_profile, ngl=0):
    threads = getattr(device_profile, "threads", 4) if hasattr(device_profile, "threads") else device_profile.get("optimal_threads", 4)
    cmd = [
        os.path.expanduser("~/.llamdrop/bin/llama-cli"),
        "-m", DUMMY_MODEL_PATH,
        "-n", "500",  # run enough tokens to hit ~10 seconds
        "-p", "Hello world, write a quick poem about hardware testing:",
        "-c", "256",
        "-t", str(threads),
        "-ngl", str(ngl)
    ]
    try:
        # Give it a max of 12 seconds
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        if result.returncode != 0:
            return 0.0
        gen_tps, _ = parse_tps_from_output(result.stderr)
        return gen_tps
    except subprocess.TimeoutExpired as e:
        # Even if it timed out, it might have output some stats in stderr if llama-cli printed them
        err_str = e.stderr if isinstance(e.stderr, str) else (e.stderr.decode() if e.stderr else "")
        gen_tps, _ = parse_tps_from_output(err_str)
        return gen_tps
    except Exception:
        return 0.0

def dynamic_probe_backend(device_profile):
    """
    Test CPU and GPU backends.
    Returns the recommended 'backend' string ("cpu" or "vulkan").
    """
    config = load_config()
    forced_backend = config.get("backend", "auto")
    if forced_backend in ("cpu", "vulkan", "ollama"):
        return forced_backend

    llama_cli = os.path.expanduser("~/.llamdrop/bin/llama-cli")
    if not os.path.exists(llama_cli):
        return "cpu"

    print("  \033[0;36mDynamic Backend Prober starting (10-second micro-benchmark)...\033[0m")
    if not download_dummy_model():
        return "cpu"

    print("  Testing CPU backend...")
    cpu_tps = run_probe(device_profile, ngl=0)
    print(f"  CPU Speed: {cpu_tps} t/s")

    print("  Testing GPU (Vulkan) backend...")
    gpu_tps = run_probe(device_profile, ngl=999)
    print(f"  GPU Speed: {gpu_tps} t/s")

    best = "cpu"
    if gpu_tps > cpu_tps * 1.05 and gpu_tps > 0:
        best = "vulkan"
        print("  \033[0;32mVulkan backend is faster and stable. Selected Vulkan.\033[0m")
    elif cpu_tps > 0:
        print("  \033[0;32mCPU backend is faster or GPU crashed. Selected CPU.\033[0m")

    if cpu_tps > 0 or gpu_tps > 0:
        # Save to config so we don't probe every time
        config["backend"] = best
        save_config(config)

    return best
