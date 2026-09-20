#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量修复题面.md：图片相对路径、See Also 链接、frontmatter。"""
import os
import re

base = r'd:\files\个人文件\22408_Notebook\408\历年真题'

for year in range(2009, 2027):
    f = os.path.join(base, str(year), '题面.md')
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    orig = content

    # 1. frontmatter: topic: 刷题纯净版 → topic: 题面
    content = re.sub(r'topic: 刷题纯净版', 'topic: 题面', content)

    # 2. 图片路径：408/历年真题/408真题精读/{year}/images/xxx.webp → images/xxx.webp
    content = re.sub(
        rf'408/历年真题/408真题精读/{year}/images/',
        'images/',
        content)
    # 兼容旧路径前缀（无 408/）
    content = re.sub(
        rf'历年真题/408真题精读/{year}/images/',
        'images/',
        content)
    # 极少数文件用 ../../真题精读/{year}/images/ 相对路径
    content = re.sub(
        rf'\.\./\.\./真题精读/{year}/images/',
        'images/',
        content)

    # 3. See Also: [[408/历年真题/408真题精读/真题精读总目录]] → [[答案与解析]]
    content = content.replace(
        '[[408/历年真题/408真题精读/真题精读总目录]]',
        '[[答案与解析]]')
    content = content.replace(
        '[[408/真题精读/真题精读总目录]]',
        '[[答案与解析]]')

    # 4. See Also: [[408/历年真题/408真题考点分析/{year}]] → [[答案与解析]]
    content = re.sub(
        r'\[\[408/历年真题/408真题考点分析/\d{4}\]\]',
        '[[答案与解析]]',
        content)

    if content != orig:
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(content)
        print(f'{year} 题面.md 已更新')

# 修 408真题做题记录表.md 中残留链接
rec = os.path.join(base, '408真题做题记录表.md')
if os.path.exists(rec):
    with open(rec, 'r', encoding='utf-8') as fp:
        content = fp.read()
    orig = content
    content = content.replace(
        '[[408/真题精读/真题精读总目录|精读页]]',
        '[[408历年真题总目录|答案与解析]]')
    if content != orig:
        with open(rec, 'w', encoding='utf-8') as fp:
            fp.write(content)
        print('408真题做题记录表.md 已更新')
