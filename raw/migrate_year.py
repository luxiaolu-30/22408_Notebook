#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 2025 年样板结构迁移单年真题到 一年一目录。
结构：{year}/题面.md + {year}/答案与解析.md + {year}/images/
"""
import os
import re
import shutil
import sys


def migrate(year: int, base: str) -> None:
    src_pure = os.path.join(base, '408历年真题纯净刷题版', f'{year}.md')
    src_read_dir = os.path.join(base, '408真题精读', str(year))
    dst = os.path.join(base, str(year))

    if not os.path.exists(src_pure):
        print(f'WARN: 题面源文件不存在 {src_pure}')
        return
    if not os.path.exists(src_read_dir):
        print(f'WARN: 解析源目录不存在 {src_read_dir}')
        return

    # 1. 创建目标目录
    os.makedirs(dst, exist_ok=True)
    os.makedirs(os.path.join(dst, 'images'), exist_ok=True)

    # 2. 复制题面
    shutil.copy2(src_pure, os.path.join(dst, '题面.md'))

    # 3. 修改题面 frontmatter 和链接
    with open(os.path.join(dst, '题面.md'), 'r', encoding='utf-8') as f:
        face = f.read()
    face = re.sub(r'title: .*', f'title: {year} 年 408 真题 · 题面', face)
    face = re.sub(r'topic: 刷题纯净版', 'topic: 题面', face)
    face = re.sub(r'# .* 题面', f'# {year} 年 408 真题 · 题面', face)
    face = re.sub(r'# .* 刷题纯净版', f'# {year} 年 408 真题 · 题面', face)
    face = re.sub(r'> 对答案：\[\[.*?\]\].*',
                  '> 刷完后对答案、看解析：[[答案与解析]]', face)
    with open(os.path.join(dst, '题面.md'), 'w', encoding='utf-8') as f:
        f.write(face)

    # 4. 复制图片
    src_images = os.path.join(src_read_dir, 'images')
    if os.path.exists(src_images):
        for f in os.listdir(src_images):
            src_file = os.path.join(src_images, f)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(dst, 'images', f))

    # 5. 拼接 4 个解析文件
    files = [
        ('数据结构.md', '数据结构'),
        ('计算机组成原理.md', '计算机组成原理'),
        ('操作系统.md', '操作系统'),
        ('计算机网络.md', '计算机网络'),
    ]

    choice_ans = {}      # 题号 -> 答案字母
    comp_info = {}       # 题号 -> (分值, 科目, 考点)
    comp_ans = {}        # 题号 -> 首句

    body_parts = []
    for fname, subj in files:
        fpath = os.path.join(src_read_dir, fname)
        if not os.path.exists(fpath):
            print(f'WARN: {fpath} 不存在，跳过')
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        start_idx = content.find('## 一、单项选择题')
        end_idx = content.find('## See Also')
        if start_idx < 0 or end_idx < 0:
            print(f'WARN: {fpath} 缺少 ## 一 或 ## See Also')
            continue
        body = content[start_idx:end_idx]

        # 提取选择题答案（题号+分值+考点+答案字母）
        # 单题块以 ### N. 开头
        mc_pattern = re.compile(
            r'###\s+(\d+)\.\s+（(\d+)\s*分\s*·\s*([^）]+?)）.*?\*\*答案\*\*：\s*([A-D])',
            re.DOTALL)
        for m in mc_pattern.finditer(body):
            qnum = int(m.group(1))
            score = m.group(2)
            point = m.group(3).strip()
            ans = m.group(4)
            if qnum <= 40:
                choice_ans[qnum] = ans

        # 提取综合题题号、分值、考点
        comp_pattern = re.compile(
            r'###\s+(\d+)\.\s+（(\d+)\s*分\s*·\s*([^）]+?)）')
        for m in comp_pattern.finditer(body):
            qnum = int(m.group(1))
            score = m.group(2)
            point = m.group(3).strip()
            if qnum >= 41:
                comp_info[qnum] = (score, subj, point)

        # 提取综合题答案首句
        comp_ans_pattern = re.compile(
            r'###\s+(\d+)\.\s+（.*?）.*?\*\*答案.*?：\s*([^\r\n]+)',
            re.DOTALL)
        for m in comp_ans_pattern.finditer(body):
            qnum = int(m.group(1))
            ans_line = m.group(2).strip()
            if qnum >= 41:
                first = re.split(r'[。\n]', ans_line)[0]
                if len(first) > 80:
                    first = first[:80] + '...'
                comp_ans[qnum] = first

        # 替换图片路径
        body = body.replace(
            f'408/历年真题/408真题精读/{year}/images/', 'images/')
        # 替换章节标题
        body = body.replace('## 一、单项选择题', f'### 选择题 · {subj}')
        body = body.replace('## 二、综合应用题', f'### 综合题 · {subj}')
        body_parts.append(body)

    # 6. 生成 答案与解析.md
    out_file = os.path.join(dst, '答案与解析.md')

    # 6.1 头部
    header = f"""---
title: {year} 年 408 真题 · 答案与解析
type: answer-analysis
domain: 408
year: {year}
created: 2026-09-18
updated: 2026-09-18
tags: ["408", 答案与解析, "{year}"]
---

# {year} 年 408 真题 · 答案与解析

> 刷完 [[题面]] 后用此页对答案、看解析。
> 顺序：数据结构（1–11, 41–42）→ 组成原理（12–22, 43–44）→ 操作系统（23–32, 45–46）→ 计算机网络（33–40, 47）

## 一、选择题答案速查表（40 题，每题 2 分，共 80 分）

"""

    # 6.2 选择题答案速查表（4 张表 × 10 题）
    tables = ''
    for row in range(4):
        start_q = row * 10 + 1
        qnums = list(range(start_q, start_q + 10))
        header_row = '| 题号 | ' + ' | '.join(str(q) for q in qnums) + ' |'
        ans_row = '| 答案 | ' + ' | '.join(
            f'**{choice_ans.get(q, "?")}**' for q in qnums) + ' |'
        subj_row = '| 科目 | ' + ' | '.join(
            '数结' if q <= 11 else
            '组原' if q <= 22 else
            '操作' if q <= 32 else
            '计网' for q in qnums) + ' |'
        tables += f'{header_row}\n{ans_row}\n{subj_row}\n\n'

    tables += '> 科目缩写：数结 = 数据结构 | 组原 = 计算机组成原理 | 操作 = 操作系统 | 计网 = 计算机网络\n\n## 二、综合题答案要点速查表（7 题，共 70 分）\n\n'

    # 6.3 综合题要点表
    tables += '| 题号 | 分值 | 科目 | 考点 | 关键结论 |\n|------|------|------|------|----------|\n'
    for q in range(41, 48):
        if q in comp_info:
            score, subj, point = comp_info[q]
            ans = comp_ans.get(q, '—')
            tables += f'| {q} | {score} | {subj} | {point} | {ans} |\n'

    tables += '\n---\n\n## 三、详细解析\n\n> 以下按题号顺序排列。每题包含题干、选项、答案、解析。\n> 图片以相对路径 `images/xxx.webp` 引用，与本文同目录。\n\n'

    # 6.4 拼接正文
    body_content = '\n'.join(body_parts)
    # 去掉末尾多余的 ---
    body_content = re.sub(r'---\s*$', '', body_content)
    body_content = re.sub(r'\n\s*\n\s*\n', '\n\n', body_content)

    # 6.5 写入文件
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(tables)
        f.write(body_content)
        # See Also
        f.write('\n## See Also\n\n- [[题面]] — 仅题干与选项，用于限时刷题\n')
        f.write('- [[../408历年真题总目录]] — 历年真题总目录\n')
        f.write('- [[408考情分析]] — 试卷构成与逐年考点统计\n')

    total_lines = sum(1 for _ in open(out_file, encoding='utf-8'))
    print(f'{year} 年：选择题答案 {len(choice_ans)} 条，综合题 {len(comp_info)} 条，总行数 {total_lines}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python migrate_year.py <year>')
        sys.exit(1)
    year = int(sys.argv[1])
    base = r'd:\files\个人文件\22408_Notebook\408\历年真题'
    migrate(year, base)
