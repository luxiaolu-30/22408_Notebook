# -*- coding: utf-8 -*-
"""408 按科目分目录：移动 4 个必考点文件 + 全局更新链接"""
import os, shutil

ROOT = '.'
SKIP_DIRS = {'.git', '.obsidian', '.workbuddy', 'raw'}
SKIP_FILES = {'wiki/log.md'}  # 历史日志不可变，单独追加

# 1. 移动文件到四科子目录
moves = [
    ('408/01-数据结构必考点.md', '408/数据结构/01-数据结构必考点.md'),
    ('408/02-计算机组成原理必考点.md', '408/计算机组成原理/02-计算机组成原理必考点.md'),
    ('408/03-操作系统必考点.md', '408/操作系统/03-操作系统必考点.md'),
    ('408/04-计算机网络必考点.md', '408/计算机网络/04-计算机网络必考点.md'),
]
for src, dst in moves:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.move(src, dst)
        print('移动:', src, '->', dst)

# 2. 全局替换链接（带路径 + 不带路径两种写法）
repls = [
    ('[[408/01-数据结构必考点', '[[408/数据结构/01-数据结构必考点'),
    ('[[01-数据结构必考点', '[[408/数据结构/01-数据结构必考点'),
    ('[[408/02-计算机组成原理必考点', '[[408/计算机组成原理/02-计算机组成原理必考点'),
    ('[[02-计算机组成原理必考点', '[[408/计算机组成原理/02-计算机组成原理必考点'),
    ('[[408/03-操作系统必考点', '[[408/操作系统/03-操作系统必考点'),
    ('[[03-操作系统必考点', '[[408/操作系统/03-操作系统必考点'),
    ('[[408/04-计算机网络必考点', '[[408/计算机网络/04-计算机网络必考点'),
    ('[[04-计算机网络必考点', '[[408/计算机网络/04-计算机网络必考点'),
]

changed = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        if not fn.endswith('.md'):
            continue
        rel = os.path.relpath(os.path.join(root, fn), ROOT).replace('\\', '/')
        if rel in SKIP_FILES:
            continue
        p = os.path.join(root, fn)
        with open(p, encoding='utf-8') as f:
            text = f.read()
        new = text
        for old, ns in repls:
            new = new.replace(old, ns)
        if new != text:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new)
            changed.append(rel)

print('更新链接的文件数:', len(changed))
for c in changed:
    print('  ', c)
