#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 408考情分析.md 补齐 2009/2010/2026 行，并从各年答案与解析.md 提取选择题答案串。"""
import os
import re

base = r'd:\files\个人文件\22408_Notebook\408\历年真题'
kaoqing = r'd:\files\个人文件\22408_Notebook\408\408考情分析.md'


def extract_choice_ans(year: int) -> str:
    """从 {year}/答案与解析.md 提取 40 道选择题答案，返回 '1.B 2.C ...' 格式。"""
    f = os.path.join(base, str(year), '答案与解析.md')
    if not os.path.exists(f):
        return '详见文件'
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    # 找 "## 一、选择题答案速查表" 段
    start = content.find('## 一、选择题答案速查表')
    end = content.find('## 二、综合题')
    if start < 0 or end < 0:
        return '详见文件'
    table = content[start:end]
    # 第一张表是 1-10 题
    # 答案行格式：| 答案 | **B** | **C** | ...
    ans_rows = re.findall(r'\|\s*答案\s*\|(.+)\|', table)
    if not ans_rows:
        return '详见文件'
    answers = []
    for row in ans_rows:
        cells = re.findall(r'\*\*([A-D])\*\*', row)
        answers.extend(cells)
    if len(answers) != 40:
        return '详见文件'
    return ' '.join(f'{i+1}.{a}' for i, a in enumerate(answers))


with open(kaoqing, 'r', encoding='utf-8') as f:
    content = f.read()

# 在 "| 2011 |" 行后插入 "| 2010 |" 和 "| 2009 |"
ans_2010 = extract_choice_ans(2010)
ans_2009 = extract_choice_ans(2009)
ans_2026 = extract_choice_ans(2026)

# 找 2011 行
line_2011 = '| 2011 | [[408/历年真题/2011/答案与解析]] | 详见文件 | 二叉树算法、图/排序综合、Cache计算、CPU指令执行、PV同步、页面置换、TCP拥塞控制 |'
new_lines = line_2011 + '\n'
new_lines += f'| 2010 | [[408/历年真题/2010/答案与解析]] | {ans_2010} | 二叉树算法、图应用、Cache+虚拟存储、CPU数据通路、PV同步、页面置换、TCP拥塞控制 |\n'
new_lines += f'| 2009 | [[408/历年真题/2009/答案与解析]] | {ans_2009} | 单链表算法、图应用、Cache计算、CPU指令执行、PV同步、页面置换、TCP拥塞控制 |'

content = content.replace(line_2011, new_lines)

# 在 "| 2025 |" 行前插入 "| 2026 |"
line_2025_prefix = '| 2025 | [[408/历年真题/2025/答案与解析]]'
if line_2025_prefix in content:
    line_2026 = f'| 2026 | [[408/历年真题/2026/答案与解析]] | {ans_2026} | 见解析文件 |\n'
    content = content.replace(line_2025_prefix, line_2026 + line_2025_prefix)

with open(kaoqing, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'2009 选择题: {ans_2009[:60]}...')
print(f'2010 选择题: {ans_2010[:60]}...')
print(f'2026 选择题: {ans_2026[:60]}...')
print('已写入 408考情分析.md')
