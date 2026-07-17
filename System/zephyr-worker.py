import os
import json
import re
import subprocess
from datetime import datetime

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(VAULT_DIR, "Capture")
BRAIN_DIR = os.path.join(VAULT_DIR, "Brain")
SYSTEM_DIR = os.path.join(VAULT_DIR, "System")
INDEX_PATH = os.path.join(SYSTEM_DIR, "index.json")

def load_index():
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(index):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end]
    body = content[end+3:].strip()

    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
            fm[k] = v
    return fm, body

def find_eligible_inbox_notes():
    """Return unclassified Capture notes suitable for Hermes inbox triage."""
    eligible = []
    if not os.path.exists(CAPTURE_DIR):
        return eligible

    for fname in sorted(os.listdir(CAPTURE_DIR)):
        if (
            not fname.endswith(".md")
            or fname == "Home.md"
            or fname.endswith(" -- draft.md")
        ):
            continue

        fpath = os.path.join(CAPTURE_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read {fname}: {e}")
            continue

        fm, _ = parse_frontmatter(content)
        if fm.get("type") or fm.get("triage_status") == "needs_review":
            continue
        eligible.append(fpath)

    return eligible

def scan_unprocessed_ideas():
    unprocessed = []
    if not os.path.exists(CAPTURE_DIR):
        return unprocessed
    for fname in os.listdir(CAPTURE_DIR):
        if not fname.endswith(".md") or fname == "Home.md":
            continue
        fpath = os.path.join(CAPTURE_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        fm, body = parse_frontmatter(content)
        if fm.get("type") != "log":
            continue

        rel_path = fpath.replace(VAULT_DIR, "").replace("\\", "/").lstrip("/")
        lines = content.splitlines()
        in_capture_section = False
        for idx, line in enumerate(lines):
            # Track ## Capture section boundary
            if re.match(r'^##\s+Capture', line):
                in_capture_section = True
                continue
            elif re.match(r'^##\s+', line):
                in_capture_section = False
                continue
            if not in_capture_section:
                continue
            # Match: idea lines (lightbulb or "idea:" prefix)
            match = re.search(r'^\s*-\s*(?:idea:)\s*(.+)$', line)
            if match:
                idea_text = match.group(1).strip()
                if idea_text and ("[[" not in idea_text or "]]" not in idea_text):
                    unprocessed.append({
                        "source_log": rel_path,
                        "line_number": idx + 1,
                        "text": idea_text
                    })
    return unprocessed

def _clean_body_for_summary(body):
    """Strip code/HTML/headings and return a compact plain-text summary source."""
    # Remove fenced code blocks first (preserves surrounding prose)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    # Remove HTML tags
    body = re.sub(r'<[^>]+>', '', body)
    # Work line-by-line so heading stripping cannot wipe the whole note
    kept = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        if s.startswith('```'):
            continue
        # Drop pure list markers / task checkboxes that carry no text
        if re.match(r'^[-*+]\s*\[[ xX]?\]\s*$', s):
            continue
        # Strip leading list markers but keep content
        s = re.sub(r'^[-*+]\s+(?:\[[ xX]\]\s*)?', '', s)
        s = re.sub(r'`[^`]+`', '', s)
        s = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', s)
        s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
        s = s.strip()
        if s:
            kept.append(s)
    return ' '.join(kept).strip()

def _summary_from_body(fm, body):
    """Build a readable index summary; prefer Focus for daily logs."""
    if fm.get("type") == "log":
        focus_match = re.search(r'(?m)^##\s+Focus\s*\n-\s*(.+)$', body)
        if focus_match:
            text = focus_match.group(1).strip()
            if text:
                return text[:150] + ("..." if len(text) > 150 else "")
        idea_match = re.search(r'(?m)^-\s*(?:idea:)\s*(.+)$', body)
        if idea_match:
            text = idea_match.group(1).strip()
            if text:
                return text[:150] + ("..." if len(text) > 150 else "")

    clean_body = _clean_body_for_summary(body)
    if not clean_body:
        # Last resort: first non-empty non-heading line from raw body
        for line in body.splitlines():
            s = line.strip()
            if s and not s.startswith('#') and not s.startswith('```') and not s.startswith('---'):
                clean_body = s
                break
    if not clean_body:
        return ""
    return clean_body[:150] + ("..." if len(clean_body) > 150 else "")

def compile_index():
    print("Compiling index.json...")
    old_index_data = load_index()
    old_notes = old_index_data.get("notes", {})
    new_notes = {}

    def scan_dir(dpath):
        if not os.path.exists(dpath):
            return
        for fname in os.listdir(dpath):
            if not fname.endswith(".md") or fname == "Home.md":
                continue
            fpath = os.path.join(dpath, fname)
            try:
                mtime = os.path.getmtime(fpath)
            except Exception:
                continue

            stem = fname.replace(".md", "")
            rel_path = fpath.replace(VAULT_DIR, "").replace("\\", "/").lstrip("/")

            # Check if cache is valid (stem exists, path matches, mtime matches)
            if (stem in old_notes
                and old_notes[stem].get("path") == rel_path
                and old_notes[stem].get("mtime") == mtime):
                new_notes[stem] = old_notes[stem]
                continue

            print(f"  [Cache Miss] Parsing: {fname}")
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            fm, body = parse_frontmatter(content)
            summary = _summary_from_body(fm, body)

            links = re.findall(r'\[\[(.*?)(?:\|(.*?))?\]\]', body)
            resolved_links = []
            for target, display in links:
                resolved_links.append(target.strip())

            new_notes[stem] = {
                "title": stem,
                "path": rel_path,
                "type": fm.get("type", "note"),
                "tags": fm.get("tags", []),
                "summary": summary,
                "links": resolved_links,
                "deadline": fm.get("deadline", ""),
                "status": fm.get("status", ""),
                "priority": fm.get("priority", ""),
                "date": fm.get("date", ""),
                "mtime": mtime
            }

    scan_dir(CAPTURE_DIR)
    scan_dir(BRAIN_DIR)

    unprocessed_ideas = scan_unprocessed_ideas()

    index_data = {
        "notes": new_notes,
        "unprocessed_ideas": unprocessed_ideas
    }
    save_index(index_data)
    print(f"Compiled {len(new_notes)} notes and {len(unprocessed_ideas)} unprocessed ideas into index.json")

def heal_links():
    print("Healing broken links...")
    index_data = load_index()
    notes = index_data.get("notes", {})
    valid_stems_lower = {k.lower(): k for k in notes.keys()}

    def heal_dir(dpath):
        if not os.path.exists(dpath):
            return
        for fname in os.listdir(dpath):
            if not fname.endswith(".md") or fname == "Home.md":
                continue
            fpath = os.path.join(dpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            modified = False

            def replacer(match):
                nonlocal modified
                orig_target = match.group(1)
                display = match.group(2) if match.group(2) else ""

                clean_target = orig_target.replace(".md", "").strip()
                target_lower = clean_target.lower()

                if target_lower in valid_stems_lower:
                    canonical = valid_stems_lower[target_lower]
                    if canonical != orig_target:
                        modified = True
                        suffix = f"|{display}" if display else ""
                        return f"[[{canonical}{suffix}]]"
                return match.group(0)

            new_content = re.sub(r'\[\[(.*?)(?:\|(.*?))?\]\]', replacer, content)
            if modified:
                try:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Healed links in: {fname}")
                except Exception as e:
                    print(f"Failed to save healed file {fname}: {e}")

    heal_dir(CAPTURE_DIR)
    heal_dir(BRAIN_DIR)

def run_git_cmd(args):
    full_args = ["git", "-C", VAULT_DIR] + args
    res = subprocess.run(full_args, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def sync_git():
    git_dir = os.path.join(VAULT_DIR, ".git")
    if not os.path.exists(git_dir):
        print("Not a git repository. Skipping git sync.")
        return

    # Check if remote is configured
    ret_rem, rem_out, _ = run_git_cmd(["remote"])
    has_remote = (ret_rem == 0 and bool(rem_out))

    # Check git status
    ret_stat, stat_out, _ = run_git_cmd(["status", "--porcelain"])
    if ret_stat != 0:
        print("Failed to check Git status.")
        return

    if stat_out:
        print("Detected local changes. Auto-committing...")
        run_git_cmd(["add", "."])
        commit_msg = f"zephyr-sync: auto-commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ret_cmt, _, cmt_err = run_git_cmd(["commit", "-m", commit_msg])
        if ret_cmt == 0:
            print("Auto-committed changes.")
        else:
            print(f"Failed to commit changes: {cmt_err}")
            return
    else:
        print("No local changes to commit.")

    if has_remote:
        print("Git remote detected. Pulling remote changes with rebase...")
        ret_pull, pull_out, pull_err = run_git_cmd(["pull", "--rebase"])
        if ret_pull != 0:
            print("\n" + "="*60)
            print("[WARNING: GIT CONFLICT / ERROR DETECTED DURING SYNC]")
            print(f"Error details:\n{pull_err or pull_out}")
            print("Aborting rebase to revert to safety...")
            run_git_cmd(["rebase", "--abort"])
            print("Successfully aborted rebase. Local commits remain intact.")
            print("Please resolve the git conflict manually.")
            print("="*60 + "\n")
            return

        print("Successfully pulled and rebased remote changes.")

        print("Pushing commits to remote...")
        ret_push, _, push_err = run_git_cmd(["push"])
        if ret_push == 0:
            print("Successfully pushed changes to remote.")
        else:
            print(f"Failed to push changes: {push_err}")
    else:
        print("No Git remote configured. Skipping remote sync.")

def load_config():
    config_paths = [
        os.path.join(VAULT_DIR, "config_local.json"),
        os.path.join(SYSTEM_DIR, "config.json")
    ]
    config = {}
    for p in config_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    config.update(json.load(f))
            except Exception as e:
                print(f"Failed to load config from {p}: {e}")
    return config

def write_frontmatter_and_move(fpath, new_fm_data, content, note_type, title):
    existing_fm, body = parse_frontmatter(content)
    merged_fm = existing_fm.copy()
    merged_fm.update(new_fm_data)
    
    # If note is successfully classified, remove triage_status
    if note_type and "triage_status" in merged_fm:
        del merged_fm["triage_status"]
    
    # Generate new frontmatter text
    fm_lines = ["---"]
    for k, v in merged_fm.items():
        if isinstance(v, list):
            list_str = ", ".join(f'"{x}"' for x in v)
            fm_lines.append(f"{k}: [{list_str}]")
        else:
            fm_lines.append(f"{k}: {v}")
    fm_lines.append("---")
    
    new_content = "\n".join(fm_lines) + "\n\n" + body
    
    orig_name = os.path.basename(fpath)
    if not note_type or not title:
        # Keep in Capture, just update frontmatter
        dest_path = fpath
    else:
        # Determine directory
        if note_type == "log":
            dest_dir = CAPTURE_DIR
        else:
            dest_dir = BRAIN_DIR
            
        # Avoid filename collisions
        dest_filename = f"{title}.md"
        dest_path = os.path.join(dest_dir, dest_filename)
        
        # Check collision
        if os.path.exists(dest_path) and dest_path.lower() != fpath.lower():
            counter = 1
            while True:
                dest_filename = f"{title}-{counter}.md"
                dest_path = os.path.join(dest_dir, dest_filename)
                if not os.path.exists(dest_path):
                    break
                counter += 1
    
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        if dest_path.lower() != fpath.lower():
            os.remove(fpath)
            print(f"    Moved and renamed: {orig_name} -> {os.path.basename(dest_path)}")
        else:
            print(f"    Updated: {orig_name}")
        return True
    except Exception as e:
        print(f"    Error writing/moving file: {e}")
        return False

def try_triage_via_hermes():
    import shutil
    print("Attempting triage via Hermes CLI...")
    hermes_cmd = shutil.which("hermes")
    if not hermes_cmd:
        print("  Hermes CLI not found on PATH.")
        return False

    prompt = (
        "First read AGENTS.md and System/skills/inbox-triage.md. "
        "Follow that protocol exactly to process eligible unclassified Capture/ notes. "
        "Then run 'python3 System/zephyr-worker.py index'."
    )

    config = load_config()
    hermes_provider = config.get("hermes_provider")
    hermes_model = config.get("hermes_model")

    cmd = [hermes_cmd]
    if hermes_provider:
        cmd.extend(["--provider", hermes_provider])
    if hermes_model:
        cmd.extend(["--model", hermes_model])
    cmd.extend(["-z", prompt])
    cmd_str_list = [os.path.basename(cmd[0])] + cmd[1:-1] + [f'"{cmd[-1][:30]}..."']
    print(f"  Running: {' '.join(cmd_str_list)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=VAULT_DIR
        )
        if result.returncode == 0:
            print("Hermes CLI triage succeeded:")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"  Hermes CLI exited with code {result.returncode}.")
            if result.stderr:
                print(f"  Hermes Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Failed to run Hermes CLI: {e}")
        return False

def try_triage_via_local_api(eligible_notes):
    import urllib.request
    import urllib.error

    config = load_config()
    api_key = config.get("ai_api_key")
    base_url = config.get("ai_base_url")
    model = config.get("ai_model", "gpt-4o-mini")

    if not api_key or api_key == "<AI_API_KEY>":
        print("  Local AI API key not configured or is placeholder.")
        return False

    if not base_url:
        base_url = "https://api.openai.com/v1"

    print(f"Attempting local API triage using model: {model}...")

    success_count = 0
    review_count = 0

    for fpath in eligible_notes:
        fname = os.path.basename(fpath)
        print(f"  Processing {fname}...")
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                note_content = f.read()
        except Exception as e:
            print(f"    Failed to read note file: {e}")
            continue

        system_prompt = (
            "You are a Zephyr vault inbox triage assistant. Classify the user's raw note.\n\n"
            "Rules:\n"
            "1. Output valid JSON only, inside a Markdown code block with 'json' identifier.\n"
            "2. Determine the 'type' of the note: 'log', 'note', or 'project'.\n"
            "   - 'log': Daily logs, checklists, meeting minutes.\n"
            "   - 'project': Active/paused projects with deadlines/priority.\n"
            "   - 'note': Evergreen notes, resources, areas.\n"
            "3. Generate 2 to 4 lowercase, hyphenated topic tags (e.g. ['productivity', 'python-dev']).\n"
            "4. Propose a unique, Windows-safe filename/title (e.g. 'python-subprocess-guide'). Do not include file extension.\n"
            "5. If you cannot confidently classify it or name it, set 'triage_status' to 'needs_review'.\n\n"
            "Response format must be exactly:\n"
            "```json\n"
            "{\n"
            "  \"type\": \"log|note|project\",\n"
            "  \"tags\": [\"tag1\", \"tag2\"],\n"
            "  \"title\": \"unique-windows-safe-title\",\n"
            "  \"triage_status\": \"ok|needs_review\"\n"
            "}\n"
            "```"
        )

        user_content = f"Note Filename: {fname}\n\nNote Content:\n{note_content}"

        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                reply = resp_data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"    API Request failed: {e}")
            return False

        match = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
        if not match:
            match_json = re.search(r'\{.*\}', reply, re.DOTALL)
            if match_json:
                json_str = match_json.group(0)
            else:
                json_str = reply
        else:
            json_str = match.group(1)

        try:
            result_json = json.loads(json_str)
        except Exception as e:
            print(f"    JSON decode error: {e}. Raw JSON: {json_str}")
            continue

        triage_status = result_json.get("triage_status", "ok")
        note_type = result_json.get("type")
        tags = result_json.get("tags", [])
        title = result_json.get("title", "").strip()

        if title:
            title = re.sub(r'[\\/:*?"<>|]', '', title).strip().replace(" ", "-").lower()

        if triage_status == "needs_review" or not note_type or not title:
            print(f"    Note marked as needs_review or missing required fields.")
            write_frontmatter_and_move(fpath, {"triage_status": "needs_review"}, note_content, None, None)
            review_count += 1
        else:
            print(f"    Classified as '{note_type}' with title '{title}' and tags {tags}")
            success = write_frontmatter_and_move(fpath, {"type": note_type, "tags": tags, "created": datetime.today().strftime('%Y-%m-%d')}, note_content, note_type, title)
            if success:
                success_count += 1
            else:
                review_count += 1

    print(f"Local API Triage completed: processed={success_count}, review={review_count}")
    compile_index()
    heal_links()
    return True

def run_triage():
    eligible_notes = find_eligible_inbox_notes()
    if not eligible_notes:
        print("No eligible notes for triage. Running standard index compiling...")
        compile_index()
        heal_links()
        return 0

    print(f"Found {len(eligible_notes)} eligible notes for triage.")

    if try_triage_via_hermes():
        return 0

    if try_triage_via_local_api(eligible_notes):
        return 0

    print("[WARNING] Neither Hermes CLI nor direct LLM API configuration is available/successful.")
    print("Please login to Hermes CLI (hermes setup) or configure ai_api_key in config_local.json.")
    print("Running standard index compiling instead...")
    compile_index()
    heal_links()
    return 1

def run_mode(mode):
    """Run a deterministic worker mode and return a process exit code."""
    if mode in {"all", "fast", "index"}:
        compile_index()
        heal_links()
        return 0
    if mode == "sync":
        sync_git()
        return 0
    if mode == "triage":
        return run_triage()

    print("Unknown mode. Use one of: index, fast, all, sync, triage.")
    return 2


if __name__ == "__main__":
    import sys

    requested_mode = sys.argv[1] if len(sys.argv) > 1 else "index"
    raise SystemExit(run_mode(requested_mode))

