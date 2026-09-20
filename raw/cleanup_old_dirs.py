#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""删除旧目录并迁移做题记录表。"""
import os
import shutil

base = r'd:\files\个人文件\22408_Notebook\408\历年真题'

# 1. 迁移做题记录表
src = os.path.join(base, '408真题精读', '真题做题记录表.md')
dst = os.path.join(base, '408真题做题记录表.md')
if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f'迁移做题记录表 → {dst}')

    # 更新内部链接
    with open(dst, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(
        '[[408/历年真题/408真题精读/真题精读总目录|精读页]]',
        '[[408历年真题总目录|答案与解析]]')
    content = content.replace(
        '[[刷题纯净版总目录]]',
        '[[408历年真题总目录]]')
    content = content.replace(
        '[[408/历年真题/408真题精读/真题精读总目录]]',
        '[[408历年真题总目录]]')
    content = content.replace(
        '配套：题目见 [[408历年真题总目录]]（纯题面整卷），答案与解析见 [[408历年真题总目录]]。',
        '配套：题面与答案解析见 [[408历年真题总目录]]，一年一目录。')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
    print('已更新做题记录表内部链接')

# 2. 删除旧目录
old_dirs = [
    '408历年真题纯净刷题版',
    '408真题精读',
    '408真题考点分析',
]
for d in old_dirs:
    p = os.path.join(base, d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f'已删除 {p}')
    else:
        print(f'不存在 {p}')

# 3. 列出新结构
print('\n新目录结构：')
for item in sorted(os.listdir(base)):
    full = os.path.join(base, item)
    if os.path.isdir(full):
        sub = os.listdir(full)
        print(f'  📁 {item}/ — {sub}')
    else:
        print(f'  📄 {item}')
