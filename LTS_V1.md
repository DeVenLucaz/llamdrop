# LLAMdrop 1.0 LTS (Long-Term Support) Master Plan

## Vision & Philosophy
This document outlines the final architectural roadmap for LLAMdrop version 1.0 (LTS). The goal of this release is to solidify LLAMdrop as the premier local AI runner for constrained environments (Termux, Linux, SBCs), decoupling it from desktop-focused bloated architectures, and ensuring it can run independently and reliably for years without constant developer maintenance. Above all, it respects the Unix philosophy: provide sensible, safe defaults, but give the user ultimate freedom to override any setting.

---

## 1. Trimming & Focusing (The "Core" Pivot)

**Feature:** Remove Windows & macOS Support.
*   **Logic:** Delete `install.ps1`, remove WMI/macOS hardware polling (`device.py`, `specs.py`), and remove OS-specific backend logic (e.g., Metal/Ollama macOS auto-detect).
*   **Reasoning:** Windows and macOS users have access to heavy, VC-backed desktop apps (LM Studio, Ollama). Trying to support them dilutes the codebase and complicates hardware detection. By dropping them, LLAMdrop becomes hyper-focused on the platforms that need it most: Android (Termux), Linux, and Raspberry Pi. This massively simplifies testing and maintenance.

**Feature:** Drop the "Desktop (24GB+)" Tier.
*   **Logic:** Remove the 70B+ model recommendations and the 24GB+ tier from the catalog.
*   **Reasoning:** LLAMdrop is designed for budget hardware. Recommending massive enterprise-grade models contradicts the project's identity. We will focus purely on Micro (under 1GB) up to Mid (12GB) tiers.

---

## 2. Content & Discovery

**Feature:** Dynamic Catalog (`models.json`) Updates.
*   **Logic:** Move `models.json` to a remote URL (like GitHub raw/Pages). The app silently fetches the latest catalog in the background on launch (or once every 24 hours) and caches it locally.
*   **Reasoning:** Prevents the app from feeling outdated. Users get new models instantly without having to run `llamdrop update` to update the core application binary.

**Feature:** Massive Catalog Expansion & Pruning.
*   **Logic:** Remove obsolete models (e.g., TinyLlama) and aggressively add the latest high-efficiency models from all major providers (Google Gemma 3, Qwen 2.5/3, DeepSeek R1, Phi-4). 
*   **Reasoning:** The open-weight space moves fast. Providing the absolute best models for constrained RAM ensures users have the highest quality experience possible on low-end hardware.

**Feature:** UI Filters (Category & Provider).
*   **Logic:** Implement interactive TUI filters to sort models by `Category` (Chat, Coding, Reasoning, Multilingual, Fast) and by `Provider` (Google, Meta, Alibaba, Microsoft, DeepSeek).
*   **Reasoning:** A massive catalog is useless if the user can't find what they need. This allows a user to instantly find a "Coding model from Alibaba that fits in 3GB of RAM."

**Feature:** Wildcard Search Overhaul.
*   **Logic:** Allow users to paste a direct Hugging Face repo URL (e.g., `bartowski/Model-GGUF`), which instantly parses the GGUF files and calculates RAM. Upgrade the text search to prioritize "Trending" models and strictly filter for the `gguf` tag. Add bold UI warnings if a selected model exceeds physical RAM.
*   **Reasoning:** Users shouldn't be locked into our catalog. If a new model drops on Twitter, they should be able to paste the URL and run it immediately, safely.

---

## 3. Intelligence & Stability (LTS Durability)

**Feature:** Dynamic Backend Probing.
*   **Logic:** On first launch, run a 10-second micro-benchmark with a 15M parameter dummy model. Test the CPU backend, then test the GPU (Vulkan) backend. Whichever produces tokens faster without crashing becomes the default backend.
*   **Reasoning:** Hardcoded rules (like `if Mali: disable Vulkan`) are brittle and break when new chips are released. Probing lets the hardware prove what it can handle, making the app future-proof for years.

**Feature:** Independent Engine Updates (`llamdrop engine-update`).
*   **Logic:** Create a dedicated command that only fetches and compiles/installs the latest `llama.cpp` backend, bypassing the main application update loop.
*   **Reasoning:** If LLAMdrop stops receiving UI updates, the underlying AI engine can still be updated by the user to gain performance boosts from the `ggerganov/llama.cpp` upstream.

**Feature:** Dynamic Prompt Templates.
*   **Logic:** Instead of hardcoding `ChatML` or `Llama3` logic, the app fetches `tokenizer_config.json` directly from the model's Hugging Face repo to dynamically construct the chat template.
*   **Reasoning:** Prevents the app from breaking when "Llama 4" or "Qwen 5" releases with a completely new template format in the future.

**Feature:** The Auto-Heal Doctor (`llamdrop doctor --fix`).
*   **Logic:** Upgrade the diagnostic tool to automatically repair broken Termux environments, fix permissions, redownload missing dependencies, and reset corrupted configs.
*   **Reasoning:** Zero-maintenance support. If something breaks locally, the app can fix itself.

**Feature:** Offline Resilience.
*   **Logic:** Aggressively cache the catalog, images, and search queries locally.
*   **Reasoning:** If the user has no internet (or Hugging Face API changes/goes down), the app silently falls back to the cache so they can still chat with their downloaded models without crashing.

---

## 4. Absolute User Freedom (Power User Overrides)

**Feature:** The "Power User" Overrides.
*   **Logic:** Ensure every "smart" or "safety" feature can be bypassed via `~/.llamdrop/config.json` or hotkeys.
    *   **Throttling:** Allow users to disable battery/thermal throttling (`"allow_thermal_melt": true`).
    *   **Backend Selection:** Allow users to force a specific backend (e.g., `--backend vulkan`) ignoring the Dynamic Prober's recommendation.
    *   **RAM Limits:** Add a toggle `[U: Unhide Unsupported Models]` to unhide models that exceed the device's physical RAM, allowing users to experiment with massive swap files.
    *   **Raw Flags:** Allow passing arbitrary launch flags directly to the underlying `llama.cpp` binary.
*   **Reasoning:** Linux and Termux users demand control. While LLAMdrop provides safe, sensible defaults to prevent crashes on budget hardware, it must never artificially lock out users who intentionally want to push their devices beyond safe limits.
