# -*- coding: utf-8 -*-
"""提取各年 完形/翻译/新题型 原文开头 + 大小作文标题，用于人工判定文章题材。"""
import os
import re

ROOT = r"D:\files\个人文件\22408_Notebook\英语二\英语二真题精读"
years = sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d))


def orig(y, f, n=180):
    t = open(os.path.join(ROOT, y, f + ".md"), encoding="utf-8").read()
    t = re.sub(r"^---.*?---", "", t, flags=re.S)
    i = t.find("## 原文")
    seg = t[i + 5:] if i >= 0 else t
    seg = re.sub(r"#+[^\n]*", "", seg)
    seg = re.sub(r"\s+", " ", seg).strip()
    return seg[:n]


for f in ["完形填空", "翻译", "新题型"]:
    print("########", f)
    for y in years:
        print(" ", y, "|", orig(y, f))

print("######## 大作文 / 小作文 标题行")
for f in ["大作文", "小作文"]:
    print("----", f)
    for y in years:
        t = open(os.path.join(ROOT, y, f + ".md"), encoding="utf-8").read()
        hs = [l for l in t.split("\n") if l.startswith("#")][:6]
        print(" ", y, "|", " // ".join(h.strip() for h in hs)[:160])
