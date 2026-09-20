#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迁移英语二做题记录表到顶级、删除旧目录、更新所有引用链接。"""
import os
import re
import shutil

base_eng = r'd:\files\个人文件\22408_Notebook\英语二'
base_zhenti = os.path.join(base_eng, '历年真题')
proj_root = r'd:\files\个人文件\22408_Notebook'


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# 1. 迁移做题记录表
src = os.path.join(base_zhenti, '英语二真题做题记录表', '真题做题记录表.md')
dst = os.path.join(base_zhenti, '英语二真题做题记录表.md')
if os.path.exists(src):
    shutil.copy2(src, dst)
    content = read(dst)
    # 更新内部链接
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题精读总目录|精读页]]',
        '[[英语二历年真题总目录|答案与解析]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题精读总目录]]',
        '[[英语二历年真题总目录]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题做题记录表]]',
        '[[英语二真题做题记录表]]')
    write(dst, content)
    print(f'迁移做题记录表 → {dst}')

# 2. 删除旧目录
old_dirs = [
    '英语二历年真题纯净刷题版',
    '英语二真题精读',
    '英语二真题做题记录表',
]
for d in old_dirs:
    p = os.path.join(base_zhenti, d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f'已删除 {p}')

# 3. 创建/更新 英语二历年真题总目录.md
index_path = os.path.join(base_zhenti, '英语二历年真题总目录.md')
index_content = """---
title: 英语二历年真题 · 总目录
type: synthesis
domain: 英语
subject: 英语二
created: 2026-09-18
updated: 2026-09-18
tags: [英语二, 真题, 索引]
---

# 英语二历年真题 · 总目录

> 2010-2025 共 16 套英语二真题，一年一目录，每目录下含三份文件：
> - **题面**：整卷试题原文与题目，用于限时刷题；
> - **答案与解析**（客观题）：答案速查表 + 完形/Text1-4/新题型原文+题目+答案+长难句精读；
> - **主观题解析**：翻译参考译文 + 小作文/大作文高分范文与解析。

| 年份 | 题面 | 答案与解析（客观题） | 主观题解析 |
|------|------|------|------|
| 2025 | [[2025/题面]] | [[2025/答案与解析]] | [[2025/主观题解析]] |
| 2024 | [[2024/题面]] | [[2024/答案与解析]] | [[2024/主观题解析]] |
| 2023 | [[2023/题面]] | [[2023/答案与解析]] | [[2023/主观题解析]] |
| 2022 | [[2022/题面]] | [[2022/答案与解析]] | [[2022/主观题解析]] |
| 2021 | [[2021/题面]] | [[2021/答案与解析]] | [[2021/主观题解析]] |
| 2020 | [[2020/题面]] | [[2020/答案与解析]] | [[2020/主观题解析]] |
| 2019 | [[2019/题面]] | [[2019/答案与解析]] | [[2019/主观题解析]] |
| 2018 | [[2018/题面]] | [[2018/答案与解析]] | [[2018/主观题解析]] |
| 2017 | [[2017/题面]] | [[2017/答案与解析]] | [[2017/主观题解析]] |
| 2016 | [[2016/题面]] | [[2016/答案与解析]] | [[2016/主观题解析]] |
| 2015 | [[2015/题面]] | [[2015/答案与解析]] | [[2015/主观题解析]] |
| 2014 | [[2014/题面]] | [[2014/答案与解析]] | [[2014/主观题解析]] |
| 2013 | [[2013/题面]] | [[2013/答案与解析]] | [[2013/主观题解析]] |
| 2012 | [[2012/题面]] | [[2012/答案与解析]] | [[2012/主观题解析]] |
| 2011 | [[2011/题面]] | [[2011/答案与解析]] | [[2011/主观题解析]] |
| 2010 | [[2010/题面]] | [[2010/答案与解析]] | [[2010/主观题解析]] |

## See Also

- [[英语二真题做题记录表]] — 逐年逐题做题记录表
- [[英语考情分析]] — 试卷构成与逐年考点统计
- [[英语总目录]]
"""
write(index_path, index_content)
print(f'创建/更新总目录 → {index_path}')

# 4. 更新各文件中的旧链接
# 通用替换规则
def fix(content):
    # 替换 真题精读总目录 → 总目录
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题精读总目录]]',
        '[[英语二历年真题总目录]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题精读总目录|精读页]]',
        '[[英语二历年真题总目录|答案与解析]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题精读总目录|逐篇精读]]',
        '[[英语二历年真题总目录|逐年真题]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题做题记录表/真题做题记录表]]',
        '[[英语二/历年真题/英语二真题做题记录表]]')
    content = content.replace(
        '[[英语二/历年真题/英语二真题精读/真题做题记录表]]',
        '[[英语二/历年真题/英语二真题做题记录表]]')
    # 残留路径前缀
    content = content.replace('英语二/英语二真题精读/', '英语二/历年真题/')
    return content


# README.md
readme = os.path.join(proj_root, 'README.md')
content = read(readme)
orig = content

# 1) 目录树
content = content.replace(
    '│   ├── 英语二真题精读/            # 2010-2025 共 16 年 × 9 题型 = 145 篇',
    '│   ├── 历年真题/                 # 2010-2025 共 16 套，一年一目录\n'
    '│   │   └── {年份}/题面.md + 答案与解析.md + 主观题解析.md')
# 表格
content = content.replace(
    '| [[英语二/历年真题/英语二真题精读/真题精读总目录]] | 2010-2025 真题按题型精读（145 篇） |',
    '| [[英语二/历年真题/英语二历年真题总目录]] | 2010-2025 真题一年一目录（题面+客观题解析+主观题解析） |')
content = content.replace(
    '| [[英语二/历年真题/英语二真题做题记录表/真题做题记录表]] | 2010-2025 逐年逐题做题记录表（16 套 × 48 题，题号/题型/答案已预填） |',
    '| [[英语二/历年真题/英语二真题做题记录表]] | 2010-2025 逐年逐题做题记录表（16 套 × 48 题，题号/题型/答案已预填） |')
if content != orig:
    write(readme, content)
    print(f'README.md 已更新')

# 英语总目录.md
f = os.path.join(base_eng, '英语总目录.md')
content = read(f)
orig = content
content = fix(content)
# 表格行替换
content = content.replace(
    '| [[英语二/历年真题/英语二真题精读/真题精读总目录]] | 2010-2025 逐篇精读总目录（阅读 + 其他题型，按年份索引） |',
    '| [[英语二/历年真题/英语二历年真题总目录]] | 2010-2025 一年一目录真题总目录（题面+客观题解析+主观题解析） |')
content = content.replace(
    '| [[英语二/历年真题/英语二真题做题记录表/真题做题记录表]] | 2010-2025 逐年逐题做题记录表（16 套 × 48 题，题号/题型/答案已预填） |',
    '| [[英语二/历年真题/英语二真题做题记录表]] | 2010-2025 逐年逐题做题记录表（16 套 × 48 题，题号/题型/答案已预填） |')
content = content.replace(
    '## 真题精读（素材页，子目录 `英语二/英语二真题精读/`）',
    '## 历年真题（一年一目录，子目录 `英语二/历年真题/`）')
content = content.replace(
    '### 真题精读（子目录 `英语二/英语二真题精读/`）',
    '### 历年真题（子目录 `英语二/历年真题/`）')
content = content.replace(
    '精读素材 → [[英语二/历年真题/英语二真题精读/真题精读总目录]]',
    '答案与解析 → [[英语二/历年真题/英语二历年真题总目录]]')
content = content.replace(
    '[[英语二/历年真题/英语二真题精读/真题精读总目录]] — 2010-2025 逐篇精读素材',
    '[[英语二/历年真题/英语二历年真题总目录]] — 2010-2025 一年一目录')
content = content.replace(
    '逐篇精读',
    '逐年精读')
if content != orig:
    write(f, content)
    print(f'英语总目录.md 已更新')

# 英语考情分析.md
f = os.path.join(base_eng, '英语考情分析.md')
content = read(f)
orig = content
content = fix(content)
content = content.replace(
    '逐年精读版见 [[英语二/历年真题/英语二真题精读/真题精读总目录]]',
    '逐年解析见 [[英语二/历年真题/英语二历年真题总目录]]')
content = content.replace(
    '[[英语二/历年真题/英语二真题精读/真题精读总目录]] — 2010-2025 逐篇精读',
    '[[英语二/历年真题/英语二历年真题总目录]] — 2010-2025 逐年真题')
if content != orig:
    write(f, content)
    print(f'英语考情分析.md 已更新')

# 英语备考规划与资料推荐.md
f = os.path.join(base_eng, '英语备考规划与资料推荐.md')
content = read(f)
orig = content
content = fix(content)
content = content.replace(
    '精读素材 → [[英语二/历年真题/英语二真题精读/真题精读总目录]]',
    '答案与解析 → [[英语二/历年真题/英语二历年真题总目录]]')
content = content.replace(
    '[[英语二/历年真题/英语二真题精读/真题精读总目录]] — 2010-2025 逐篇精读素材',
    '[[英语二/历年真题/英语二历年真题总目录]] — 2010-2025 一年一目录')
if content != orig:
    write(f, content)
    print(f'英语备考规划与资料推荐.md 已更新')

# 英语考前速看.md（检查是否引用旧路径）
f = os.path.join(base_eng, '英语考前速看.md')
if os.path.exists(f):
    content = read(f)
    orig = content
    content = fix(content)
    if content != orig:
        write(f, content)
        print(f'英语考前速看.md 已更新')

# 5. 列出新结构
print('\n新目录结构：')
for item in sorted(os.listdir(base_zhenti)):
    full = os.path.join(base_zhenti, item)
    if os.path.isdir(full):
        sub = os.listdir(full)
        print(f'  📁 {item}/ — {sub}')
    else:
        print(f'  📄 {item}')
