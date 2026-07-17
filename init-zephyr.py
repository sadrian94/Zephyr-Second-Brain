import os
import json
import shutil
import subprocess
import re
import sys

DEFAULT_VAULT_DIR = os.path.join(os.path.expanduser("~"), "Obsidian", "Zephyr")
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg):
    print(f"[Init] {msg}")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        log(f"Created directory: {path}")

def load_or_create_config(vault_dir):
    config_path = os.path.join(vault_dir, "System", "config.json")
    workspace_config_path = os.path.join(WORKSPACE_DIR, "config_local.json")

    # Default masked template
    default_config = {
        "user_name": "<USER_NAME>",
        "preferred_language": "English",
        "timezone": "US/Central",
        "primary_agent_name": "<PRIMARY_AGENT_NAME>",
        "secondary_agent_name": "<SECONDARY_AGENT_NAME>",
        "discord_webhook_url": "<DISCORD_WEBHOOK_URL>",
        "hermes_provider": "",
        "hermes_model": "",
        "ai_base_url": "https://api.openai.com/v1",
        "ai_api_key": "<AI_API_KEY>",
        "ai_model": "gpt-4o-mini"
    }

    # Try loading existing vault config
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                log("Found existing config in vault System/config.json. Loading it...")
                vault_cfg = json.load(f)
                # Merge with default to ensure all keys exist
                for k, v in default_config.items():
                    if k not in vault_cfg:
                        vault_cfg[k] = v
                return vault_cfg
        except Exception as e:
            log(f"Failed to read existing vault config: {e}")

    # Try loading workspace config_local.json
    if os.path.exists(workspace_config_path):
        try:
            with open(workspace_config_path, "r", encoding="utf-8") as f:
                log("Found config_local.json in workspace. Loading it...")
                local_cfg = json.load(f)
                for k, v in default_config.items():
                    if k not in local_cfg:
                        local_cfg[k] = v
                return local_cfg
        except Exception as e:
            log(f"Failed to read workspace local config: {e}")

    log("No existing config found. Initializing with masked placeholders...")
    return default_config

def apply_replacements(content, config):
    for k, v in config.items():
        placeholder = f"{{{{{k}}}}}"
        content = content.replace(placeholder, str(v))
    return content

def prompt_config_value(prompt_text, default_val):
    try:
        val = input(f"{prompt_text} [{default_val}]: ").strip()
        return val if val else default_val
    except Exception:
        return default_val

def prompt_config(current_cfg):
    # Check if stdin is interactive
    if not sys.stdin.isatty():
        log("Non-interactive terminal detected. Skipping prompts, using default/existing values.")
        return current_cfg

    print("\n--- Zephyr Second Brain Setup Wizard ---")
    print("Press Enter to keep the default/current value in brackets.\n")

    # Preserve unrecognized legacy settings while no longer prompting for them.
    new_cfg = current_cfg.copy()
    new_cfg["user_name"] = prompt_config_value("Enter your name", current_cfg.get("user_name", "<USER_NAME>"))
    new_cfg["preferred_language"] = prompt_config_value("Enter preferred communication language", current_cfg.get("preferred_language", "Traditional Chinese"))

    print("  [Hint] Timezone should be an IANA database name, e.g., 'Asia/Taipei' or 'America/New_York'")
    new_cfg["timezone"] = prompt_config_value("Enter your timezone", current_cfg.get("timezone", "US/Central"))

    new_cfg["primary_agent_name"] = prompt_config_value("Enter primary agent name", current_cfg.get("primary_agent_name", "<PRIMARY_AGENT_NAME>"))
    new_cfg["secondary_agent_name"] = prompt_config_value("Enter secondary agent name", current_cfg.get("secondary_agent_name", "<SECONDARY_AGENT_NAME>"))

    print("  [Hint] To get a Discord Webhook: Server Settings -> Integrations -> Webhooks -> New Webhook")
    new_cfg["discord_webhook_url"] = prompt_config_value("Enter Discord Webhook URL", current_cfg.get("discord_webhook_url", "<DISCORD_WEBHOOK_URL>"))

    print("\n--- Inbox Triage Configuration ---")
    print("Choose triage method:")
    print("  1. Hermes CLI (uses local hermes commands, zero-config API keys)")
    print("  2. Direct LLM API (uses standard API url, key, and model)")
    triage_choice = prompt_config_value("Select method (1 or 2)", "1")
    
    if triage_choice == "1":
        print("\nConfiguring Hermes CLI Triage:")
        new_cfg["hermes_provider"] = prompt_config_value("  Enter Hermes provider (e.g. openrouter, anthropic) [optional]", current_cfg.get("hermes_provider", ""))
        new_cfg["hermes_model"] = prompt_config_value("  Enter Hermes model (e.g. google/gemini-flash-1.5) [optional]", current_cfg.get("hermes_model", ""))
        new_cfg["ai_base_url"] = current_cfg.get("ai_base_url", "https://api.openai.com/v1")
        new_cfg["ai_api_key"] = current_cfg.get("ai_api_key", "<AI_API_KEY>")
        new_cfg["ai_model"] = current_cfg.get("ai_model", "gpt-4o-mini")
    else:
        print("\nConfiguring Direct LLM API:")
        new_cfg["ai_base_url"] = prompt_config_value("  Enter API Base URL", current_cfg.get("ai_base_url", "https://api.openai.com/v1"))
        new_cfg["ai_api_key"] = prompt_config_value("  Enter API Key", current_cfg.get("ai_api_key", "<AI_API_KEY>"))
        new_cfg["ai_model"] = prompt_config_value("  Enter AI Model", current_cfg.get("ai_model", "gpt-4o-mini"))
        new_cfg["hermes_provider"] = current_cfg.get("hermes_provider", "")
        new_cfg["hermes_model"] = current_cfg.get("hermes_model", "")

    print("\nConfiguration compiled successfully!\n")
    return new_cfg

def enable_obsidian_plugins(vault_dir):
    # Enable dataview in community-plugins.json safely
    com_plugins_path = os.path.join(vault_dir, ".obsidian", "community-plugins.json")
    try:
        plugins = []
        if os.path.exists(com_plugins_path):
            with open(com_plugins_path, "r", encoding="utf-8") as f:
                plugins = json.load(f)
        if not isinstance(plugins, list):
            plugins = []
        if "dataview" not in plugins:
            plugins.append("dataview")
        with open(com_plugins_path, "w", encoding="utf-8") as f:
            json.dump(plugins, f, indent=4)
        log("Enabled 'dataview' in community-plugins.json")
    except Exception as e:
        log(f"Failed to enable community plugin: {e}")

    # Enable snippet in appearance.json safely
    appearance_path = os.path.join(vault_dir, ".obsidian", "appearance.json")
    try:
        appearance_cfg = {}
        if os.path.exists(appearance_path):
            with open(appearance_path, "r", encoding="utf-8") as f:
                appearance_cfg = json.load(f)
        if not isinstance(appearance_cfg, dict):
            appearance_cfg = {}

        snippets = appearance_cfg.get("enabledCssSnippets", [])
        if not isinstance(snippets, list):
            snippets = []
        if "zephyr-dashboard" not in snippets:
            snippets.append("zephyr-dashboard")

        appearance_cfg["enabledCssSnippets"] = snippets
        if "cssTheme" not in appearance_cfg:
            appearance_cfg["cssTheme"] = ""
        if "theme" not in appearance_cfg:
            appearance_cfg["theme"] = "moonstone"

        with open(appearance_path, "w", encoding="utf-8") as f:
            json.dump(appearance_cfg, f, indent=4)
        log("Enabled 'zephyr-dashboard' snippet in appearance.json")
    except Exception as e:
        log(f"Failed to enable CSS snippet: {e}")

UPDATE_FILES = {
    "run-watcher.sh",
    "run-watcher.bat",
    "Home.md",
    "Capture/Capture.md",
    "Brain/Brain.md",
    "System/DESIGN.md",
    "System/rules.md",
    "System/zephyr-dashboard.css",
    "System/zephyr-watcher.py",
    "System/zephyr-worker.py",
}
UPDATE_DIRECTORIES = ("System/skills", "System/templates")
TEXT_FILE_EXTENSIONS = (".md", ".json", ".py", ".css", ".sh", ".bat", ".txt")


def copy_template_file(src_file, dest_file, config):
    ensure_dir(os.path.dirname(dest_file))
    if src_file.endswith(TEXT_FILE_EXTENSIONS):
        with open(src_file, "r", encoding="utf-8") as source_file:
            content = apply_replacements(source_file.read(), config)
        with open(dest_file, "w", encoding="utf-8") as destination_file:
            destination_file.write(content)
        shutil.copymode(src_file, dest_file)
    else:
        shutil.copy2(src_file, dest_file)


def update_vault(vault_dir):
    config_path = os.path.join(vault_dir, "System", "config.json")
    if not os.path.isfile(config_path):
        raise SystemExit("[Init] --update requires an initialized vault with System/config.json. Run init-zephyr.py first.")

    git_dir = os.path.join(WORKSPACE_DIR, ".git")
    if os.path.exists(git_dir):
        log("Checking for latest template updates from git remote...")
        try:
            rem_check = subprocess.run(["git", "-C", WORKSPACE_DIR, "remote"], capture_output=True, text=True, encoding="utf-8")
            if rem_check.returncode == 0 and rem_check.stdout.strip():
                pull_res = subprocess.run(["git", "-C", WORKSPACE_DIR, "pull"], capture_output=True, text=True, encoding="utf-8")
                if pull_res.returncode == 0:
                    log("Successfully pulled the latest updates from git remote.")
                else:
                    log(f"Warning: Could not automatically pull remote changes: {pull_res.stderr.strip()}")
                    log("Proceeding with the update using current local files...")
            else:
                log("No git remote configured in workspace. Updating from current local files...")
        except Exception as e:
            log(f"Warning: Failed to check for git updates: {e}")

    config = load_or_create_config(vault_dir)
    update_paths = set(UPDATE_FILES)
    for directory in UPDATE_DIRECTORIES:
        source_directory = os.path.join(WORKSPACE_DIR, directory)
        if not os.path.isdir(source_directory):
            continue
        for root, _, files in os.walk(source_directory):
            for filename in files:
                update_paths.add(os.path.relpath(os.path.join(root, filename), WORKSPACE_DIR))

    for relative_path in sorted(update_paths):
        source_file = os.path.join(WORKSPACE_DIR, relative_path)
        if not os.path.isfile(source_file):
            continue
        destination_file = os.path.join(vault_dir, relative_path)
        copy_template_file(source_file, destination_file, config)
        log(f"Updated system asset: {relative_path}")

    src_css = os.path.join(vault_dir, "System", "zephyr-dashboard.css")
    dest_css = os.path.join(vault_dir, ".obsidian", "snippets", "zephyr-dashboard.css")
    if os.path.exists(src_css):
        ensure_dir(os.path.dirname(dest_css))
        shutil.copy2(src_css, dest_css)
        log("Updated zephyr-dashboard.css snippet in Obsidian settings.")

    enable_obsidian_plugins(vault_dir)
    worker_path = os.path.join(vault_dir, "System", "zephyr-worker.py")
    if os.path.isfile(worker_path):
        result = subprocess.run([sys.executable, worker_path, "index"], check=False)
        if result.returncode != 0:
            raise SystemExit("[Init] --update copied assets but failed to rebuild System/index.json.")

    log("Zephyr system update complete. Personal notes and System/config.json were not overwritten.")


def main():
    here_mode = "--here" in sys.argv
    update_mode = "--update" in sys.argv
    if here_mode and update_mode:
        raise SystemExit("[Init] --here and --update cannot be used together.")

    vault_dir = WORKSPACE_DIR if here_mode else DEFAULT_VAULT_DIR
    if update_mode:
        update_vault(vault_dir)
        return

    log("Zephyr Second Brain (0.1.0) Initialization & Configuration Wizard")
    if here_mode:
        log(f"In-place mode (--here): vault dir = {vault_dir}")
    else:
        log(f"Install mode: vault dir = {vault_dir}")

    # Create basic directory structure
    ensure_dir(vault_dir)
    ensure_dir(os.path.join(vault_dir, "Capture"))
    ensure_dir(os.path.join(vault_dir, "Brain"))
    ensure_dir(os.path.join(vault_dir, "System"))
    ensure_dir(os.path.join(vault_dir, "System", "Archive"))
    ensure_dir(os.path.join(vault_dir, "System", "templates"))
    ensure_dir(os.path.join(vault_dir, "System", "skills"))
    ensure_dir(os.path.join(vault_dir, ".obsidian", "snippets"))

    # Load and prompt configuration
    initial_config = load_or_create_config(vault_dir)
    config = prompt_config(initial_config)

    # Save the config file in vault System/config.json
    config_path = os.path.join(vault_dir, "System", "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    log(f"Saved configuration to: {config_path}")

    if not here_mode:
        # Copy files from workspace root to target vault with token replacements
        for root, dirs, files in os.walk(WORKSPACE_DIR):
            # Modify dirs in-place to avoid walking into unwanted folders
            dirs[:] = [d for d in dirs if d not in [".git", ".agents", "__pycache__", "node_modules", "docs"]]

            for fname in files:
                src_file = os.path.join(root, fname)
                rel_path = os.path.relpath(src_file, WORKSPACE_DIR)

                # Skip setup scripts, secrets, and docs-only files
                if fname in [
                    "init-zephyr.py", "config_local.json", "skills-lock.json",
                    "config.example.json", "config.json",
                    "README.md", "README-ZH.md", "IDEA.md",
                    "LICENSE", "LICENSE.md", "LICENSE.txt"
                ]:
                    continue

                dest_file = os.path.join(vault_dir, rel_path)

                # Create parent folder if missing
                dest_dir = os.path.dirname(dest_file)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                # Process and write file
                try:
                    if fname.endswith((".md", ".json", ".py", ".css", ".sh", ".bat", ".txt")):
                        with open(src_file, "r", encoding="utf-8") as sf:
                            content = sf.read()
                        content = apply_replacements(content, config)
                        with open(dest_file, "w", encoding="utf-8") as df:
                            df.write(content)
                        log(f"Customized and copied: {rel_path} -> {dest_file}")
                    else:
                        # Binary or other files
                        shutil.copy2(src_file, dest_file)
                        log(f"Copied binary file: {rel_path}")
                except Exception as e:
                    log(f"Failed to process file {rel_path}: {e}")

        # Optional convenience: if another local vault already has Dataview installed,
        # copy it into the personal vault so dashboards work offline. This is not
        # vendored in the public template; Community Plugins install is the default.
        old_plugins_dir = os.path.join(os.path.expanduser("~"), "Obsidian", "My_Vault", ".obsidian", "plugins", "dataview")
        new_plugins_dir = os.path.join(vault_dir, ".obsidian", "plugins", "dataview")

        if os.path.exists(old_plugins_dir):
            ensure_dir(os.path.dirname(new_plugins_dir))
            if os.path.exists(new_plugins_dir):
                shutil.rmtree(new_plugins_dir)
            shutil.copytree(old_plugins_dir, new_plugins_dir)
            log("Optional: copied local Dataview plugin into the personal vault.")
        else:
            log("Dataview plugin binary not found locally. Install Dataview from Obsidian Community Plugins.")
    else:
        # In-place mode keeps the repo as a public template.
        # Never rewrite tracked AGENTS.md / GEMINI.md with personal config values —
        # that would leak names into git. Personal values live only in System/config.json.
        log("In-place mode: skipping full file copy and template personalization.")
        log("Personal values saved only to System/config.json (gitignored).")
        log("Tracked AGENTS.md / GEMINI.md remain as {{placeholder}} templates.")

    # Ensure design system lives under System/
    design_candidates = [
        os.path.join(WORKSPACE_DIR, "System", "DESIGN.md"),
        os.path.join(WORKSPACE_DIR, "DESIGN.md"),
    ]
    design_dest = os.path.join(vault_dir, "System", "DESIGN.md")
    design_copied = False
    for design_src in design_candidates:
        if os.path.exists(design_src) and os.path.abspath(design_src) != os.path.abspath(design_dest):
            ensure_dir(os.path.dirname(design_dest))
            shutil.copy2(design_src, design_dest)
            log("Copied DESIGN.md to System/DESIGN.md")
            design_copied = True
            break
    if not design_copied and os.path.exists(design_dest):
        log("System/DESIGN.md already present.")

    # Copy zephyr-dashboard.css to Obsidian snippets folder
    src_css = os.path.join(vault_dir, "System", "zephyr-dashboard.css")
    dest_css = os.path.join(vault_dir, ".obsidian", "snippets", "zephyr-dashboard.css")
    if os.path.exists(src_css):
        ensure_dir(os.path.dirname(dest_css))
        shutil.copy2(src_css, dest_css)
        log("Copied zephyr-dashboard.css snippet to Obsidian snippets directory.")

    enable_obsidian_plugins(vault_dir)

    # Generate initial index.json if not present
    index_path = os.path.join(vault_dir, "System", "index.json")
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("{}")
        log(f"Generated initial empty index: {index_path}")

    log("Zephyr Second Brain initialization complete!")
    log("Setup paths & folders verified.")
    log(f"Obsidian Vault: {vault_dir}")
    log("Next: enable DataviewJS, then run ./run-watcher.sh (or python3 System/zephyr-worker.py index)")

if __name__ == "__main__":
    main()
