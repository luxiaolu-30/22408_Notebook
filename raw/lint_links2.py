# -*- coding: utf-8 -*-
"""22408 知识库健康检查 v2：精确链接分析 + frontmatter + 冲突标记（只读）"""
import os
import re
from collections import defaultdict

ROOT = r"D:\files\个人文件\22408_Notebook"
SKIP_DIRS = {".git", ".obsidian", ".workbuddy", "raw"}

def all_md_files():
    files = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                files[rel] = full
    return files

def extract_links(text):
    """返回原始目标列表（保留路径），同时记录原始字符串"""
    out = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        raw = m.group(1)
        target = raw.split("|")[0].split("#")[0].strip()
        out.append((raw, target))
    return out

def file_stem(rel):
    """去 .md 后缀后取 basename（不用 splitext，避免 8.3 之类数字点被误判为扩展名）"""
    stem = rel[:-3] if rel.endswith(".md") else rel
    return os.path.basename(stem)

files = all_md_files()
by_base = defaultdict(list)
for rel in files:
    by_base[file_stem(rel)].append(rel)

# ---------- 1. 链接分类 ----------
path_ok, path_bad, broken, self_links = [], [], [], []
link_src = defaultdict(set)  # base_name -> set(sources)
for rel in sorted(files):
    with open(files[rel], encoding="utf-8") as f:
        text = f.read()
    for raw, tgt in extract_links(text):
        tgt_stem = tgt[:-3] if tgt.endswith(".md") else tgt
        base = os.path.basename(tgt_stem)
        # 1) 目标是否真实存在（basename 匹配）
        exists = base in by_base
        # 2) 链接是否自带路径
        has_path = "/" in tgt or "\\" in tgt
        if not exists:
            broken.append((rel, raw, tgt))
            continue
        # 3) 若带路径，检查路径是否指向正确位置
        if has_path:
            # 去掉 .md 后比较
            tgt_norm = tgt[:-3] if tgt.endswith(".md") else tgt
            # 找到该 basename 的真实路径，看链接路径是否与任一真实路径匹配
            real_paths = by_base[base]
            matched = any(tgt_norm == p[:-3] for p in real_paths)
            if not matched:
                path_bad.append((rel, raw, real_paths))
        # 4) 统计入链（按 basename）
        link_src[base].add(rel)

print("=" * 70)
print("[1] 链接路径前缀错误（目标存在但路径不对，Obsidian 中会断链/歧义）")
print(f"    共 {len(path_bad)} 条")
for rel, raw, real in sorted(path_bad)[:40]:
    print(f"    {rel}: [[{raw}]]  实际路径: {real}")

print("=" * 70)
print("[2] 完全断链（目标页面不存在）")
print(f"    共 {len(broken)} 条")
for rel, raw, tgt in sorted(broken):
    print(f"    {rel}: [[{raw}]]")

# ---------- 2. 孤立页面（按 basename 入链） ----------
special = {"index", "log", "README", "WIKI-SCHEMA"}
print("=" * 70)
print("[3] 孤立页面（没有任何入链；index/README/WIKI-SCHEMA/log 除外）")
orphans = []
for rel in sorted(files):
    base = file_stem(rel)
    if base in special:
        continue
    if base not in link_src:
        orphans.append(rel)
print(f"    共 {len(orphans)} 个")
for o in orphans:
    print(f"    {o}")

# ---------- 3. 入链数（按 basename，去除自我引用） ----------
print("=" * 70)
print("[4] 入链统计（按文件名，排除自引用）")
ranked = sorted(link_src.items(), key=lambda kv: -len(kv[1]))
for name, srcs in ranked[:12]:
    print(f"    {len(srcs):>3}  <- {name}")

# ---------- 4. frontmatter 检查 ----------
print("=" * 70)
print("[5] frontmatter 检查")
REQ_KEYS = ["title", "type", "created", "updated"]
issues = []
no_fm = []
for rel in sorted(files):
    base = file_stem(rel)
    if base in special:
        continue
    with open(files[rel], encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        no_fm.append(rel)
        continue
    fm = m.group(1)
    missing = [k for k in REQ_KEYS if not re.search(rf"^{k}:", fm, re.M)]
    if missing:
        issues.append((rel, f"缺 frontmatter 字段: {missing}"))
    # updated 是否过期（>90 天）
    um = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
    if um:
        d = um.group(1)
        if d < "2026-05-14":
            issues.append((rel, f"updated 距今超 90 天: {d}"))
print(f"    无 frontmatter: {len(no_fm)}")
for rel in no_fm:
    print(f"      [无FM] {rel}")
print(f"    frontmatter 问题: {len(issues)}")
for rel, msg in issues:
    print(f"      [FM] {rel}: {msg}")

# ---------- 5. Git 冲突标记检查 ----------
print("=" * 70)
print("[6] Git 合并冲突残留标记检查")
conflict_files = []
for rel in sorted(files):
    with open(files[rel], encoding="utf-8") as f:
        text = f.read()
    # 检查冲突标记（粗略处理）
    if re.search(r"^<<<<<<< ", text, re.M):
        conflict_files.append(rel)
        cnt = len(re.findall(r"^<<<<<<< ", text, re.M))
        print(f"    [冲突] {rel}: {cnt} 处 <<<<<<< 标记")
        for cm in re.finditer(r"^<<<<<<< .*?\n(.*?)^>>>>>>> .*?$", text, re.M | re.S):
            block = cm.group(1)
            print(f"      ---冲突块---")
            for line in block.splitlines()[:8]:
                print(f"      | {line}")
if not conflict_files:
    print("    无冲突标记")
