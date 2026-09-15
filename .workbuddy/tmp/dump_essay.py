# -*- coding: utf-8 -*-
"""提取各年 大作文「图表描述/题目」与 小作文「题目」，用于判定作文题材/文体。"""
import os
import re

ROOT = r"D:\files\个人文件\22408_Notebook\英语二\英语二真题精读"
years = sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d))


def sect(y, f, name, n=260):
    t = open(os.path.join(ROOT, y, f + ".md"), encoding="utf-8").read()
    m = re.search(r"##\s*" + name + r"\s*\n(.{0,900}?)(?=\n##|\Z)", t, re.S)
    if not m:
        return "【无】"
    s = re.sub(r"\s+", " ", m.group(1)).strip()
    return s[:n]


for y in years:
    print("==", y)
    print("   [大作文-图表描述]", sect(y, "大作文", "图表描述", 200))
    print("   [大作文-题目]", sect(y, "大作文", "题目", 200))
    print("   [小作文-题目]", sect(y, "小作文", "题目", 220))
