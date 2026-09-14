import os, re

ROOT = r"D:\files\个人文件\22408_Notebook"
EXCLUDE_DIRS = {".git", ".workbuddy"}

def parse_scalar(v):
    v = v.strip()
    if v.startswith(('"', "'")) and v.endswith(v[0]) and len(v) >= 2:
        return v[1:-1], True
    return v, False

problems = []
ok = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in sorted(filenames):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT)
        with open(p, encoding="utf-8", newline="") as f:
            text = f.read()
        m = re.match(r"^---\s*\r?\n(.*?)\r?\n---", text, re.S)
        if not m:
            continue
        fm = m.group(1)
        tm = re.search(r"^tags:.*$", fm, re.M)
        if not tm:
            continue
        line = tm.group(0).rstrip("\r")
        if not re.match(r"^tags:\s*\[.*\]\s*$", line):
            problems.append((rel, "not inline style", line))
            continue
        inner = line[line.index("[")+1:line.rindex("]")]
        items = [s.strip() for s in inner.split(",") if s.strip()]
        if not items:
            problems.append((rel, "empty tags", line))
            continue
        for it in items:
            val, quoted = parse_scalar(it)
            if not quoted and re.match(r"^-?\d+$", val):
                problems.append((rel, "bare numeric tag", it))
            if val.startswith("#"):
                problems.append((rel, "# prefix", it))
        ok += 1

print("OK files:", ok)
print("Problems:", len(problems))
for pr in problems[:20]:
    print("  ", pr)
