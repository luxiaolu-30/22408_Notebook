#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 2025 年样板结构迁移英语二单年真题到一年一目录。
结构：{year}/题面.md + 答案与解析.md（客观题） + 主观题解析.md + images/
- 题面.md：整卷（来自刷题纯净版）
- 答案与解析.md：完形 + Text1-4 + 新题型（合并原文+题目+答案+解析+长难句精读）
- 主观题解析.md：翻译 + 小作文 + 大作文
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


def extract_body(content):
    """从精读文件提取正文（去掉 frontmatter 和首行标题），保留所有内容。"""
    if content is None:
        return ''
    # 去掉 frontmatter
    m = re.match(r'^---\n.*?\n---\n*', content, re.DOTALL)
    if m:
        content = content[m.end():]
    return content.strip()


def extract_answer_line(content, pattern=r'### 参考答案\s*\n([^\n]+)'):
    """从精读文件提取参考答案行。"""
    if not content:
        return ''
    m = re.search(pattern, content)
    if m:
        return m.group(1).strip()
    return ''


def migrate(year: int, base: str) -> None:
    src_pure = os.path.join(base, '英语二历年真题纯净刷题版', f'{year}.md')
    src_read_dir = os.path.join(base, '英语二真题精读', str(year))
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

    # 2. 复制题面并修改
    shutil.copy2(src_pure, os.path.join(dst, '题面.md'))
    face = read_file(os.path.join(dst, '题面.md'))
    # 在题面顶部 frontmatter 添加（若原文件无 frontmatter 则加一个）
    if not face.startswith('---'):
        face = f"""---
title: {year} 年英语二真题 · 题面
type: source
domain: 英语
subject: 英语二
topic: 题面
year: {year}
created: 2026-09-18
updated: 2026-09-18
tags: ["英语二", 题面, "{year}"]
---

""" + face

    # 修改原文件首行标题（若有 # 开头的标题）
    face = re.sub(r'^# .*英语.*卷.*$',
                  f'# {year} 年英语二真题 · 题面', face, flags=re.MULTILINE)
    # 在第一个 --- 之后插入「刷完后对答案」提示（若不存在）
    if '刷完后对答案' not in face:
        # 在第二个 --- 之后插入
        parts = face.split('---', 2)
        if len(parts) >= 3:
            face = parts[0] + '---' + parts[1] + '---\n\n' + \
                f'> 刷完后对答案：[[答案与解析]]（客观题）· [[主观题解析]]（翻译+作文）\n\n' + parts[2]

    with open(os.path.join(dst, '题面.md'), 'w', encoding='utf-8') as f:
        f.write(face)

    # 3. 读取 6 个客观题文件
    objective_files = ['完形填空.md', 'Text1.md', 'Text2.md',
                       'Text3.md', 'Text4.md', '新题型.md']
    subjective_files = ['翻译.md', '小作文.md', '大作文.md']

    obj_bodies = {}
    for fname in objective_files:
        obj_bodies[fname] = read_file(os.path.join(src_read_dir, fname))

    subj_bodies = {}
    for fname in subjective_files:
        subj_bodies[fname] = read_file(os.path.join(src_read_dir, fname))

    # 4. 提取答案速查
    # 完形 1-20
    cloze_ans = extract_answer_line(obj_bodies['完形填空.md'] or '')
    # Text1-4 各 5 题 21-40
    text_answers = []
    for i, t in enumerate(['Text1.md', 'Text2.md', 'Text3.md', 'Text4.md']):
        ans = extract_answer_line(obj_bodies[t] or '')
        text_answers.append(ans)
    # 新题型 41-45
    newtype_ans = extract_answer_line(obj_bodies['新题型.md'] or '')

    # 5. 生成 答案与解析.md（客观题）
    out_obj = os.path.join(dst, '答案与解析.md')

    header = f"""---
title: {year} 年英语二真题 · 答案与解析（客观题）
type: answer-analysis
domain: 英语
subject: 英语二
year: {year}
created: 2026-09-18
updated: 2026-09-18
tags: ["英语二", 答案与解析, "{year}"]
---

# {year} 年英语二真题 · 答案与解析（客观题）

> 刷完 [[题面]] 后用此页对答案、看解析（客观题部分）。
> 主观题（翻译+作文）见 [[主观题解析]]。
> 顺序：完形填空（1-20）→ Text1（21-25）→ Text2（26-30）→ Text3（31-35）→ Text4（36-40）→ 新题型（41-45）

## 一、答案速查表

### 完形填空（1-20，每题 0.5 分，共 10 分）

{cloze_ans or '—'}

### 阅读理解 Part A（21-40，每题 2 分，共 40 分）

| Text | 题号 | 答案 |
|------|------|------|
| Text1 | 21-25 | {text_answers[0] or '—'} |
| Text2 | 26-30 | {text_answers[1] or '—'} |
| Text3 | 31-35 | {text_answers[2] or '—'} |
| Text4 | 36-40 | {text_answers[3] or '—'} |

### 阅读理解 Part B 新题型（41-45，每题 2 分，共 10 分）

{newtype_ans or '—'}

---

## 二、详细解析

"""

    # 拼接 6 个客观题文件正文
    obj_content = ''
    section_titles = {
        '完形填空.md': '完形填空（1-20）',
        'Text1.md': 'Text1（21-25）',
        'Text2.md': 'Text2（26-30）',
        'Text3.md': 'Text3（31-35）',
        'Text4.md': 'Text4（36-40）',
        '新题型.md': '新题型 Part B（41-45）',
    }
    for fname in objective_files:
        body = extract_body(obj_bodies[fname])
        if not body:
            continue
        # 将原文件中的 # 标题改为 ### 子标题
        body = re.sub(r'^# .+$',
                      f'### {section_titles[fname]}', body, flags=re.MULTILINE)
        # 将 ## 二级标题降为 #### 四级
        body = re.sub(r'^## ', '#### ', body, flags=re.MULTILINE)
        # 将 ### 三级标题降为 ##### 五级
        body = re.sub(r'^### ', '##### ', body, flags=re.MULTILINE)
        obj_content += body + '\n\n---\n\n'

    # 修正图片路径（若有）
    obj_content = re.sub(
        rf'英语二/历年真题/英语二真题精读/{year}/images/',
        'images/', obj_content)
    obj_content = re.sub(
        rf'历年真题/英语二真题精读/{year}/images/',
        'images/', obj_content)

    # See Also
    obj_content += """
## See Also

- [[题面]] — 仅题干与选项，用于限时刷题
- [[主观题解析]] — 翻译+小作文+大作文（含范文）
- [[../英语二历年真题总目录]] — 历年真题总目录
- [[英语考情分析]] — 试卷构成与逐年考点统计
"""

    with open(out_obj, 'w', encoding='utf-8') as f:
        f.write(header + obj_content)

    # 6. 生成 主观题解析.md
    out_subj = os.path.join(dst, '主观题解析.md')

    subj_header = f"""---
title: {year} 年英语二真题 · 主观题解析（翻译+作文）
type: answer-analysis
domain: 英语
subject: 英语二
year: {year}
created: 2026-09-18
updated: 2026-09-18
tags: ["英语二", 主观题解析, "{year}"]
---

# {year} 年英语二真题 · 主观题解析（翻译+作文）

> 刷完 [[题面]] 后用此页看翻译参考译文、作文高分范文与解析。
> 客观题（完形+阅读+新题型）见 [[答案与解析]]。
> 顺序：翻译（15 分）→ 小作文（10 分）→ 大作文（15 分）

---

## 详细解析

"""

    subj_section_titles = {
        '翻译.md': '翻译（15 分）',
        '小作文.md': '小作文（10 分）',
        '大作文.md': '大作文（15 分）',
    }
    subj_content = ''
    for fname in subjective_files:
        body = extract_body(subj_bodies[fname])
        if not body:
            continue
        body = re.sub(r'^# .+$',
                      f'### {subj_section_titles[fname]}', body, flags=re.MULTILINE)
        body = re.sub(r'^## ', '#### ', body, flags=re.MULTILINE)
        body = re.sub(r'^### ', '##### ', body, flags=re.MULTILINE)
        subj_content += body + '\n\n---\n\n'

    subj_content = re.sub(
        rf'英语二/历年真题/英语二真题精读/{year}/images/',
        'images/', subj_content)
    subj_content = re.sub(
        rf'历年真题/英语二真题精读/{year}/images/',
        'images/', subj_content)

    subj_content += """
## See Also

- [[题面]] — 仅题干与选项，用于限时刷题
- [[答案与解析]] — 客观题（完形+阅读+新题型）
- [[../英语二历年真题总目录]] — 历年真题总目录
- [[英语考情分析]] — 试卷构成与逐年考点统计
"""

    with open(out_subj, 'w', encoding='utf-8') as f:
        f.write(subj_header + subj_content)

    # 7. 复制图片
    src_images = os.path.join(src_read_dir, 'images')
    if os.path.exists(src_images):
        for f in os.listdir(src_images):
            src_file = os.path.join(src_images, f)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(dst, 'images', f))

    # 统计
    obj_lines = sum(1 for _ in open(out_obj, encoding='utf-8'))
    subj_lines = sum(1 for _ in open(out_subj, encoding='utf-8'))
    print(
        f'{year} 年：客观题 {obj_lines} 行，主观题 {subj_lines} 行，'
        f'完形答案 {cloze_ans[:30]}...')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python migrate_eng_year.py <year>')
        sys.exit(1)
    year = int(sys.argv[1])
    base = r'd:\files\个人文件\22408_Notebook\英语二\历年真题'
    migrate(year, base)
