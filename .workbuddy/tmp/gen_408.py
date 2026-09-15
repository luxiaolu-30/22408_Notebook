# -*- coding: utf-8 -*-
"""
生成 408/真题精读/真题做题记录表.md
逐年一张表：题号 | 科目 | 章节（考点） | 做题时间 | 难度 | 正确答案 | 错选了啥
数据源：408/真题精读/{年份}/{科目}.md
"""
import os
import re
from collections import Counter

ROOT = r"D:\files\个人文件\22408_Notebook\408\真题精读"
OUT = os.path.join(ROOT, "真题做题记录表.md")
TODAY = "2026-09-14"

SUBJECTS = ["数据结构", "计算机组成原理", "操作系统", "计算机网络"]
HEAD = re.compile(r"^###\s+(\d+)\.\s*（\s*(\d+)\s*分\s*·\s*([^）]*?)）\s*$", re.M)
ANS_CHOICE = re.compile(r"^\*\*答案\*\*：\s*([A-D])\b", re.M)


def split_sections(text):
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    choice = comp = ""
    for p in re.split(r"^##\s+", text, flags=re.M):
        if p.startswith("一、单项选择题"):
            choice = p
        elif p.startswith("二、综合应用题"):
            comp = p
    return choice, comp


def parse(block, kind):
    """返回 [(num, score, chapter, answer)]"""
    out = []
    marks = list(HEAD.finditer(block))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(block)
        body = block[m.end():end]
        a = ANS_CHOICE.search(body)
        out.append((int(m.group(1)), int(m.group(2)), m.group(3).strip(),
                    a.group(1) if (kind == "choice" and a) else "—"))
    return out


def main():
    years = sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d))
    blocks, stat, problems = [], Counter(), []

    for y in years:
        qs = []
        for subj in SUBJECTS:
            fp = os.path.join(ROOT, y, subj + ".md")
            if not os.path.exists(fp):
                problems.append(f"{y} 缺 {subj}")
                continue
            text = open(fp, encoding="utf-8").read()
            choice, comp = split_sections(text)
            if not choice:
                problems.append(f"{y} {subj} 缺「一、单项选择题」段")
            if not comp:
                problems.append(f"{y} {subj} 缺「二、综合应用题」段")
            for n, s, ch, a in parse(choice, "choice"):
                qs.append({"num": n, "score": s, "ch": ch, "ans": a, "subj": subj, "kind": "choice"})
            for n, s, ch, a in parse(comp, "comp"):
                qs.append({"num": n, "score": s, "ch": ch, "ans": a, "subj": subj, "kind": "comp"})

        qs.sort(key=lambda q: q["num"])
        if [q["num"] for q in qs] != list(range(1, len(qs) + 1)):
            problems.append(f"{y} 题号不连续：{[q['num'] for q in qs]}")

        blocks.append((y, qs))
        for q in qs:
            stat[q["subj"]] += 1
            if q["ans"] == "—" and q["kind"] == "choice":
                problems.append(f"{y} {q['subj']} {q['num']} 选择题缺答案")

    # ---------- 输出 ----------
    L = []
    L.append("---")
    L.append("title: 408 真题做题记录表")
    L.append("type: synthesis")
    L.append("domain: 408")
    L.append("created: " + TODAY)
    L.append("updated: " + TODAY)
    L.append('tags: ["408", 真题, 做题记录, "刷题"]')
    L.append("---")
    L.append("")
    L.append("# 408 真题做题记录表")
    L.append("")
    L.append("> 2009-2026 年 408 统考真题逐题记录表，**按年份分表**，共 18 套 × 47 题 = 846 行。")
    L.append("> **已预填**：题号、科目、章节（考点）、正确答案（仅选择题）。**做题后自己填**：做题时间、难度、错选了啥。")
    L.append("")
    L.append("| 列 | 怎么填 |")
    L.append("|----|--------|")
    L.append("| 题号 | 科目 + 原卷题号（如 `数据结构 26题`、`操作系统 45题`） |")
    L.append("| 科目 | 数据结构 1-11 / 41-42｜组成原理 12-22 / 43-44｜操作系统 23-32 / 45-46｜计算机网络 33-40 / 47 |")
    L.append("| 章节（考点） | 取自精读页题头标注，如 `树与二叉树`、`存储系统`、`进程与线程` — 大题同此列 |")
    L.append("| 做题时间 | 该题耗时，如 `3'10\"` |")
    L.append("| 难度 | ⭐~⭐⭐⭐⭐，或写「易 / 中 / 难」 |")
    L.append("| 正确答案 | 选择题已预填选项字母；综合应用题（41-47）为 `—`，主观作答后对着 [[408/真题精读/真题精读总目录|精读页]] 自评 |")
    L.append("| 错选了啥 | 填选错的选项字母，如 `C`；做对留空；大题可写失分点 |")
    L.append("")
    L.append("> 全卷结构（150 分）：单项选择题 1-40（每题 2 分，共 80 分）｜综合应用题 41-47（共 70 分）")
    L.append(">")
    L.append("> 建议节奏：选择 60-70 分钟｜综合 95-105 分钟｜检查 10-15 分钟（详见 [[408考情分析]]）")
    L.append(">")
    L.append("> 用法建议：做完一套回看本表，把「错选了啥」按**科目**和**章节**两个维度汇总，定位反复丢分的高频章节。")
    L.append(">")
    L.append("> 配套：题目见 [[408/历年真题/刷题纯净版/刷题纯净版总目录]]（纯题面整卷），答案与解析见 [[408/真题精读/真题精读总目录]]。")
    L.append("")
    L.append("---")
    L.append("")

    for y, qs in blocks:
        ch_n = sum(1 for q in qs if q["kind"] == "choice")
        cp_n = len(qs) - ch_n
        ch_s = sum(q["score"] for q in qs if q["kind"] == "choice")
        cp_s = sum(q["score"] for q in qs if q["kind"] == "comp")
        L.append(f"## {y} 年")
        L.append("")
        L.append(f"> 选择题 {ch_n} 题（{ch_s} 分）｜综合应用题 {cp_n} 题（{cp_s} 分）")
        L.append("")
        L.append("| 题号 | 科目 | 章节（考点） | 做题时间 | 难度 | 正确答案 | 错选了啥 |")
        L.append("|------|------|------------|---------|------|---------|---------|")
        for q in qs:
            L.append("| " + " | ".join([
                f"{q['subj']} {q['num']}题", q["subj"], q["ch"], "", "", q["ans"], "",
            ]) + " |")
        L.append("")

    L.append("---")
    L.append("")
    L.append("## See Also")
    L.append("")
    L.append("- [[408/真题精读/真题精读总目录]] — 全文精读（题干 + 选项 + 答案 + 解析 + 原图，按四科拆分）")
    L.append("- [[408/历年真题/刷题纯净版/刷题纯净版总目录]] — 纯题面整卷（用来做题）")
    L.append("- [[408考情分析]] — 试卷构成、分值占比、建议做题时间")
    L.append("- [[408/408总目录]]")
    L.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print("写出：", OUT)
    print("科目题量：", dict(stat))
    print("总行数：", sum(len(q) for _, q in blocks))
    print("数据问题：", problems if problems else "无")


if __name__ == "__main__":
    main()
