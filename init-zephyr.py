import os
import json
import shutil
import re
import sys

VAULT_DIR = os.path.join(os.path.expanduser("~"), "Obsidian", "Zephyr")
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg):
    print(f"[Init] {msg}")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        log(f"Created directory: {path}")

def load_or_create_config():
    config_path = os.path.join(VAULT_DIR, "System", "config.json")
    workspace_config_path = os.path.join(WORKSPACE_DIR, "config_local.json")
    
    # Default masked template
    default_config = {
        "user_name": "<USER_NAME>",
        "preferred_language": "English",
        "timezone": "US/Central",
        "primary_agent_name": "<PRIMARY_AGENT_NAME>",
        "secondary_agent_name": "<SECONDARY_AGENT_NAME>",
        "discord_webhook_url": "<DISCORD_WEBHOOK_URL>",
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
    
    new_cfg = {}
    new_cfg["user_name"] = prompt_config_value("Enter your name", current_cfg.get("user_name", "<USER_NAME>"))
    new_cfg["preferred_language"] = prompt_config_value("Enter preferred communication language", current_cfg.get("preferred_language", "Traditional Chinese"))
    
    print("  [Hint] Timezone should be an IANA database name, e.g., 'Asia/Taipei' or 'America/New_York'")
    new_cfg["timezone"] = prompt_config_value("Enter your timezone", current_cfg.get("timezone", "US/Central"))
    
    new_cfg["primary_agent_name"] = prompt_config_value("Enter primary agent name", current_cfg.get("primary_agent_name", "<PRIMARY_AGENT_NAME>"))
    new_cfg["secondary_agent_name"] = prompt_config_value("Enter secondary agent name", current_cfg.get("secondary_agent_name", "<SECONDARY_AGENT_NAME>"))
    
    print("  [Hint] To get a Discord Webhook: Server Settings -> Integrations -> Webhooks -> New Webhook")
    new_cfg["discord_webhook_url"] = prompt_config_value("Enter Discord Webhook URL", current_cfg.get("discord_webhook_url", "<DISCORD_WEBHOOK_URL>"))
    new_cfg["ai_base_url"] = prompt_config_value("Enter LLM API Base URL", current_cfg.get("ai_base_url", "https://api.openai.com/v1"))
    new_cfg["ai_api_key"] = prompt_config_value("Enter LLM API Key", current_cfg.get("ai_api_key", "<AI_API_KEY>"))
    new_cfg["ai_model"] = prompt_config_value("Enter LLM Model Name", current_cfg.get("ai_model", "gpt-4o-mini"))
    
    print("\nConfiguration compiled successfully!\n")
    return new_cfg

def main():
    log("Zephyr Second Brain (0.1.0) Initialization & Configuration Wizard")
    
    # Create basic directory structure
    ensure_dir(VAULT_DIR)
    ensure_dir(os.path.join(VAULT_DIR, "Capture"))
    ensure_dir(os.path.join(VAULT_DIR, "Brain"))
    ensure_dir(os.path.join(VAULT_DIR, "System"))
    ensure_dir(os.path.join(VAULT_DIR, "System", "Archive"))
    ensure_dir(os.path.join(VAULT_DIR, "System", "templates"))
    ensure_dir(os.path.join(VAULT_DIR, "System", "skills"))
    ensure_dir(os.path.join(VAULT_DIR, ".obsidian", "snippets"))

    # Load and prompt configuration
    initial_config = load_or_create_config()
    config = prompt_config(initial_config)
    
    # Save the config file in vault System/config.json
    config_path = os.path.join(VAULT_DIR, "System", "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    log(f"Saved configuration to: {config_path}")

    # Copy files from workspace root to target vault with token replacements
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Modify dirs in-place to avoid walking into unwanted folders
        dirs[:] = [d for d in dirs if d not in [".git", ".agents", "__pycache__", "node_modules", "docs"]]
            
        for fname in files:
            src_file = os.path.join(root, fname)
            rel_path = os.path.relpath(src_file, WORKSPACE_DIR)
            
            # Skip configuration templates, setup scripts, and git locks
            if fname in ["init-zephyr.py", "config_local.json", "skills-lock.json", "config.json.example", "config.json",
                         "README.md", "README-ZH.md", "DESIGN.md"]:
                continue
                
            dest_file = os.path.join(VAULT_DIR, rel_path)
                
            # Create parent folder if missing
            dest_dir = os.path.dirname(dest_file)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            # Process and write file
            try:
                if fname.endswith((".md", ".json", ".py", ".css")):
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
                
    # Copy Dataview plugin from My_Vault to Zephyr for auto-activation
    old_plugins_dir = os.path.join(os.path.expanduser("~"), "Obsidian", "My_Vault", ".obsidian", "plugins", "dataview")
    new_plugins_dir = os.path.join(VAULT_DIR, ".obsidian", "plugins", "dataview")
    
    if os.path.exists(old_plugins_dir):
        ensure_dir(os.path.dirname(new_plugins_dir))
        if os.path.exists(new_plugins_dir):
            shutil.rmtree(new_plugins_dir)
        shutil.copytree(old_plugins_dir, new_plugins_dir)
        log("Auto-copied Dataview plugin from My_Vault to Zephyr.")
        
    # Copy zephyr-dashboard.css to Obsidian snippets folder
    src_css = os.path.join(VAULT_DIR, "System", "zephyr-dashboard.css")
    dest_css = os.path.join(VAULT_DIR, ".obsidian", "snippets", "zephyr-dashboard.css")
    if os.path.exists(src_css):
        ensure_dir(os.path.dirname(dest_css))
        shutil.copy2(src_css, dest_css)
        log("Copied zephyr-dashboard.css snippet to Obsidian snippets directory.")
        
    # Copy DESIGN.md to System/ for agent design compliance
    design_src = os.path.join(WORKSPACE_DIR, "DESIGN.md")
    design_dest = os.path.join(VAULT_DIR, "System", "DESIGN.md")
    if os.path.exists(design_src):
        ensure_dir(os.path.dirname(design_dest))
        shutil.copy2(design_src, design_dest)
        log("Copied DESIGN.md to System/DESIGN.md")
        
    # Enable dataview in community-plugins.json safely
    com_plugins_path = os.path.join(VAULT_DIR, ".obsidian", "community-plugins.json")
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
    appearance_path = os.path.join(VAULT_DIR, ".obsidian", "appearance.json")
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
            
    # Generate initial index.json if not present
    index_path = os.path.join(VAULT_DIR, "System", "index.json")
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("{}")
        log(f"Generated initial empty index: {index_path}")
        
    log("Zephyr Second Brain initialization complete!")
    log("Setup paths & folders verified.")
    log(f"Obsidian Vault: {VAULT_DIR}")

if __name__ == "__main__":
    main()
