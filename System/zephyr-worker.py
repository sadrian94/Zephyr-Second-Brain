import os
import json
import re
import urllib.request
import urllib.error
import subprocess
from datetime import datetime

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(VAULT_DIR, "Capture")
BRAIN_DIR = os.path.join(VAULT_DIR, "Brain")
SYSTEM_DIR = os.path.join(VAULT_DIR, "System")
CONFIG_PATH = os.path.join(SYSTEM_DIR, "config.json")
INDEX_PATH = os.path.join(SYSTEM_DIR, "index.json")

# ==============================================================================
# AI API Key Usage Documentation:
# The LLM API key (configured in config.json under 'ai_api_key') is REQUIRED for:
# 1. Fast Mode Inbox Classification (classify_and_tag): Automatically parsing note 
#    text inside Capture/ and extracting type, tags, and titles.
# 2. Idea Cultivation and Source processing in agent skills (invoked by agents).
#
# It is NOT required for:
# - Scanning directories and compiling index.json
# - Link healing (fixing case differences or broken references)
# - Git status checks and Git auto-commits/sync
# - Running the worker in 'index' mode
# ==============================================================================

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_index():
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(index):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

def call_llm(base_url, api_key, model, system_prompt, user_prompt):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
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
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}\nResponse: {err}")
        raise
    except Exception as e:
        print(f"LLM request error: {e}")
        raise

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

def build_frontmatter(fm):
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            items = ", ".join(f'"{x}"' for x in v)
            lines.append(f"{k}: [{items}]")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)

def _is_likely_daily_log(filename, body):
    """Heuristic: filename matches YYYY-MM-DD or date-like pattern."""
    stem = filename.replace(".md", "")
    if re.match(r'^\d{4}-\d{2}-\d{2}$', stem):
        return True
    # body starts with daily log title
    if re.search(r'# Daily Log', body[:100]):
        return True
    return False

def _is_likely_source(body):
    """Heuristic: body contains a URL or source-like markers."""
    if re.search(r'https?://\S+', body):
        return True
    if re.search(r'\burl:\s*\S+', body):
        return True
    return False

def _is_likely_project(body):
    """Heuristic: body contains project-like keywords."""
    project_markers = [r'\bproject\b', r'專案', r'Project', r'todo', r'TODO', r'Goal', r'goals?', r'deadline']
    score = sum(1 for m in project_markers if re.search(m, body))
    return score >= 2

def fallback_classify(filename, body):
    """Offline classification without LLM API."""
    stem = filename.replace(".md", "")
    tags = []

    if _is_likely_daily_log(filename, body):
        return {"type": "log", "tags": ["daily"], "title": stem}
    elif _is_likely_source(body):
        return {"type": "note", "tags": ["source", "inbox"], "title": stem}
    elif _is_likely_project(body):
        return {"type": "project", "tags": ["project", "inbox"], "title": stem}
    else:
        # Extract a few content words for tags
        words = re.findall(r'[a-zA-Z]{3,}', body.lower())
        word_counts = {}
        for w in words:
            if w not in ('the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'are', 'was', 'were', 'been', 'will', 'can', 'not', 'but', 'all', 'has', 'had', 'its', 'our', 'who', 'how', 'what', 'when', 'where', 'which'):
                word_counts[w] = word_counts.get(w, 0) + 1
        top_words = sorted(word_counts.items(), key=lambda x: -x[1])[:3]
        tags = [w for w, _ in top_words] if top_words else ["inbox"]
        return {"type": "note", "tags": tags, "title": stem}

def classify_and_tag(file_path, content, config):
    # API key check guard
    api_key = config.get("ai_api_key", "")
    if not api_key or "YOUR" in api_key or api_key.startswith("<"):
        print("Skipping AI classification: No valid 'ai_api_key' configured in System/config.json. Using fallback...")
        return fallback_classify(os.path.basename(file_path), content)

    system_prompt = (
        'You are the classification engine for the Zephyr Second Brain.\n'
        'You must output a raw JSON object containing exactly three fields:\n'
        '1. "type": must be one of "project", "log", or "note"\n'
        '2. "tags": a list of 2-4 lowercase topic tags related to the content\n'
        '3. "title": a clean, concise, NTFS-safe title for the note (max 5 words, space-separated, no slashes or special characters)\n'
        'Output ONLY raw JSON. No markdown backticks, no comments.'
    )

    user_prompt = f"Note content to classify:\n\n{content[:2000]}"

    try:
        response_text = call_llm(
            config["ai_base_url"],
            api_key,
            config["ai_model"],
            system_prompt,
            user_prompt
        )
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(response_text)
    except Exception as e:
        print(f"Error classifying {os.path.basename(file_path)}: {e}. Using fallback...")
        return fallback_classify(os.path.basename(file_path), content)

def process_inbox():
    config = load_config()
    if not os.path.exists(CAPTURE_DIR):
        return

    for fname in os.listdir(CAPTURE_DIR):
        if not fname.endswith(".md") or fname == "Home.md":
            continue

        fpath = os.path.join(CAPTURE_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read {fname}: {e}")
            continue

        fm, body = parse_frontmatter(content)

        # Check if already classified
        if fm.get("type"):
            continue

        print(f"Processing unclassified note: {fname}")
        res = classify_and_tag(fpath, body, config)
        if not res:
            # classify_and_tag always returns something now (fallback)
            continue

        fm["type"] = res.get("type", "note")
        fm["tags"] = res.get("tags", [])
        fm["created"] = datetime.now().strftime("%Y-%m-%d")

        # Reconstruct note
        new_content = build_frontmatter(fm) + "\n\n" + body

        # Decide target path
        target_name = res.get("title", fname.replace(".md", "")) + ".md"
        target_name = re.sub(r'[\\/:*?"<>|]', "", target_name)

        if fm["type"] == "log":
            target_path = os.path.join(CAPTURE_DIR, target_name)
        else:
            target_path = os.path.join(BRAIN_DIR, target_name)

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Successfully processed {fname} -> {target_path}")
            if target_path != fpath:
                os.remove(fpath)
                print(f"Deleted old file: {fpath}")
        except Exception as e:
            print(f"Failed to write target file: {e}")

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

if __name__ == "__main__":
    import sys
    mode = "all"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == "fast":
        process_inbox()
        compile_index()
        heal_links()
        sync_git()
    elif mode == "index":
        compile_index()
        heal_links()
    else:
        process_inbox()
        compile_index()
        heal_links()
        sync_git()
