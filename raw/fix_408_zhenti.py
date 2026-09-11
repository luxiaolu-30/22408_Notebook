# -*- coding: utf-8 -*-
"""补 408/历年真题 的 created/updated + 生成 00-总目录索引"""
import os, re, datetime

def mtime_date(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')

zj_dir = '408/历年真题'

# 1. 补 created/updated
done = 0
for fn in sorted(os.listdir(zj_dir)):
    if not fn.endswith('.md') or fn.startswith('00-'):
        continue
    p = os.path.join(zj_dir, fn)
    with open(p, encoding='utf-8') as f:
        text = f.read()
    if re.search(r'^created:', text, re.M):
        continue
    d = mtime_date(p)
    if re.search(r'^tags:', text, re.M):
        text = re.sub(r'^(tags:)', f'created: {d}\nupdated: {d}\n\\1', text, count=1, flags=re.M)
    else:
        text = re.sub(r'\n---\n', f'\ncreated: {d}\nupdated: {d}\n---\n', text, count=1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print('补 created/updated:', p)
    done += 1
print(f'共补 {done} 个')

# 2. 生成 00-总目录
years = sorted([os.path.splitext(fn)[0] for fn in os.listdir(zj_dir)
                if fn.endswith('.md') and not fn.startswith('00-')], key=lambda x: int(x))
lines = []
lines.append('---')
lines.append('title: 408 历年真题 · 总目录')
lines.append('type: synthesis')
lines.append('domain: 408')
lines.append('created: 2026-09-11')
lines.append('updated: 2026-09-11')
lines.append('tags: [考研, 408, 真题, 索引]')
lines.append('---')
lines.append('')
lines.append('# 408 历年真题 · 总目录')
lines.append('')
lines.append('> 历年 408 计算机统考真题逐年考点分析（选择题分布 + 大题考点）。')
lines.append('')
lines.append('| 年份 | 页面 |')
lines.append('|------|------|')
for y in years:
    lines.append(f'| {y} | [[{zj_dir}/{y}]] |')
lines.append('')
lines.append('## See Also')
lines.append('- [[408/408历年真题]]')
lines.append('- [[408/00-408考点总目录]]')
lines.append('')

with open(os.path.join(zj_dir, '00-总目录.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('生成 408/历年真题/00-总目录.md，共', len(years), '年')
