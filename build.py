"""Combine data/topics/*.json, data/cuisines/*.json and data/guides/*.json into data/bundle.json (what the app loads) and
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
REGIONS = {"Hong Kong", "Asia", "Europe", "Americas", "Middle East & Africa", "Oceania"}


def check_items(where, items):
    if len(items) < 3:
        problems.append(f"{where}: needs at least 3 entries")
    for i, d in enumerate(items):
        for k in ("name", "what"):
            if not d.get(k):
                problems.append(f"{where}: entry {i + 1} missing {k}")
        if not (d.get("tags") or d.get("facts")):
            problems.append(f"{where}: entry {i + 1} ({d.get('name')}) needs tags or facts")


# World cuisines: one file per cuisine, turned into a picture guide.
cuisine_groups = []
for p in sorted((ROOT / "data" / "cuisines").glob("*.json")):
    try:
        c = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        problems.append(f"cuisines/{p.name}: not valid JSON ({e})")
        continue
    if c.get("slug") != p.stem:
        problems.append(f"cuisines/{p.name}: slug should be '{p.stem}'")
    for k in ("cuisine", "flag", "intro", "flavours"):
        if not c.get(k):
            problems.append(f"cuisines/{p.name}: missing {k}")
    if c.get("region") not in REGIONS:
        problems.append(f"cuisines/{p.name}: region must be one of {sorted(REGIONS)}")
    dishes = c.get("dishes") or []
    for d in dishes:
        if not d.get("wiki"):
            problems.append(f"cuisines/{p.name}: {d.get('name')} needs a wiki title for its picture")
    check_items(f"cuisines/{p.name}", [{**d, "tags": d.get("ingredients")} for d in dishes])
    cuisine_groups.append({"slug": c["slug"], "name": c.get("cuisine"), "emoji": c.get("flag"), "region": c.get("region"),
                           "lang": c.get("lang", ""), "order": c.get("order", 999), "intro": c.get("intro"),
                           "key": {"label": "Key flavours", "value": c.get("flavours")}, "hk": c.get("hk", ""),
                           "items": [{**{k: v for k, v in d.items() if k != "ingredients"}, "tags": d.get("ingredients")} for d in dishes]})
cuisine_groups.sort(key=lambda g: (g["order"], g["name"]))
guides = [{"slug": "cuisines", "title": "World cuisines", "emoji": "🍜", "order": 1, "groupNoun": "cuisines",
           "blurb": "Signature dishes from around the world: what they look like, what's in them, and how to say them.",
           "tagLabel": "Main ingredients", "quizTags": True, "request": "Cuisine", "groups": cuisine_groups}]

# Other picture guides: data/guides/<slug>.json, groups inline.
for p in sorted((ROOT / "data" / "guides").glob("*.json")):
    try:
        g = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        problems.append(f"guides/{p.name}: not valid JSON ({e})")
        continue
    if g.get("slug") != p.stem:
        problems.append(f"guides/{p.name}: slug should be '{p.stem}'")
    for k in ("title", "emoji", "blurb", "groups"):
        if not g.get(k):
            problems.append(f"guides/{p.name}: missing {k}")
    seen = set()
    for grp in g.get("groups") or []:
        if not grp.get("slug") or not grp.get("name") or grp["slug"] in seen:
            problems.append(f"guides/{p.name}: every group needs a unique slug and a name")
        seen.add(grp.get("slug"))
        if grp.get("region") and grp["region"] not in REGIONS:
            problems.append(f"guides/{p.name}: {grp.get('name')} region must be one of {sorted(REGIONS)}")
        check_items(f"guides/{p.name} › {grp.get('name')}", grp.get("items") or [])
    guides.append(g)
guides.sort(key=lambda g: (g.get("order", 999), g.get("title", "")))
if problems:
    sys.exit("Fix these before publishing:\n  " + "\n  ".join(problems))

weekly_path = ROOT / "data" / "weekly.json"
weekly = json.loads(weekly_path.read_text()) if weekly_path.exists() else {}
repo = json.loads((ROOT / "config.json").read_text()).get("repo", "")
body = json.dumps({"repo": repo, "weekly": weekly, "topics": topics, "guides": guides}, ensure_ascii=False, separators=(",", ":"))
(ROOT / "data" / "bundle.json").write_text(body)

h = hashlib.sha1(body.encode())
for name in ("index.html", "manifest.webmanifest"):
    h.update((ROOT / name).read_bytes())
sw = ROOT / "sw.js"
sw.write_text(re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{h.hexdigest()[:12]}";', sw.read_text(), count=1))
print(f"data/bundle.json: {len(topics)} topics, {len(guides)} picture guides ({sum(len(x['items']) for g in guides for x in g['groups'])} entries), {len(body) // 1024} KB")
