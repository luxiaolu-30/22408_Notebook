import os

ROOT = r"D:\files\个人文件\22408_Notebook"
EXCLUDE_DIRS = {".git", ".workbuddy"}
EXCLUDE_FILES = {"log.md"}

RULES = [
    ("[[408考点总目录", "[[408/408总目录"),
    ("[[408/历年真题/00-总目录", "[[408/历年真题/历年真题总目录"),
    ("[[政治/00-总目录", "[[政治/政治总目录"),
    ("[[英语/00-总目录", "[[英语/英语总目录"),
    ("[[数学/00-总目录", "[[数学/数学总目录"),
    ("[[数学/题目/00-题目总目录", "[[数学/题目/题目总目录"),
    ("[[英语/英语二真题精读/00-真题精读总目录", "[[英语/英语二真题精读/真题精读总目录"),
    ("靠 `00-总目录` 索引", "靠 `总目录` 索引"),
    ("3 主体 + 考点总目录 + 四科专题 27", "3 主体 + 总目录 + 四科专题 27"),
]

changed = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        if not fn.endswith(".md") or fn in EXCLUDE_FILES:
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding="utf-8", newline="") as f:
            text = f.read()
        new = text
        count = 0
        for old, rep in RULES:
            if old in new:
                count += new.count(old)
                new = new.replace(old, rep)
        if count:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            changed[os.path.relpath(p, ROOT)] = count

for k, v in sorted(changed.items()):
    print(f"{k}: {v}")
print("TOTAL:", sum(changed.values()))
