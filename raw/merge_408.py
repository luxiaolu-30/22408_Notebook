# -*- coding: utf-8 -*-
"""合并 408 四个重叠文件为两个：考点总目录(00+06) + 历年真题(真题+考情)"""
import os, re, datetime

TODAY = datetime.datetime.now().strftime('%Y-%m-%d')

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

c00 = read('408/00-408考点总目录.md')
c06 = read('408/06-408考点全清单.md')
czj = read('408/408历年真题.md')
ckq = read('408/408考情分析.md')

# ============ 文件 A：00 + 06 -> 408/00-408考点总目录.md ============
# 主体用 06（完整清单），插入 00 的分科导航，改 title，去重

# 提取 00 的分科考点文档导航（## 📚 分科考点文档 到 下一个 ## 之前）
m = re.search(r'## 📚 分科考点文档.*?(?=\n## )', c00, re.S)
nav = m.group(0).strip() if m else ''

# 改 06 的 frontmatter title
cA = re.sub(r'^title: .*$', 'title: 408 考点总目录与全清单', c06, count=1, flags=re.M)
cA = re.sub(r'^updated: .*$', f'updated: {TODAY}', cA, count=1, flags=re.M)

# 在 "## 一、数据结构" 前插入分科导航
nav_block = '\n---\n\n' + nav + '\n'
cA = cA.replace('## 一、数据结构（45 分）', nav_block + '## 一、数据结构（45 分）', 1)

# 删除 See Also 里指向 00 的链接（00 已并入本文件）
cA = re.sub(r'- \[\[00-408考点总目录\]\][^\n]*\n', '', cA)

# 更新相关文档引用：06 的 self 引用（[[00-408考点总目录]] 已在 See Also 删了，正文里还有 [[00-408考点总目录]] | [[408历年真题]]）
cA = cA.replace('**相关文档**：[[00-408考点总目录]] | [[408历年真题]]', '**相关文档**：[[408历年真题]]')

with open('408/00-408考点总目录.md', 'w', encoding='utf-8') as f:
    f.write(cA)
print('生成文件 A: 408/00-408考点总目录.md')

# ============ 文件 B：408历年真题 + 408考情分析 -> 408/408历年真题.md ============
# 主体用 408历年真题，开头插入 408考情分析 的考情速览，改 title，删 TOP20

# 提取 408考情分析 正文（# 标题 到 ## See Also 之前）
m = re.search(r'# 408 考情分析（可视化总览）.*?(?=\n## See Also)', ckq, re.S)
kq_body = m.group(0).strip() if m else ''

# 改 title
cB = re.sub(r'^title: .*$', 'title: 408 历年真题与考情分析', czj, count=1, flags=re.M)
cB = re.sub(r'^updated: .*$', f'updated: {TODAY}', cB, count=1, flags=re.M)

# 在 "## 一、考点总览统计表" 前插入考情速览
kq_block = '\n---\n\n' + kq_body + '\n'
cB = cB.replace('## 一、考点总览统计表（2011-2025）', kq_block + '## 一、考点总览统计表（2011-2025）', 1)

# 删除 3.1 TOP20（重复，TOP20 在文件 A）
cB = re.sub(r'### 3\.1 必考知识点 TOP 20.*?(?=### 3\.2 )', '', cB, flags=re.S)

# 修正 3.2 标题（删掉 3.1 后，3.2 改为 3.1 或保留）
cB = cB.replace('### 3.2 各科目考点分布热力图', '### 3.1 各科目考点分布热力图', 1)

# 更新 See Also：加入 408考情分析 特有的链接（wiki/408高频考点分析）
cB = cB.replace('- [[wiki/408真题考点分析-跨年份汇总]] — 2022-2025 真题考点频率+命题趋势',
                '- [[wiki/408真题考点分析-跨年份汇总]] — 2022-2025 真题考点频率+命题趋势\n- [[wiki/408高频考点分析_2016-2025]] — 近 10 年大题考点年份对照')

with open('408/408历年真题.md', 'w', encoding='utf-8') as f:
    f.write(cB)
print('生成文件 B: 408/408历年真题.md')

# ============ 删除旧文件 ============
for p in ['408/06-408考点全清单.md', '408/408考情分析.md']:
    if os.path.exists(p):
        os.remove(p)
        print('删除:', p)
