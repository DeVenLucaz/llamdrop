"""
llamdrop - config.py
User configuration file support.

Config lives at ~/.llamdrop/config.json
Users can override any auto-detected setting.
llamdrop reads it at launch — auto-detection fills anything not set.

Example config.json:
{
  "threads": 4,
  "context_size": 2048,
  "batch_size": 256,
    "max_tokens": 512,
  "temperature": 0.7,
  "system_prompt": "You are a helpful assistant. Be concise.",
  "auto_save_sessions": true,
  "warn_battery_below": 15
}
"""

import os
import json


LLAMDROP_DIR = os.path.expanduser("~/.llamdrop")
CONFIG_FILE  = os.path.join(LLAMDROP_DIR, "config.json")

# All valid config keys with their types and defaults
CONFIG_SCHEMA = {
    "threads":            {"type": int,   "default": None,  "min": 1,   "max": 32},
    "context_size":       {"type": int,   "default": None,  "min": 128, "max": 8192},
    "batch_size":         {"type": int,   "default": None,  "min": 32,  "max": 2048},
    "max_tokens":         {"type": int,   "default": 512,   "min": 50,  "max": 2048},
    "temperature":        {"type": float, "default": 0.7,   "min": 0.0, "max": 2.0},
    "system_prompt":      {"type": str,   "default": None},
    "auto_save_sessions": {"type": bool,  "default": True},
    "warn_battery_below": {"type": int,   "default": 15,    "min": 0,   "max": 100},
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Be concise and clear. If you don't know something, say so."
)

_config_cache = None
_config_mtime = None   # Bug #8 fix: track file mtime to detect external edits


def load_config(force=False):
    """
    Load config from ~/.llamdrop/config.json.
    Returns a dict with all keys — missing keys use defaults.

    Caches after first load.  Cache is automatically invalidated when:
    - force=True is passed (e.g. after save_config())
    - the file's mtime has changed since last load (external editor support)
    """
    global _config_cache, _config_mtime

    # Check if the file has been modified since we last read it
    current_mtime = None
    if os.path.exists(CONFIG_FILE):
        try:
            current_mtime = os.path.getmtime(CONFIG_FILE)
        except Exception:
            pass

    if _config_cache is not None and not force:
        if current_mtime == _config_mtime:
            return _config_cache
        # mtime changed — file was edited externally, fall through to reload

    user_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                user_config = json.load(f)
        except Exception:
            user_config = {}

    config = {}
    for key, schema in CONFIG_SCHEMA.items():
        val = user_config.get(key)
        if val is None:
            config[key] = schema["default"]
            continue

        # Type coerce
        try:
            val = schema["type"](val)
        except (ValueError, TypeError):
            config[key] = schema["default"]
            continue

        # Range check for numeric types
        if "min" in schema and val < schema["min"]:
            val = schema["min"]
        if "max" in schema and val > schema["max"]:
            val = schema["max"]

        config[key] = val

    _config_cache = config
    _config_mtime = current_mtime
    return config


def get(key, fallback=None):
    """Get a single config value."""
    return load_config().get(key, fallback)


def save_config(updates):
    """
    Save updated config values to config.json.
    Merges with existing config — only updates specified keys.
    """
    global _config_cache, _config_mtime

    existing = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    existing.update(updates)

    os.makedirs(LLAMDROP_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    _config_cache = None  # invalidate cache
    _config_mtime = None


def create_default_config():
    """
    Write a default config.json on first install.
    Only writes actual settable keys — no pseudo-comment keys that pollute
    the schema and confuse load_config().
    Called on first install or when user asks to reset config.
    """
    os.makedirs(LLAMDROP_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default = {
            "max_tokens":         512,
            "temperature":        0.7,
            "auto_save_sessions": True,
            "warn_battery_below": 15,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=2)
        # Write a separate human-readable README alongside the config
        readme = CONFIG_FILE.replace(".json", "_README.txt")
        try:
            with open(readme, "w") as f:
                f.write(
                    "llamdrop config.json — edit this file to override auto-detected settings.\n"
                    "Delete any key to let llamdrop auto-detect it again.\n\n"
                    "Available keys:\n"
                    "  threads            — CPU thread count (int, 1–32)\n"
                    "  context_size       — context window in tokens (int, 128–8192)\n"
                    "  batch_size         — batch size (int, 32–2048)\n"
                    "  max_tokens         — max tokens per response (int, 50–2048)\n"
                    "  temperature        — sampling temperature (float, 0.0–2.0)\n"
                    "  system_prompt      — custom system prompt (string)\n"
                    "  auto_save_sessions — auto-save conversations (bool)\n"
                    "  warn_battery_below — warn if battery % below this (int, 0–100)\n"
                )
        except Exception:
            pass


def apply_to_device_profile(device_profile):
    """
    Override device_profile values with user config where set.
    Supports both DeviceProfile dataclass (specs.py) and legacy dict.
    device_profile is modified in place (dict) or via setattr (dataclass).
    """
    config = load_config()

    if hasattr(device_profile, "threads"):
        # New-style DeviceProfile dataclass
        if config.get("threads") is not None:
            device_profile.threads    = config["threads"]
        if config.get("context_size") is not None:
            device_profile.ctx_size   = config["context_size"]
        if config.get("batch_size") is not None:
            device_profile.batch_size = config["batch_size"]
    else:
        # Legacy dict profile
        if config.get("threads") is not None:
            device_profile["optimal_threads"] = config["threads"]
        if config.get("context_size") is not None:
            device_profile["safe_context"] = config["context_size"]
        if config.get("batch_size") is not None:
            device_profile["safe_batch"] = config["batch_size"]

    return device_profile


def get_system_prompt():
    """Return user's custom system prompt or the default."""
    custom = get("system_prompt")
    return custom if custom else DEFAULT_SYSTEM_PROMPT


def get_max_tokens():
    return get("max_tokens", 512)


def get_temperature():
    return get("temperature", 0.7)


def show_config():
    """
    Interactive config viewer and editor.
    Shows all current values with source (user-set vs auto), then offers
    an edit menu so users never need to touch the JSON file manually.
    """
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
    RED    = "\033[31m"

    # Human-readable descriptions for each key
    DESCRIPTIONS = {
        "threads":            "CPU threads to use during inference (1–32)",
        "context_size":       "Context window size in tokens (128–8192)",
        "batch_size":         "Batch size for prompt processing (32–2048)",
        "max_tokens":         "Max tokens per model response (50–2048)",
        "temperature":        "Sampling temperature — 0.0=focused, 2.0=creative (0.0–2.0)",
        "system_prompt":      "Custom system prompt (overrides default)",
        "auto_save_sessions": "Auto-save conversations (true/false)",
        "warn_battery_below": "Warn before chat if battery is below this % (0–100)",
    }

    while True:
        os.system("clear")

        config = load_config()
        user_config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    user_config = json.load(f)
            except Exception:
                pass

        print(f"\n  {BOLD}llamdrop — Settings{RESET}  ({CONFIG_FILE})\n")

        keys = [k for k in CONFIG_SCHEMA.keys() if not k.startswith("_")]
        for idx, key in enumerate(keys, 1):
            val     = config.get(key)
            is_set  = key in user_config
            source  = f"{GREEN}(saved){RESET}" if is_set else f"{YELLOW}(auto) {RESET}"
            display = str(val) if val is not None else "auto-detected"
            # Truncate long system prompts for display
            if key == "system_prompt" and val and len(str(val)) > 40:
                display = str(val)[:40] + "..."
            print(f"  {CYAN}{idx}.{RESET} {key:<22} {display:<44} {source}")

        print(f"\n  {BOLD}[E]{RESET} Edit a setting   "
              f"{BOLD}[R]{RESET} Reset all to defaults   "
              f"{BOLD}[B]{RESET} Back\n")

        try:
            choice = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if choice in ("b", "back", ""):
            return

        elif choice == "r":
            try:
                confirm = input(f"\n  Reset ALL settings to defaults? (y/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                continue
            if confirm == "y":
                try:
                    if os.path.exists(CONFIG_FILE):
                        os.remove(CONFIG_FILE)
                    _config_cache.__class__  # just touch it
                except Exception:
                    pass
                # Force cache invalidation
                global _config_cache, _config_mtime
                _config_cache = None
                _config_mtime = None
                create_default_config()
                print(f"  {GREEN}✓ Config reset to defaults.{RESET}")
                import time as _time; _time.sleep(1)

        elif choice == "e":
            try:
                raw = input(f"\n  Enter setting number to edit (1–{len(keys)}): ").strip()
                idx = int(raw) - 1
                if not (0 <= idx < len(keys)):
                    raise ValueError
            except (ValueError, EOFError, KeyboardInterrupt):
                print(f"  {RED}Invalid selection.{RESET}")
                import time as _time; _time.sleep(0.8)
                continue

            key    = keys[idx]
            schema = CONFIG_SCHEMA[key]
            config = load_config()
            current = config.get(key)
            desc    = DESCRIPTIONS.get(key, "")

            print(f"\n  {BOLD}{key}{RESET}")
            print(f"  {desc}")
            print(f"  Current value : {current if current is not None else 'auto-detected'}")
            if "min" in schema and "max" in schema:
                print(f"  Range         : {schema['min']} – {schema['max']}")
            if schema["type"] == bool:
                print(f"  Values        : true / false")
            print(f"  (Press Enter to keep current, type 'auto' to remove override)\n")

            # Multi-line support for system_prompt
            if key == "system_prompt":
                print(f"  Current prompt:")
                if current:
                    for line in str(current).splitlines():
                        print(f"    {line}")
                print(f"\n  Enter new prompt (single line, or press Enter to keep):")
                try:
                    new_val_raw = input("  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    continue
            else:
                try:
                    new_val_raw = input(f"  New value: ").strip()
                except (EOFError, KeyboardInterrupt):
                    continue

            if new_val_raw == "":
                # Keep current — do nothing
                continue

            if new_val_raw.lower() == "auto":
                # Remove the key from saved config so auto-detection takes over
                if os.path.exists(CONFIG_FILE):
                    try:
                        with open(CONFIG_FILE) as f:
                            existing = json.load(f)
                        existing.pop(key, None)
                        with open(CONFIG_FILE, "w") as f:
                            json.dump(existing, f, indent=2)
                        global _config_cache, _config_mtime
                        _config_cache = None
                        _config_mtime = None
                        print(f"  {GREEN}✓ '{key}' removed — will be auto-detected.{RESET}")
                    except Exception as e:
                        print(f"  {RED}✗ Could not update config: {e}{RESET}")
                import time as _time; _time.sleep(1)
                continue

            # Type coerce and validate
            try:
                if schema["type"] == bool:
                    if new_val_raw.lower() in ("true", "yes", "1"):
                        new_val = True
                    elif new_val_raw.lower() in ("false", "no", "0"):
                        new_val = False
                    else:
                        raise ValueError(f"Expected true or false")
                else:
                    new_val = schema["type"](new_val_raw)
            except (ValueError, TypeError) as e:
                print(f"  {RED}✗ Invalid value: {e}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue

            # Range check
            if "min" in schema and new_val < schema["min"]:
                print(f"  {RED}✗ Too low — minimum is {schema['min']}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue
            if "max" in schema and new_val > schema["max"]:
                print(f"  {RED}✗ Too high — maximum is {schema['max']}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue

            save_config({key: new_val})
            print(f"  {GREEN}✓ Saved: {key} = {new_val}{RESET}")
            import time as _time; _time.sleep(0.8)

        else:
            # Maybe they typed a number directly
            try:
                idx = int(choice) - 1
                if not (0 <= idx < len(keys)):
                    raise ValueError
            except ValueError:
                continue

            key    = keys[idx]
            schema = CONFIG_SCHEMA[key]
            config = load_config()
            current = config.get(key)
            desc    = DESCRIPTIONS.get(key, "")

            print(f"\n  {BOLD}{key}{RESET}")
            print(f"  {desc}")
            print(f"  Current value : {current if current is not None else 'auto-detected'}")
            if "min" in schema and "max" in schema:
                print(f"  Range         : {schema['min']} – {schema['max']}")
            if schema["type"] == bool:
                print(f"  Values        : true / false")
            print(f"  (Press Enter to keep current, type 'auto' to remove override)\n")

            if key == "system_prompt":
                if current:
                    print(f"  Current prompt:")
                    for line in str(current).splitlines():
                        print(f"    {line}")
                print(f"\n  Enter new prompt (press Enter to keep):")
                try:
                    new_val_raw = input("  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    continue
            else:
                try:
                    new_val_raw = input(f"  New value: ").strip()
                except (EOFError, KeyboardInterrupt):
                    continue

            if new_val_raw == "":
                continue

            if new_val_raw.lower() == "auto":
                if os.path.exists(CONFIG_FILE):
                    try:
                        with open(CONFIG_FILE) as f:
                            existing = json.load(f)
                        existing.pop(key, None)
                        with open(CONFIG_FILE, "w") as f:
                            json.dump(existing, f, indent=2)
                        global _config_cache, _config_mtime
                        _config_cache = None
                        _config_mtime = None
                        print(f"  {GREEN}✓ '{key}' removed — will be auto-detected.{RESET}")
                    except Exception as e:
                        print(f"  {RED}✗ Could not update config: {e}{RESET}")
                import time as _time; _time.sleep(1)
                continue

            try:
                if schema["type"] == bool:
                    if new_val_raw.lower() in ("true", "yes", "1"):
                        new_val = True
                    elif new_val_raw.lower() in ("false", "no", "0"):
                        new_val = False
                    else:
                        raise ValueError("Expected true or false")
                else:
                    new_val = schema["type"](new_val_raw)
            except (ValueError, TypeError) as e:
                print(f"  {RED}✗ Invalid value: {e}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue

            if "min" in schema and new_val < schema["min"]:
                print(f"  {RED}✗ Too low — minimum is {schema['min']}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue
            if "max" in schema and new_val > schema["max"]:
                print(f"  {RED}✗ Too high — maximum is {schema['max']}{RESET}")
                import time as _time; _time.sleep(1.2)
                continue

            save_config({key: new_val})
            print(f"  {GREEN}✓ Saved: {key} = {new_val}{RESET}")
            import time as _time; _time.sleep(0.8)
