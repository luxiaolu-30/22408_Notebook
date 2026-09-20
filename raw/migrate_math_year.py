#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迁移数学二单年真题到一年一目录（题面 + 答案与解析）。

- 题面.md：来自「数学二历年真题纯净刷题版/{year}.md」
- 答案与解析.md：来自「数学二历年真题解析/{year}.md」（缺失年份跳过）
"""
import os
import re
import shutil
import sys


def read_file(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def add_frontmatter(content, title, year, kind):
    """如果原文无 frontmatter，添加一个。"""
    if content.startswith('---'):
        return content
    type_field = {
        'face': 'source',
        'analysis': 'answer-analysis',
    }[kind]
    topic_field = f'\ntopic: 题面' if kind == 'face' else ''
    fm = (
        f"""---
title: {title}
type: {type_field}
domain: 数学
subject: 数学二{topic_field}
year: {year}
created: 2026-09-18
updated: 2026-09-18
tags: ["数学二", {"题面" if kind == "face" else "答案与解析"}, "{year}"]
---

""")
    return fm + content


def migrate(year: int, base: str) -> None:
    src_face = os.path.join(base, '数学二历年真题纯净刷题版', f'{year}.md')
    src_analysis = os.path.join(base, '数学二历年真题解析', f'{year}.md')
    dst = os.path.join(base, str(year))

    if not os.path.exists(src_face):
        print(f'{year} WARN: 题面源文件不存在')
        return

    os.makedirs(dst, exist_ok=True)
    os.makedirs(os.path.join(dst, 'images'), exist_ok=True)

    # 1. 题面.md
    face = read_file(src_face)
    # 修改首行标题
    face = re.sub(r'^# .+数学.二.+',
                  f'# {year} 年数学二真题 · 题面', face, flags=re.MULTILINE)
    # 在首行标题后插入刷题提示
    insert_hint = (
        f'\n> 刷完后对答案：[[答案与解析]]'
        f'{"" if not os.path.exists(src_analysis) else ""}\n')
    if '刷完后对答案' not in face:
        # 在第一个二级标题前插入
        face = re.sub(r'(\n)(## )', r'\1' + insert_hint + r'\1\2', face, count=1)
    face = add_frontmatter(face, f'{year} 年数学二真题 · 题面', year, 'face')

    # 修正图片路径（若有）
    face = re.sub(
        rf'数学二/历年真题/数学二历年真题纯净刷题版/{year}/images/',
        'images/', face)
    face = re.sub(
        rf'数学二/历年真题/数学二历年真题解析/{year}/images/',
        'images/', face)

    write_file(os.path.join(dst, '题面.md'), face)

    # 2. 答案与解析.md（若存在）
    if not os.path.exists(src_analysis):
        print(f'{year} 年：题面已迁移，解析缺失（跳过）')
        return

    analysis = read_file(src_analysis)
    # 修改首行标题
    analysis = re.sub(r'^# .+数学.二.+',
                      f'# {year} 年数学二真题 · 答案与解析',
                      analysis, flags=re.MULTILINE)

    # 如果解析文件中没有「答案速查」段，尝试生成一个
    if '答案速查' not in analysis and '## 一、' in analysis:
        # 抽取所有形如 **答案：X** 或 **X** 的答案
        answers = re.findall(
            r'\*\*答案[：:]\s*([^\*\n]+?)\*\*', analysis)
        if not answers:
            answers = re.findall(
                r'\|\s*\d+\s*\|\s*\*\*([^\|]+?)\*\*', analysis)
        if answers:
            quick_table = '\n## 答案速查\n\n'
            quick_table += ' | '.join(
                f'题{i+1}' for i in range(len(answers))) + '\n'
            quick_table += '|---' * len(answers) + '|\n'
            quick_table += ' | '.join(answers) + '\n\n---\n'
            # 在第一个 ## 之前插入（用 replace 避免 re.sub 转义问题）
            idx = analysis.find('## ')
            if idx > 0:
                analysis = analysis[:idx] + quick_table + analysis[idx:]

    # 添加 See Also
    if '## See Also' not in analysis:
        analysis = analysis.rstrip() + '\n\n---\n\n## See Also\n\n'
        analysis += '- [[题面]] — 仅题干，用于限时刷题\n'
        analysis += f'- [[../数学二历年真题总目录]] — 历年真题总目录\n'
        analysis += '- [[数学考情分析]] — 试卷构成与逐年考点统计\n'

    analysis = add_frontmatter(
        analysis, f'{year} 年数学二真题 · 答案与解析', year, 'analysis')

    analysis = re.sub(
        rf'数学二/历年真题/数学二历年真题纯净刷题版/{year}/images/',
        'images/', analysis)
    analysis = re.sub(
        rf'数学二/历年真题/数学二历年真题解析/{year}/images/',
        'images/', analysis)

    write_file(os.path.join(dst, '答案与解析.md'), analysis)

    # 3. 复制图片（若有）
    for src_dir_name in ['数学二历年真题纯净刷题版', '数学二历年真题解析']:
        src_images = os.path.join(base, src_dir_name, str(year), 'images')
        if not os.path.exists(src_images):
            src_images = os.path.join(base, src_dir_name, 'images', str(year))
        if not os.path.exists(src_images):
            continue
        for f in os.listdir(src_images):
            src_file = os.path.join(src_images, f)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(dst, 'images', f))

    face_lines = sum(1 for _ in open(
        os.path.join(dst, '题面.md'), encoding='utf-8'))
    analysis_lines = sum(1 for _ in open(
        os.path.join(dst, '答案与解析.md'), encoding='utf-8'))
    print(f'{year} 年：题面 {face_lines} 行，解析 {analysis_lines} 行')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python migrate_math_year.py <year>')
        sys.exit(1)
    year = int(sys.argv[1])
    base = r'd:\files\个人文件\22408_Notebook\数学二\历年真题'
    migrate(year, base)
