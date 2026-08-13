# -*- coding: utf-8 -*-
"""22408 知识库健康检查：双链分析脚本（只读，不修改任何文件）"""
import os
import re
import sys
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
    """提取 [[...]] 链接，返回规范化后的目标名集合"""
    links = set()
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1)
        # 去掉 |别名
        target = target.split("|")[0]
        # 去掉 #标题
        target = target.split("#")[0]
        target = target.strip()
        if target:
            links.add(target)
    return links

def main():
    files = all_md_files()
    # basename -> [rel paths]
    by_name = defaultdict(list)
    for rel in files:
        base = os.path.splitext(os.path.basename(rel))[0]
        by_name[base].append(rel)

    outlinks = {}   # rel -> set(targets)
    inlinks = defaultdict(set)  # target_name -> set(rel sources)

    for rel, full in files.items():
        with open(full, encoding="utf-8") as f:
            text = f.read()
        links = extract_links(text)
        outlinks[rel] = links
        for t in links:
            inlinks[t].add(rel)

    # 断链：目标在现有文件名（含/不含路径、带/不带扩展名）中都找不到
    broken = []  # (source_rel, target)
    for rel, links in sorted(outlinks.items()):
        for t in sorted(links):
            # 尝试匹配：直接 basename、带路径、带 .md
            candidates = {t, t + ".md", t.split("/")[-1], t.split("/")[-1] + ".md"}
            found = False
            for c in candidates:
                if c in files:
                    found = True
                    break
                base = os.path.splitext(os.path.basename(c))[0]
                if base in by_name:
                    found = True
                    break
            if not found:
                broken.append((rel, t))

    # 孤立页面：没有入链 且 不是 index/log/README/WIKI-SCHEMA
    special = {"index", "log", "README", "WIKI-SCHEMA"}
    orphans = []
    for rel in sorted(files):
        base = os.path.splitext(os.path.basename(rel))[0]
        if base in special:
            continue
        if base not in inlinks:
            orphans.append(rel)
        else:
            # 入链都来自自己？(自引用)
            sources = inlinks[base]
            if sources and all(s == rel for s in sources):
                orphans.append(rel)

    print("=" * 60)
    print(f"总文件数: {len(files)}")
    print(f"断链总数: {len(broken)}")
    print("-" * 60)
    for src, tgt in broken:
        print(f"  [断链] {src} -> [[{tgt}]]")
    print("-" * 60)
    print(f"孤立页面数: {len(orphans)} (无任何其他页面链接到它)")
    for o in orphans:
        print(f"  [孤立] {o}")

    # 出链为 0 的页面（除了 index/log）
    no_out = [rel for rel, links in outlinks.items() if not links and os.path.basename(rel) not in special]
    print("-" * 60)
    print(f"无出链页面数: {len(no_out)}")
    for n in no_out:
        print(f"  [无出链] {n}")

    # 入链最多的页面 TOP15
    print("-" * 60)
    print("入链最多的页面 TOP15:")
    ranked = sorted(inlinks.items(), key=lambda kv: len(kv[1]), reverse=True)
    for name, srcs in ranked[:15]:
        print(f"  {len(srcs):>3}  <- {name}   (来自: {', '.join(sorted(srcs)[:4])}{'...' if len(srcs)>4 else ''})")

if __name__ == "__main__":
    main()
