#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理数学二旧目录、建总目录、更新所有引用链接。"""
import os
import shutil

base_math = r'd:\files\个人文件\22408_Notebook\数学二'
base_zhenti = os.path.join(base_math, '历年真题')
proj_root = r'd:\files\个人文件\22408_Notebook'


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# 1. 删除旧目录
old_dirs = [
    '数学二历年真题纯净刷题版',
    '数学二历年真题解析',
]
for d in old_dirs:
    p = os.path.join(base_zhenti, d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f'已删除 {p}')

# 2. 创建 数学二历年真题总目录.md
index_path = os.path.join(base_zhenti, '数学二历年真题总目录.md')

# 检查每年是否有解析文件
years_with_analysis = []
years_without_analysis = []
for y in range(2006, 2026):
    analysis_path = os.path.join(base_zhenti, str(y), '答案与解析.md')
    if os.path.exists(analysis_path):
        years_with_analysis.append(y)
    else:
        years_without_analysis.append(y)

# 生成表格行
table_rows = []
for y in range(2025, 2005, -1):
    face_link = f'[[{y}/题面]]'
    if y in years_with_analysis:
        analysis_link = f'[[{y}/答案与解析]]'
    else:
        analysis_link = '— 待补充'
    table_rows.append(f'| {y} | {face_link} | {analysis_link} |')

index_content = f"""---
title: 数学二历年真题 · 总目录
type: synthesis
domain: 数学
subject: 数学二
created: 2026-09-18
updated: 2026-09-18
tags: [数学二, 真题, 索引]
---

# 数学二历年真题 · 总目录

> 2006-2025 共 20 套数学二真题，一年一目录，每目录下含两份文件：
> - **题面**：整卷试题原文与题目，用于限时刷题；
> - **答案与解析**：答案速查 + 逐题详解（部分年份为简版答案）。
>
> 注：{', '.join(map(str, years_without_analysis))} 年解析暂缺，仅迁移题面。

| 年份 | 题面 | 答案与解析 |
|------|------|------|
""" + '\n'.join(table_rows) + """

## See Also

- [[数学考情分析]] — 试卷构成与逐年考点统计
- [[数学总目录]]
"""

write(index_path, index_content)
print(f'创建总目录 → {index_path}')
print(f'有解析年份：{years_with_analysis}')
print(f'缺解析年份：{years_without_analysis}')

# 3. 更新各文件中的旧链接
def fix(content):
    # 替换旧链接为新链接
    for y in range(2006, 2026):
        content = content.replace(
            f'[[数学二/历年真题/数学二历年真题纯净刷题版/{y}]]',
            f'[[数学二/历年真题/{y}/题面]]')
        content = content.replace(
            f'[[数学二/历年真题/数学二历年真题解析/{y}]]',
            f'[[数学二/历年真题/{y}/答案与解析]]')
        # 没有路径前缀的
        content = content.replace(
            f'[[数学二历年真题纯净刷题版/{y}]]',
            f'[[数学二/历年真题/{y}/题面]]')
        content = content.replace(
            f'[[数学二历年真题解析/{y}]]',
            f'[[数学二/历年真题/{y}/答案与解析]]')
    return content


# 数学总目录.md
f = os.path.join(base_math, '数学总目录.md')
content = read(f)
orig = content
content = fix(content)
# 重写「历年真题」段
import re
new_section = """## 历年真题（子目录 `数学二/历年真题/`，一年一目录）

> 2006-2025 共 20 套真题，一年一目录，每目录含「题面.md」+「答案与解析.md」（部分年份解析暂缺）。

| 页面 | 说明 |
|------|------|
| [[数学二历年真题总目录]] | 2006-2025 真题总目录（一年一目录索引） |"""
content = re.sub(
    r'## 历年真题.*?(?=\n---\n|\n## |\Z)',
    new_section + '\n', content, flags=re.DOTALL)
if content != orig:
    write(f, content)
    print(f'数学总目录.md 已更新')

# README.md
readme = os.path.join(proj_root, 'README.md')
content = read(readme)
orig = content
content = fix(content)
# 1) 目录树：在数学二树视图中插入「历年真题」目录
content = content.replace(
    '│   ├── 题目/                     # 9 篇（高数 7 + 线代 1 + 总目录）\n│   ├── 数学总目录.md             # 子索引',
    '│   ├── 题目/                     # 9 篇（高数 7 + 线代 1 + 总目录）\n'
    '│   ├── 历年真题/                 # 2006-2025 共 20 套，一年一目录\n'
    '│   │   └── {年份}/题面.md + 答案与解析.md\n'
    '│   ├── 数学总目录.md             # 子索引')
# 2) 数学二导航表
content = content.replace(
    '| [[数学二/题目/题目总目录]] | 题目练习索引（高数 7 + 线代 1） |',
    '| [[数学二/题目/题目总目录]] | 题目练习索引（高数 7 + 线代 1） |\n'
    '| [[数学二/历年真题/数学二历年真题总目录]] | 2006-2025 真题一年一目录（题面+答案与解析） |')
if content != orig:
    write(readme, content)
    print(f'README.md 已更新')

# 4. 列出新结构
print('\n新目录结构：')
for item in sorted(os.listdir(base_zhenti)):
    full = os.path.join(base_zhenti, item)
    if os.path.isdir(full):
        sub = os.listdir(full)
        print(f'  📁 {item}/ — {sub}')
    else:
        print(f'  📄 {item}')
