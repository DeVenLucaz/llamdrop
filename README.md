# llamdrop 🦙

> **Run AI on any device. No PC. No subscription. No struggle.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Linux%20%7C%20RPi%20%7C%20macOS%20%7C%20Windows-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Free Forever](https://img.shields.io/badge/Free-Forever-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/Version-0.9.5-blue.svg)]()

---

## What is llamdrop?

llamdrop is a **free, open-source** tool that lets anyone run a local AI model on whatever device they own — an Android phone, an old laptop, a Raspberry Pi, a budget PC, even a gaming console running Linux.

It **reads your hardware automatically**, detects your exact chip, RAM, GPU, and platform, then finds AI models that will actually work on your specs, downloads the right quantization, and runs it. You don't need to know what quantization means. You don't need to read any documentation. You just run it.

**llamdrop will always be completely free. It cannot be sold. Ever.**
That's not a promise — it's written into the license (GPL v3).

---

## Who is this for?

This project was born from a real experience — spending hours trying to run local AI on a phone with no PC, no budget, and no guidance. Dozens of crashes, incompatible models, RAM errors with no explanation.

llamdrop is for **anyone on low-end or budget hardware** who keeps getting left out:

- 📱 **Phone users** — Android via Termux, no PC needed
- 💻 **Old laptop owners** — that 2012 laptop collecting dust can run AI
- 🍓 **Raspberry Pi / SBC users** — Pi 4, Pi 5, Orange Pi, etc.
- 🎮 **Console / embedded Linux users** — if it runs Linux, llamdrop runs on it
- 🪟 **Windows users** — native PowerShell installer, no WSL required
- 🍎 **macOS users** — Apple Silicon detected, Ollama backend auto-configured
- 🌍 **Users in regions** where $20/month is not a small amount
- 🧑‍🎓 **Students and self-learners** wanting to experiment with AI for free
- 🔧 **Developers and tinkerers** who want to test local AI on constrained hardware

**If you've ever given up trying to run local AI because it was too complicated, crashed too many times, or cost too much — this is for you.**

---

## Quick Install

**Android (Termux) / Linux / Raspberry Pi / macOS:**

```bash
curl -sL https://raw.githubusercontent.com/DeVenLucaz/llamdrop/main/install.sh | bash
```

**Windows (PowerShell, run as Administrator):**

```powershell
irm https://raw.githubusercontent.com/DeVenLucaz/llamdrop/main/install.ps1 | iex
```

Then run:

```bash
llamdrop
```

Two commands. No compilation. No configuration. No account needed.

---

## Features

### Device Intelligence
- 🔍 **Full device profiling** — reads RAM, CPU model, core layout (big.LITTLE aware), CPU flags (AVX2/AVX512/NEON), GPU vendor, storage, Android SoC/API level
- 🖥️ **7-tier classification** — Micro / Low / Low-Mid / Mid / High / Desktop / Workstation — auto-configures everything per tier
- 🧠 **Backend auto-selection** — picks the correct backend for every platform×GPU combination: Termux pkg, CUDA, ROCm, Vulkan, Metal/Ollama, IPEX-LLM, or CPU
- ⚡ **GPU acceleration** — Vulkan for Adreno/Mali/AMD desktop, CUDA for NVIDIA, Metal via Ollama on Apple Silicon
- 🚫 **Android GPU safety** — never forces GPU on Android (Mali Vulkan is slower than CPU; Adreno crashes). CPU-only, no guessing.
- 👋 **First-launch Device Profile** — shows detected specs card with tier, backend decision, runtime flags, and model recommendations. Runs once.

### Model Browser & Download
- 📋 **Smart model browser** — two modes:
  - ✅ **Verified catalog** — 41 curated models confirmed working across all device tiers, filtered automatically to show only what fits your hardware
  - 🔎 **Live HuggingFace search** — search any GGUF model with live RAM estimates
- ⬇️ **Resilient downloader** — auto-resumes on connection drops, retries automatically, verifies via SHA-256 checksum
- 🎯 **Smart quantization** — picks the best Q4/Q2/Q5/IQ variant based on your *live* RAM at download time
- 🧩 **IQ quant support** — IQ3_M and IQ2_M variants — better quality than Q2_K at same RAM. Vulkan auto-disabled for IQ quants.
- 📊 **Benchmark scores** — tokens/second recorded per model (rolling average, last 5 runs)
- 🗂️ **Cancelled download cleanup** — partial files deleted immediately on cancel

### Chat & Inference
- 🤖 **Ollama backend** — auto-detected on Linux/desktop and macOS, hardware-aware auto-tuning
- 💬 **Stable chat** — automatic context trimming prevents out-of-memory crashes. First exchange always preserved.
- 🦙 **Live thinking indicator** — animated spinner with non-blocking stdout while the model generates
- 🎯 **Prompt format auto-detect** — correct template per model family (ChatML, Llama3, Gemma, Phi3)
- 📂 **File context** — attach a file to your conversation before chatting
- 💾 **Session save/load/delete** — resume conversations where you left off, auto-save every 5 exchanges
- 📤 **Chat export** — `/export` saves conversation to Downloads as markdown
- 🧹 **Clean output pipeline** — llama.cpp banner, duplicate responses, timing stats, and format tags all stripped

### System & UX
- ⚠️ **Live RAM monitor** — colour-coded bar in UI (green/yellow/red)
- 🔋 **Battery monitoring** — shows charge %, per-inference battery drop, warns at configurable low threshold
- 📂 **Phone-wide GGUF scanner** — finds models already on your device. Runs in background — UI stays responsive.
- 🆙 **Self-update** — `llamdrop update` pulls latest version from GitHub
- 🩺 **Doctor** — `llamdrop doctor` checks binary, libraries, RAM, storage, network, Python version, Termux permissions, and Ollama status. `--cleanup` removes orphaned partial downloads.
- ⚙️ **Config file** — override threads, context, temperature, system prompt, auto-save, battery threshold at `~/.llamdrop/config.json`. Hot-reloads on external edits.
- 🌐 **Multi-language UI** — English, Hindi, Spanish, Portuguese, Arabic
- 🖥️ **Curses TUI** — keyboard-navigable menu with live RAM bar, battery line, llama.cpp + GPU status
- ⚡ **Fast startup** — hardware detection runs exactly once at launch

---

## Model Catalog

**Current verified catalog (41 models across 6 tiers):**

| Tier | Available RAM | Example Models |
|---|---|---|
| Micro | < 1 GB | SmolLM2 135M / 360M / 1.7B, Qwen2.5 0.5B, TinyLlama, Gemma 3 1B, Qwen3 1.7B |
| Low | 1 – 3 GB | Qwen2.5 1.5B, Llama 3.2 1B, DeepSeek R1 1.5B, Gemma 2 2B, Phi-4 Mini, Qwen3 4B, SmolLM3 3B |
| Low-Mid | 3 – 6 GB | Mistral 7B, Llama 3.1 8B, DeepSeek R1 7B, Qwen2.5 7B, Phi-3.5 Mini, Llama 3.2 3B |
| Mid | 6 – 12 GB | Gemma 3 12B, Qwen3 8B, Phi-4 14B, DeepSeek R1 14B, Mistral NeMo 12B |
| High | 12 – 24 GB | Gemma 3 27B, Qwen3 32B, DeepSeek R1 32B, Qwen2.5 Coder 32B |
| Desktop | 24 GB+ | Llama 3.3 70B, Qwen2.5 72B, DeepSeek R1 70B |

All verified models are free, open-source, and downloadable without login or account.
The browser automatically hides models outside your device's tier — you only see what can actually run.

---

## Usage

```bash
llamdrop              # Launch UI
llamdrop update       # Update to latest version
llamdrop doctor       # Check install health
llamdrop doctor --cleanup  # Remove orphaned partial downloads
llamdrop version      # Show version
```

**Chat commands:** `/help` `/export` `/clear` `/ram` `/quit`

For full usage guides, see the [Wiki](https://github.com/DeVenLucaz/llamdrop/wiki).

---

## Supported Platforms

| Platform | Status | Notes |
|---|---|---|
| Android via Termux | 🎯 Primary test platform | Built and tested here first |
| Linux laptop / desktop | ✅ Fully supported | Any distro, x86_64 or ARM64 |
| Raspberry Pi 4 / 5 | ✅ Fully supported | ARM64 |
| macOS (Apple Silicon) | ✅ Fully supported | Ollama backend, GPU_LAYERS=999 |
| macOS (Intel) | ✅ Fully supported | CPU backend |
| Windows (native) | ✅ Fully supported | PowerShell installer, CUDA/Vulkan auto-detected |
| Old Windows PC (WSL2) | ✅ Supported | Via Windows Subsystem for Linux |
| Chromebook (Linux mode) | 🔄 Should work | ARM64 or x86_64 |
| Orange Pi / SBC | 🔄 Should work | ARM64 Linux |
| iOS | ❌ Not supported | No proper terminal environment |

---

## Project Structure

```
llamdrop/
├── llamdrop.py          # Main entry point + CLI (update, doctor, version)
├── install.sh           # One-line installer (Linux/Android/macOS/WSL)
├── install.ps1          # Native Windows PowerShell installer
├── models.json          # Verified model catalog (41 models, 6 tiers)
├── CHANGELOG.md         # Full version history
├── modules/
│   ├── specs.py         # Full device profiling — DeviceProfile dataclass, tier, backend, flags
│   ├── device.py        # Hardware detection bridge + legacy compat
│   ├── browser.py       # Model browser — verified catalog + HF live search
│   ├── downloader.py    # Resilient downloader + GGUF phone scanner
│   ├── launcher.py      # llama.cpp wrapper + Vulkan + mmap + DeviceProfile-aware
│   ├── chat.py          # Chat loop + inference extraction + backend dispatch
│   ├── ram_monitor.py   # Live RAM tracking and display
│   ├── hf_search.py     # Live HuggingFace search
│   ├── i18n.py          # Multi-language UI strings (EN/HI/ES/PT/AR)
│   ├── updater.py       # Self-update + background catalog updater
│   ├── benchmarks.py    # Tokens/sec benchmark storage (rolling average, 5 runs)
│   ├── doctor.py        # Install health checker + partial download cleanup
│   ├── config.py        # User config file with mtime-aware hot-reload
│   ├── battery.py       # Battery monitoring during inference
│   ├── filecontext.py   # File attachment for chat context
│   └── backends/
│       ├── __init__.py  # Backends package
│       └── ollama.py    # Ollama HTTP backend (auto-detected)
├── tests/
│   ├── test_specs.py    # Hardware tiering + device profiling tests
│   └── test_prompts.py  # Prompt builder tests (ChatML, Llama3, etc.)
└── docs/
    ├── CONTRIBUTING.md  # How to contribute
    └── DEVICES.md       # Community device compatibility list
```

---

## Roadmap

### v0.9.5 — Current
- [x] RAM monitoring unified — single source of truth across all modules
- [x] Inference blocking fixed — non-blocking stdout, smooth "Thinking..." animation
- [x] Ollama first-class — hardware-aware auto-tuning, same as llama.cpp path
- [x] Formal test suite added — `tests/` with 6 passing tests
- [x] `doctor --cleanup` — detects and removes orphaned partial downloads
- [x] GitHub URL migration — all references updated to DeVenLucaz/llamdrop

### v1.0 — Planned
- [ ] Web-based model catalog (GitHub Pages)
- [ ] Community device profile submissions
- [ ] `/doc` command — document chat with chunking (no vector DB needed)
- [ ] llamdrop server mode — run on phone, access from browser on WiFi
- [ ] Streaming tokens via Ollama backend
- [ ] Multiple file context — attach more than one file to a conversation

---

## Contributing

You don't need to be a developer to contribute:

- 📲 **Test a model** on your device → open a PR to update `models.json`
- 🌐 **Translate** the UI into your language
- 📝 **Write a setup guide** for your specific device
- 🐛 **Report a crash** via GitHub Issues
- ⭐ **Star this repo** — it helps others find it when they need it most

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for full details.

---

## License

**GNU General Public License v3.0** — see [LICENSE](LICENSE)

- ✅ Free to use forever
- ✅ Free to modify and share
- ❌ Cannot be sold
- ❌ Cannot be made closed-source
- ❌ Cannot be put behind a paywall

**llamdrop will always be free. That is non-negotiable.**

---

## The Story

> This project started because one vibe-coder spent hours trying to run local AI on an Oppo F19 Pro+ with no PC and no budget. Dozens of crashes. Models that were incompatible. RAM errors with no explanation. When it finally worked — with a tiny 1.5B model running in Termux — the thought was: nobody should have to go through all of that just to get started.
>
> llamdrop is the tool that should have existed already.

Built by [@DeVenLucaz](https://github.com/DeVenLucaz) and contributors.
If llamdrop helped you, star the repo and share it with someone who needs it.
