#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新 408考情分析.md 中的真题链接，从 408真题考点分析/YYYY 改为 YYYY/答案与解析。"""
import re

path = r'd:\files\个人文件\22408_Notebook\408\408考情分析.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 [[408/历年真题/408真题考点分析/YYYY]] 为 [[408/历年真题/YYYY/答案与解析]]
content = re.sub(
    r'\[\[408/历年真题/408真题考点分析/(\d{4})\]\]',
    r'[[408/历年真题/\1/答案与解析]]',
    content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证
import re
matches = re.findall(r'\[\[408/历年真题/(\d{4})/答案与解析\]\]', content)
print(f'已更新 {len(matches)} 条链接')
print('年份:', sorted(matches))
