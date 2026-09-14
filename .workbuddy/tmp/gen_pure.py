# -*- coding: utf-8 -*-
"""
从 408/真题精读/ 提取「只有题目」的刷题纯净版。
输入：408/真题精读/{year}/{科目}.md
输出：408/历年真题/刷题纯净版/{year}.md（按原卷题号 1-47 排好，仅题干+选项+图片）
"""
import os
import re
import json
from collections import defaultdict

ROOT = r"D:\files\个人文件\22408_Notebook"
SRC = os.path.join(ROOT, "408", "真题精读")
OUT = os.path.join(ROOT, "408", "历年真题", "刷题纯净版")
TODAY = "2026-09-14"

SUBJECTS = ["数据结构", "计算机组成原理", "操作系统", "计算机网络"]

HEAD = re.compile(r"^###\s+(\d+)\.\s*（\s*(\d+)\s*分[^）]*）\s*$")
OPT = re.compile(r"^- \*\*([A-D])\.\*\*\s*(.*)$")
KEYS = ["A", "B", "C", "D"]


def split_sections(text):
    """返回 (选择题块, 综合题块)"""
    # 去掉 frontmatter
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    parts = re.split(r"^##\s+", text, flags=re.M)
    choice, comp = "", ""
    for p in parts:
        if p.startswith("一、单项选择题"):
            choice = p
        elif p.startswith("二、综合应用题"):
            comp = p
    return choice, comp


def parse_block(block):
    """把 '一、单项选择题\n\n### 1. ...' 拆成 [ {num, score, stem, options} ]"""
    qs = []
    lines = block.split("\n")
    # 定位所有题号行
    marks = [(i, m) for i, ln in enumerate(lines) for m in [HEAD.match(ln)] if m]
    for k, (i, m) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        body = lines[i + 1:end]
        qs.append({"num": int(m.group(1)), "score": int(m.group(2)), "body": body})
    return qs


def clean_choice(body):
    """选择题：正文 → (题干, 选项列表)"""
    opts = []
    stem_lines = []
    started = False
    for ln in body:
        m = OPT.match(ln)
        if m and len(opts) < 4 and m.group(1) == KEYS[len(opts)]:
            started = True
            opts.append((m.group(1), m.group(2).strip()))
            continue
        if not started:
            stem_lines.append(ln)
    return trim(stem_lines), opts


def clean_comp(body):
    """综合题：截到 '**答案 / 解析**' 之前"""
    cut = []
    for ln in body:
        if ln.strip().startswith("**答案") and "解析" in ln:
            break
        cut.append(ln)
    return trim(cut), []


def trim(lines):
    """去掉首尾空行与分隔线"""
    while lines and lines[0].strip() in ("", "---"):
        lines.pop(0)
    while lines and lines[-1].strip() in ("", "---"):
        lines.pop()
    return "\n".join(lines)


def fix_img(text, year):
    return re.sub(r"\(images/", f"(../../真题精读/{year}/images/", text)


years = sorted(d for d in os.listdir(SRC) if re.fullmatch(r"\d{4}", d))
os.makedirs(OUT, exist_ok=True)

report = []
for y in years:
    allq = []
    for subj in SUBJECTS:
        fp = os.path.join(SRC, y, subj + ".md")
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        choice, comp = split_sections(text)
        for q in parse_block(choice):
            stem, opts = clean_choice(q["body"])
            allq.append(dict(q, kind="choice", stem=stem, options=opts, subj=subj))
        for q in parse_block(comp):
            stem, opts = clean_comp(q["body"])
            allq.append(dict(q, kind="comp", stem=stem, options=opts, subj=subj))

    allq.sort(key=lambda q: q["num"])

    choice = [q for q in allq if q["kind"] == "choice"]
    comp = [q for q in allq if q["kind"] == "comp"]

    L = []
    L.append("---")
    L.append(f"title: {y} 年 408 真题 · 刷题纯净版")
    L.append("type: source")
    L.append("domain: 408")
    L.append("topic: 刷题纯净版")
    L.append(f"year: {y}")
    L.append(f"created: {TODAY}")
    L.append(f"updated: {TODAY}")
    L.append(f'tags: ["408", 刷题, "真题", "{y}"]')
    L.append("---")
    L.append("")
    L.append(f"# {y} 年 408 真题 · 刷题纯净版")
    L.append("")
    L.append(f"> 共 {len(allq)} 题（选择 {len(choice)} 题 + 综合 {len(comp)} 题）。仅题干与选项，不含答案。")
    L.append(f"> 对答案：[[408/真题精读/{y}/数据结构]] 等四科精读页。")
    L.append("")

    if choice:
        L.append(f"## 一、单项选择题（{len(choice)} 题，每题 2 分，共 {len(choice) * 2} 分）")
        L.append("")
        for q in choice:
            L.append(f"### {q['num']}.")
            L.append("")
            L.append(fix_img(q["stem"], y))
            L.append("")
            for k, t in q["options"]:
                L.append(f"- **{k}.** {t}")
            L.append("")
            L.append("---")
            L.append("")

    if comp:
        tot = sum(q["score"] for q in comp)
        L.append(f"## 二、综合应用题（{len(comp)} 题，共 {tot} 分）")
        L.append("")
        for q in comp:
            L.append(f"### {q['num']}. （{q['score']} 分）")
            L.append("")
            L.append(fix_img(q["stem"], y))
            L.append("")
            L.append("---")
            L.append("")

    L.append("## See Also")
    L.append("")
    L.append(f"- [[408/真题精读/真题精读总目录]]")
    L.append(f"- [[408/历年真题/历年真题总目录]]")
    L.append(f"- [[408/历年真题/{y}]]")
    L.append("")

    with open(os.path.join(OUT, f"{y}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    report.append({
        "year": y,
        "total": len(allq),
        "choice": len(choice),
        "comp": len(comp),
        "empty_stem": sum(1 for q in allq if not q["stem"].strip()),
        "nums": [q["num"] for q in allq],
    })

# 校验：题号连续 1..N 且无重复
bad = []
for r in report:
    ns = r["nums"]
    if ns != list(range(1, len(ns) + 1)):
        bad.append((r["year"], ns))

print(json.dumps(report, ensure_ascii=False, indent=1))
print("题号异常年份：", bad if bad else "无（全部 1..47 连续）")
