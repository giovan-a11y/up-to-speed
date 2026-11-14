"""Combine data/topics/*.json into data/bundle.json (what the app loads) and
stamp sw.js so installed apps pick up the new content.

Usage:  python3 build.py   (standard library only; run after any content change)
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
TOPICS = ROOT / "data" / "topics"
REQUIRED = ["slug", "topic", "category", "refresh", "updated", "tagline", "why", "essentials", "jargon",
            "names", "timeline", "now", "local", "debates", "starters", "sayThis", "avoid", "quiz"]
CATEGORIES = {"Sports", "Luxury & style", "Money", "Food & drink", "Tech", "Culture", "Lifestyle"}

problems, topics = [], []
for p in sorted(TOPICS.glob("*.json")):
    try:
        t = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        problems.append(f"{p.name}: not valid JSON ({e})")
        continue
    missing = [k for k in REQUIRED if k not in t]
    if missing:
        problems.append(f"{p.name}: missing {', '.join(missing)}")
    if t.get("slug") != p.stem:
        problems.append(f"{p.name}: slug should be '{p.stem}'")
    if t.get("category") not in CATEGORIES:
        problems.append(f"{p.name}: category must be one of {sorted(CATEGORIES)}")
    for i, q in enumerate(t.get("quiz", [])):
        if not (isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(q.get("options", []))):
            problems.append(f"{p.name}: quiz question {i + 1} has a bad answer index")
    topics.append(t)
if problems:
    sys.exit("Fix these before publishing:\n  " + "\n  ".join(problems))

weekly_path = ROOT / "data" / "weekly.json"
weekly = json.loads(weekly_path.read_text()) if weekly_path.exists() else {}
repo = json.loads((ROOT / "config.json").read_text()).get("repo", "")
body = json.dumps({"repo": repo, "weekly": weekly, "topics": topics}, ensure_ascii=False, separators=(",", ":"))
(ROOT / "data" / "bundle.json").write_text(body)

h = hashlib.sha1(body.encode())
for name in ("index.html", "manifest.webmanifest"):
    h.update((ROOT / name).read_bytes())
sw = ROOT / "sw.js"
sw.write_text(re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{h.hexdigest()[:12]}";', sw.read_text(), count=1))
print(f"data/bundle.json: {len(topics)} topics, {len(body) // 1024} KB")
