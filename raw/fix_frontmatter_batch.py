# -*- coding: utf-8 -*-
"""批量补 frontmatter：英语真题精读 64 篇 + 408/06 + 408强化 + 择校（幂等，跳过已有）"""
import os, glob, re, datetime

def mtime_date(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')

def has_frontmatter(text):
    return text.lstrip().startswith('---\n')

def add_frontmatter(path, fm_lines):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if has_frontmatter(text):
        print('  跳过(已有FM):', path)
        return False
    body = text.lstrip('\n')
    fm = '---\n' + '\n'.join(fm_lines) + '\n---\n\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fm + body)
    print('  补FM:', path)
    return True

done = 0

# 1) 英语真题精读 64 篇
for path in sorted(glob.glob('英语/英语二真题精读/**/*.md', recursive=True)):
    parts = path.replace('\\', '/').split('/')
    year = parts[2]
    fname = parts[3]
    m = re.search(r'[Tt]ext\s*(\d+)', fname)
    n = m.group(1) if m else '?'
    title = f'英语二 {year} Text{n}'
    d = mtime_date(path)
    lines = [
        f'title: {title}',
        'type: source-summary',
        'domain: 英语',
        'subject: 英语二',
        'topic: 真题精读',
        f'created: {d}',
        f'updated: {d}',
        f'tags: [英语二, 真题精读, {year}, Text{n}]',
    ]
    if add_frontmatter(path, lines):
        done += 1

# 2) 408/06-408考点全清单
d = mtime_date('408/06-408考点全清单.md')
done += add_frontmatter('408/06-408考点全清单.md', [
    'title: 408 考点全清单',
    'type: concept',
    'domain: 408',
    f'created: {d}',
    f'updated: {d}',
    'tags: [408, 考点, 必考, 清单]',
])

# 3) 408强化.md
d = mtime_date('408强化.md')
done += add_frontmatter('408强化.md', [
    'title: 408 强化',
    'type: concept',
    'domain: 408',
    f'created: {d}',
    f'updated: {d}',
    'tags: [408, 强化, 复习方法]',
])

# 4) 择校.md
d = mtime_date('择校.md')
done += add_frontmatter('择校.md', [
    'title: 择校：全日制与学科代码',
    'type: comparison',
    f'created: {d}',
    f'updated: {d}',
    'tags: [考研, 择校, 全日制, 学科代码, 定向选调]',
])

print(f'共补 {done} 个 frontmatter')
