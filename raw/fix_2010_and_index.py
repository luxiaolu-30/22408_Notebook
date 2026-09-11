# -*- coding: utf-8 -*-
"""补 2010 年 5 个题型文件 frontmatter + 重新生成英语真题精读总目录（纳入 2010/2020 其他题型）"""
import os, re, datetime

def mtime_date(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')

# ---------- 1. 补 2010 年题型文件 FM ----------
types_2010 = ['完形填空', '新题型', '翻译', '大作文', '小作文']
done = 0
for t in types_2010:
    p = f'英语/英语二真题精读/2010/{t}.md'
    with open(p, encoding='utf-8') as f:
        text = f.read()
    if text.lstrip().startswith('---\n'):
        print('  跳过(已有FM):', p)
        continue
    d = mtime_date(p)
    lines = [
        f'title: 英语二 2010 {t}',
        'type: source-summary',
        'domain: 英语',
        'subject: 英语二',
        'topic: 真题精读',
        f'created: {d}',
        f'updated: {d}',
        f'tags: [英语二, 真题精读, 2010, {t}]',
    ]
    body = text.lstrip('\n')
    fm = '---\n' + '\n'.join(lines) + '\n---\n\n'
    with open(p, 'w', encoding='utf-8') as f:
        f.write(fm + body)
    print('  补FM:', p)
    done += 1
print(f'共补 {done} 个 2010 题型 FM')

# ---------- 2. 重新生成英语真题精读总目录 ----------
en_dir = '英语/英语二真题精读'
years = sorted([d for d in os.listdir(en_dir) if os.path.isdir(os.path.join(en_dir, d))],
               key=lambda x: int(x))

# 阅读 Text 文件
text_rows = []
other_rows = []
for y in years:
    fs = sorted(os.listdir(os.path.join(en_dir, y)))
    text_files = [f for f in fs if re.search(r'[Tt]ext\s*\d+', f)]
    other_files = [f for f in fs if not re.search(r'[Tt]ext\s*\d+', f) and f.endswith('.md')]
    if text_files:
        def key(f):
            m = re.search(r'[Tt]ext\s*(\d+)', f)
            return int(m.group(1)) if m else 0
        text_files = sorted(text_files, key=key)
        cells = []
        for f in text_files:
            base = os.path.splitext(f)[0]
            cells.append(f'[[{en_dir}/{y}/{base}]]')
        text_rows.append((y, cells))
    if other_files:
        others = []
        for f in other_files:
            base = os.path.splitext(f)[0]
            others.append(f'[[{en_dir}/{y}/{base}]]')
        other_rows.append((y, others))

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
lines.append('> 阅读 Part A 每年 4 篇（Text1-4）；2010、2020 两年另含完形填空、新题型、翻译、大小作文。')
lines.append('')
lines.append('## 阅读 Part A（每年 4 篇）')
lines.append('')
lines.append('| 年份 | Text1 | Text2 | Text3 | Text4 |')
lines.append('|------|-------|-------|-------|-------|')
for y, cells in text_rows:
    lines.append(f'| {y} | ' + ' | '.join(cells) + ' |')
lines.append('')
if other_rows:
    lines.append('## 其他题型（完形 / 新题型 / 翻译 / 大小作文）')
    lines.append('')
    for y, others in other_rows:
        lines.append(f'### {y}')
        lines.append('')
        for o in others:
            lines.append(f'- {o}')
        lines.append('')
lines.append('## See Also')
lines.append('- [[英语/历年真题]]')
lines.append('- [[英语/英语考情分析]]')
lines.append('')

with open(os.path.join(en_dir, '00-真题精读总目录.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('重新生成英语总目录：阅读', sum(len(r[1]) for r in text_rows), '篇 + 其他', sum(len(r[1]) for r in other_rows), '篇')
