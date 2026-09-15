# -*- coding: utf-8 -*-
"""校验指定文件里的 [[双链]] 是否都能解析到实际页面。"""
import os
import re
import sys

ROOT = r"D:\files\个人文件\22408_Notebook"
os.chdir(ROOT)

byname = {}
bypath = set()
for root, dirs, files in os.walk("."):
    if ".workbuddy" in root or ".git" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            p = os.path.join(root, f).replace("\\", "/")[2:]
            bypath.add(p[:-3])
            byname.setdefault(f[:-3], []).append(p)

LINK = re.compile(r"(?<!\\)\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
PLAIN = re.compile(r"(?<!\\)\[\[")

targets = sys.argv[1:] or ["README.md"]
for target in targets:
    t = open(target, encoding="utf-8").read()
    bad = [m.group(1) for m in LINK.finditer(t)
           if m.group(1) not in bypath and m.group(1).split("/")[-1] not in byname]
    print(f"{target}: 双链 {len(PLAIN.findall(t))} 条 | 断链: {bad if bad else '无'}")
