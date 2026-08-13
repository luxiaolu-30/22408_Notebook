# -*- coding: utf-8 -*-
"""为缺失 frontmatter 的知识页面补全 frontmatter（按 WIKI-SCHEMA 3.1 格式）"""
import os, re, subprocess

BASE = r"D:\files\个人文件\22408_Notebook"
TODAY = "2026-08-12"
FALLBACK_CREATED = "2026-07-17"  # 仓库创建时间

def git_created(relpath):
    """查询文件在 git 中的最早创建提交日期"""
    try:
        r = subprocess.run(
            ["git", "-C", BASE, "log", "--diff-filter=A", "--follow", "--format=%ad", "--date=short", "--", relpath],
            capture_output=True, text=True, encoding="utf-8", timeout=15)
        dates = [l.strip() for l in r.stdout.splitlines() if re.match(r"^\d{4}-\d{2}-\d{2}$", l.strip())]
        return dates[-1] if dates else FALLBACK_CREATED
    except Exception:
        return FALLBACK_CREATED

def extract_title(content):
    for line in content.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return None

# (相对路径, type, domain, tags)
TARGETS = []

def add_dir(subdir, type_, domain, tags):
    d = os.path.join(BASE, subdir)
    for f in sorted(os.listdir(d)):
        if f.endswith(".md"):
            TARGETS.append((os.path.join(subdir, f).replace("\\", "/"), type_, domain, tags))

add_dir("数学/基础公式", "concept", "数学", ["考研", "数学", "公式", "基础"])
add_dir("数学/高数考点", "concept", "数学", ["考研", "数学", "高数", "考点"])
add_dir("数学/线代考点", "concept", "数学", ["考研", "数学", "线代", "考点"])
TARGETS += [
    ("数学/数学二历年真题.md", "source-summary", "数学", ["考研", "数学", "真题"]),
    ("408/00-408考点总目录.md", "synthesis", "408", ["考研", "408", "总目录", "必考点"]),
    ("408/01-数据结构必考点.md", "concept", "408", ["考研", "408", "数据结构", "必考点"]),
    ("408/02-计算机组成原理必考点.md", "concept", "408", ["考研", "408", "计算机组成原理", "必考点"]),
    ("408/03-操作系统必考点.md", "concept", "408", ["考研", "408", "操作系统", "必考点"]),
    ("408/04-计算机网络必考点.md", "concept", "408", ["考研", "408", "计算机网络", "必考点"]),
    ("408/05-备考策略与资料推荐.md", "synthesis", "408", ["考研", "408", "备考策略"]),
    ("408/408历年真题.md", "source-summary", "408", ["考研", "408", "真题"]),
    ("英语/历年真题.md", "source-summary", "英语", ["考研", "英语", "真题"]),
    ("英语/常考作文题材与范文.md", "concept", "英语", ["考研", "英语", "作文"]),
    ("英语/考研核心词汇语境记忆_完整版.md", "concept", "英语", ["考研", "英语", "词汇"]),
    ("P.md", "entity", "进度", ["考研", "计划", "时间线"]),
]

fixed, skipped = 0, 0
for rel, type_, domain, tags in TARGETS:
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        print(f"[MISS] {rel}")
        continue
    with open(p, encoding="utf-8") as fh:
        content = fh.read()
    # 已有 frontmatter 则跳过
    if content.lstrip("\ufeff\n").startswith("---"):
        skipped += 1
        print(f"[SKIP] {rel}（已有 frontmatter）")
        continue
    title = extract_title(content)
    if not title:
        print(f"[WARN] {rel} 未找到标题，跳过")
        skipped += 1
        continue
    created = git_created(rel)
    fm = (
        "---\n"
        f"title: {title}\n"
        f"type: {type_}\n"
        f"domain: {domain}\n"
        f"created: {created}\n"
        f"updated: {TODAY}\n"
        f"tags: [{', '.join(tags)}]\n"
        "---\n\n"
    )
    # 去掉开头空白，插入 frontmatter
    stripped = content.lstrip("\ufeff\n")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(fm + stripped)
    fixed += 1
    print(f"[FIX] {rel} | title={title} | created={created}")

print(f"\n完成：修复 {fixed}，跳过 {skipped}")
