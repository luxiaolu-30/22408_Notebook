# -*- coding: utf-8 -*-
"""修复数学目录下 [[计算机基础/数学/...]] 错误路径前缀 → [[数学/...]]"""
import os, re

BASE = r"D:\files\个人文件\22408_Notebook"
MATH_DIR = os.path.join(BASE, "数学")

fixed = 0
for root, _, files in os.walk(MATH_DIR):
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(root, f)
        with open(p, encoding="utf-8") as fh:
            content = fh.read()
        new = content.replace("[[计算机基础/数学/", "[[数学/")
        if new != content:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            n = content.count("[[计算机基础/数学/")
            fixed += n
            print(f"[FIX] {os.path.relpath(p, BASE)}: {n} 处")

print(f"\n总计修复 {fixed} 处")

# 验证：数学目录下不应再有任何错误前缀
left = 0
for root, _, files in os.walk(MATH_DIR):
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(root, f)
        with open(p, encoding="utf-8") as fh:
            c = fh.read()
        m = c.count("[[计算机基础/")
        if m:
            left += m
            print(f"[REMAIN] {p}: {m}")
print(f"剩余错误前缀: {left}")
