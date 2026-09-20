#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为数学二生成真题做题记录表。

从「数学二/历年真题/{year}/答案与解析.md」提取每题正确答案，
生成「数学二/历年真题/数学二真题做题记录表.md」。
"""
import os
import re

base_zhenti = r'd:\files\个人文件\22408_Notebook\数学二\历年真题'
out_path = os.path.join(base_zhenti, '数学二真题做题记录表.md')


def read_file(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_answers(year):
    """从答案与解析.md 提取每题答案。返回 dict: {题号: 答案}"""
    path = os.path.join(base_zhenti, str(year), '答案与解析.md')
    content = read_file(path)
    if not content:
        return {}
    answers = {}

    # 1. 优先从「## 答案速查」表段提取（2018/2025 风格）
    quick_match = re.search(
        r'##\s*答案速查\s*\n(.*?)(?=\n---\s*\n|\n##\s|\Z)',
        content, re.DOTALL)
    if quick_match:
        block = quick_match.group(1)
        lines = [l.strip() for l in block.split('\n') if '|' in l]
        # 跳过分隔行 |---|---|
        data_lines = [l for l in lines if not re.match(r'^\|[\s:-]+\|$', l)]
        # 找包含 A/B/C/D 的数据行
        for l in data_lines:
            cells = [c.strip() for c in l.split('|')][1:-1]
            if not cells:
                continue
            # 行内只要有一个 cell 首字母是 A/B/C/D 就当作答案行
            if any(re.match(r'\b[ABCD]\b', c) for c in cells):
                for i, c in enumerate(cells):
                    m = re.match(r'\b([ABCD])\b', c)
                    if m and (i + 1) not in answers:
                        answers[i + 1] = m.group(1)

    # 2. 如果速查段提取不全，按「题号 → 下一个答案」配对方式补齐
    # 避免跨题段匹配造成错位
    if len(answers) < 16:
        body = content
        if quick_match:
            body = content[:quick_match.start()] + content[quick_match.end():]

        # 找所有题号标记位置：**1.** 或 **(1)** 或 **（1）**
        # 题号 N 后到下一个题号标记之间，找第一个「答案：X」（X 是 ABCD 才算）
        qmarks = list(re.finditer(
            r'\*\*(?:[（(]\s*(\d+)\s*[）)]|(\d+)\.?)\*\*', body))
        amarks = list(re.finditer(
            r'答案[：:]\s*\*{0,2}\s*([ABCD])\b', body))

        # 对每个题号标记，找其后第一个答案标记（在下个题号标记之前）
        for i, qm in enumerate(qmarks):
            qnum = int(qm.group(1) or qm.group(2))
            qpos = qm.end()
            # 下一个题号标记位置
            next_qpos = qmarks[i + 1].start() if i + 1 < len(qmarks) else len(body)
            # 在 (qpos, next_qpos) 范围内找第一个 ABCD 答案
            for am in amarks:
                if qpos < am.start() < next_qpos:
                    ans = am.group(1)
                    if qnum not in answers:
                        answers[qnum] = ans
                    break

    return answers


def get_knowledge_point(year, qnum, qtype):
    """根据题号 + 题型返回考点（占位，可后续完善）。"""
    if qtype == '选择':
        # 1-10 选择题
        kp_map = {
            1: '极限/等价无穷小',
            2: '导数应用/极值拐点',
            3: '微分方程',
            4: '无穷小比较',
            5: '二重积分换序',
            6: '定积分应用',
            7: '线代-矩阵/行列式',
            8: '线代-向量组',
            9: '线代-线性方程组',
            10: '线代-特征值/相似',
        }
        return kp_map.get(qnum, '')
    if qtype == '填空':
        kp_map = {
            11: '极限计算',
            12: '导数/微分',
            13: '不定积分/定积分',
            14: '多元函数微分',
            15: '微分方程/线代',
            16: '线代',
        }
        return kp_map.get(qnum, '')
    if qtype == '解答':
        kp_map = {
            17: '极限/定积分计算',
            18: '导数应用/中值定理',
            19: '多元函数极值/二重积分',
            20: '定积分应用/微分方程',
            21: '线代-方程组/矩阵',
            22: '线代-特征值/二次型',
        }
        return kp_map.get(qnum, '')
    return ''


def generate():
    years = list(range(2006, 2026))
    years_data = {}
    for y in years:
        ans = extract_answers(y)
        years_data[y] = ans
        print(f'{y} 年：提取到 {len(ans)} 个客观题答案')

    # 生成表格
    # 数学二结构：
    # - 2006-2008 旧结构：填空(1-6)+选择(7-14)+解答(15-23)
    # - 2009-今 新结构：选择(1-10)+填空(11-16)+解答(17-22)
    # 但我们统一用 1-22 题号；答案顺序按「选择→填空→解答」排列
    # 旧年份结构不同时按实际编排

    out = []
    out.append("""---
title: 数学二真题做题记录表
type: synthesis
domain: 数学
subject: 数学二
created: 2026-09-18
updated: 2026-09-18
tags: [数学二, 真题, 做题记录, "刷题"]
---

# 数学二真题做题记录表

> 2006-2025 年数学二真题逐题记录表，**按年份分表**，共 20 套 × 22 题 = 440 行。
> **已预填**：题号、题目类型、考点、正确答案（客观题）。**做题后自己填**：做题时间、难度、错因。

| 列 | 怎么填 |
|----|--------|
| 题号 | 题型 + 原卷题号（如 `选择 3 题`） |
| 题目类型 | 选择 / 填空 / 解答 |
| 考点 | 该题涉及的知识点（预填为常见考点，可自行修正） |
| 做题时间 | 该题耗时，如 `4'30"` |
| 难度 | ⭐~⭐⭐⭐，或写「易 / 中 / 难」 |
| 正确答案 | 客观题已预填；解答题留空（看 [[答案与解析]]） |
| 错因 | 填错因分类：`计算失误`/`思路错`/`知识点盲区`/`审题错`，做对留空 |

> 全卷结构（150 分）：选择 1-10（50 分）｜填空 11-16（30 分）｜解答 17-22（70 分）
> 注：2006-2008 为旧题型结构（填空 1-6 + 选择 7-14 + 解答 15-23，分值不同），表内仍按当年题号顺序记录。
>
> 建议节奏：选择 40 分钟｜填空 30 分钟｜解答 100 分钟（详见 [[数学考情分析]]）
>
> 用法建议：做完一套回看本表，把「错因」按**题型**和**考点**两个维度汇总，就能看出自己到底是哪类题型、哪个考点稳定丢分。

""")
    # 加分割线
    out.append("---\n\n")

    # 各年表格
    for y in years:
        out.append(f'## {y} 年\n\n')
        ans = years_data[y]
        out.append('| 题号 | 题目类型 | 考点 | 做题时间 | 难度 | 正确答案 | 错因 |')
        out.append('\n|------|---------|------|---------|------|---------|------|\n')

        # 确定该年题型分布
        if y <= 2020:
            # 旧题型（2006-2020）：填空1-6, 选择7-14, 解答15-23
            qtypes = ([(i, '填空') for i in range(1, 7)] +
                      [(i, '选择') for i in range(7, 15)] +
                      [(i, '解答') for i in range(15, 24)])
        else:
            # 新题型（2021-2025）：选择1-10, 填空11-16, 解答17-22
            qtypes = ([(i, '选择') for i in range(1, 11)] +
                      [(i, '填空') for i in range(11, 17)] +
                      [(i, '解答') for i in range(17, 23)])

        for qnum, qtype in qtypes:
            kp = get_knowledge_point(y, qnum, qtype)
            answer = ans.get(qnum, '')
            if qtype == '解答':
                answer_str = '（见解析）'
            else:
                answer_str = answer if answer else ''
            out.append(
                f'| {qtype} {qnum}题 | {qtype} | {kp} |  |  | {answer_str} |  |\n')
        out.append('\n')

        # See Also 链接到该年真题
        out.append(f'> 对答案与看解析：[[{y}/答案与解析]] · 刷题面：[[{y}/题面]]\n\n')

    # 末尾汇总
    out.append("""---

## See Also

- [[数学二历年真题总目录]] — 历年真题总目录
- [[数学考情分析]] — 试卷构成与逐年考点统计
- [[数学备考规划与资料推荐]] — 三阶段规划与资料推荐
""")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(out))
    print(f'\n生成 → {out_path}')
    total_lines = sum(1 for _ in open(out_path, encoding='utf-8'))
    print(f'共 {total_lines} 行')


if __name__ == '__main__':
    generate()
