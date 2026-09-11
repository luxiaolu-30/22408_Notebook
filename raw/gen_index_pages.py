# -*- coding: utf-8 -*-
"""生成两个索引页：英语真题精读总目录 + 数学题目总目录（幂等覆盖）"""
import os, glob, re

# ---------- 英语真题精读总目录 ----------
en_dir = '英语/英语二真题精读'
years = sorted([d for d in os.listdir(en_dir) if os.path.isdir(os.path.join(en_dir, d))],
               key=lambda x: int(x))

rows = []
for y in years:
    fs = sorted(os.listdir(os.path.join(en_dir, y)))
    # 提取 Text 编号排序
    def key(f):
        m = re.search(r'[Tt]ext\s*(\d+)', f)
        return int(m.group(1)) if m else 0
    fs = sorted(fs, key=key)
    cells = []
    for f in fs:
        base = os.path.splitext(f)[0]
        cells.append(f'[[{en_dir}/{y}/{base}]]')
    rows.append((y, cells))

lines = []
lines.append('---')
lines.append('title: 英语二真题精读 · 总目录')
lines.append('type: synthesis')
lines.append('domain: 英语')
lines.append('created: 2026-09-11')
lines.append('updated: 2026-09-11')
lines.append('tags: [英语二, 真题精读, 索引]')
lines.append('---')
lines.append('')
lines.append('# 英语二真题精读 · 总目录')
lines.append('')
lines.append('> 2010-2025 年英语二真题逐篇精读（原文 + 生词注释 + 题目 + 解析）。')
lines.append('> 每年 4 篇（Text1-4），对应阅读 Part A 的四篇文章。')
lines.append('')
lines.append('| 年份 | Text1 | Text2 | Text3 | Text4 |')
lines.append('|------|-------|-------|-------|-------|')
for y, cells in rows:
    lines.append(f'| {y} | ' + ' | '.join(cells) + ' |')
lines.append('')
lines.append('## See Also')
lines.append('- [[英语/英语考情分析]]')
lines.append('')

with open(os.path.join(en_dir, '00-真题精读总目录.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('生成英语索引页，共', len(rows), '年', len(rows)*4, '篇')

# ---------- 数学题目总目录 ----------
m_dir = '数学/题目'
problems = []
for root, dirs, files in os.walk(m_dir):
    for fn in files:
        if fn.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, fn)).replace('\\', '/')
            problems.append(rel)
problems.sort()

# 按 高数/线代 分组，再按主题分组
from collections import defaultdict
group = defaultdict(list)
for p in problems:
    parts = p.split('/')  # 数学/题目/高数/反常积分/xxx.md
    subj = parts[2]       # 高数 or 线代
    topic = parts[3] if len(parts) > 4 else '其他'
    group[(subj, topic)].append(p)

mlines = []
mlines.append('---')
mlines.append('title: 数学题目 · 总目录')
mlines.append('type: synthesis')
mlines.append('domain: 数学')
mlines.append('created: 2026-09-11')
mlines.append('updated: 2026-09-11')
mlines.append('tags: [考研, 数学, 题目, 索引]')
mlines.append('---')
mlines.append('')
mlines.append('# 数学题目 · 总目录')
mlines.append('')
mlines.append('> 高数与线代的典型例题、习题精解，配合考点页与公式页使用。')
mlines.append('')

cur_subj = None
for (subj, topic), ps in sorted(group.items()):
    if subj != cur_subj:
        mlines.append(f'## {subj}')
        cur_subj = subj
    mlines.append(f'')
    mlines.append(f'### {topic}')
    mlines.append('')
    for p in ps:
        base = os.path.splitext(os.path.basename(p))[0]
        mlines.append(f'- [[{p[:-3]}]]')
    mlines.append('')

mlines.append('## See Also')
mlines.append('- [[数学/高数考点/00-高数做题思路总纲]]')
mlines.append('- [[数学/基础公式/02-求导与积分公式速查]]')
mlines.append('')

with open(os.path.join(m_dir, '00-题目总目录.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(mlines))
print('生成数学题目索引页，共', len(problems), '篇')
