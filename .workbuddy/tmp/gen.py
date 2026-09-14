# -*- coding: utf-8 -*-
"""
从 postgraduate-exam-website 仓库提取 408 真题，生成「按四科拆分」的 Markdown 精读文件。
输出：408/真题精读/{年份}/{科目}.md + images/
"""
import json, os, shutil, re
from collections import defaultdict

REPO = r"D:\files\个人文件\22408_Notebook\.workbuddy\tmp\exam_repo\client\public\exams"
OUT = r"D:\files\个人文件\22408_Notebook\408\真题精读"
TODAY = "2026-09-14"

SUBJECTS = [
    ("ds", "数据结构"),
    ("co", "计算机组成原理"),
    ("os", "操作系统"),
    ("cn", "计算机网络"),
]
SUBJ_NAME = dict(SUBJECTS)


def stars(n):
    try:
        n = int(n)
    except Exception:
        n = 0
    n = max(0, min(4, n))
    return "⭐" * n if n else "—"


def fix_img(text):
    """把 /exams/2024/images/xxx.webp 改成本地相对路径 images/xxx.webp"""
    if not text:
        return ""
    return re.sub(r"\(/exams/\d+/images/", "(images/", text)


def meta_line(q):
    parts = []
    if q.get("difficulty"):
        parts.append("难度 " + stars(q["difficulty"]))
    if q.get("chapterName"):
        parts.append("章节 " + q["chapterName"])
    if q.get("tags"):
        parts.append("标签 " + " / ".join(q["tags"]))
    return " ｜ ".join(parts)


years = sorted(os.listdir(REPO))
index_rows = []

for y in years:
    pj = os.path.join(REPO, y, "paper.json")
    if not os.path.exists(pj):
        continue
    with open(pj, encoding="utf-8") as f:
        data = json.load(f)
    qs = data["questions"]

    out_y = os.path.join(OUT, y)
    os.makedirs(out_y, exist_ok=True)

    # 复制图片
    src_imgs = os.path.join(REPO, y, "images")
    if os.path.isdir(src_imgs) and os.listdir(src_imgs):
        dst_imgs = os.path.join(out_y, "images")
        os.makedirs(dst_imgs, exist_ok=True)
        for fn in os.listdir(src_imgs):
            shutil.copy2(os.path.join(src_imgs, fn), os.path.join(dst_imgs, fn))

    by_subj = defaultdict(list)
    for q in qs:
        by_subj[q.get("subject")].append(q)

    row = {"year": y}

    for code, name in SUBJECTS:
        qlist = by_subj.get(code, [])
        if not qlist:
            continue
        choices = [q for q in qlist if q.get("questionType") == "choice"]
        comps = [q for q in qlist if q.get("questionType") == "comprehensive"]
        cscore = sum(q.get("score", 0) for q in choices)
        zscore = sum(q.get("score", 0) for q in comps)
        total = cscore + zscore

        L = []
        L.append("---")
        L.append(f"title: {y} 408 真题 · {name}")
        L.append("type: source-summary")
        L.append("domain: 408")
        L.append('subject: "408"')
        L.append("topic: 真题精读")
        L.append(f"year: {y}")
        L.append(f"created: {TODAY}")
        L.append(f"updated: {TODAY}")
        L.append(f'tags: ["408", 真题精读, "{y}", {name}]')
        L.append("---")
        L.append("")
        L.append(f"# {y} 408 真题 · {name}")
        L.append("")
        L.append(f"> 本科目共 {len(qlist)} 题 / {total} 分：单项选择题 {len(choices)} 题（{cscore} 分）+ 综合应用题 {len(comps)} 题（{zscore} 分）。")
        L.append("")

        if choices:
            L.append("## 一、单项选择题")
            L.append("")
            for q in choices:
                ch = q.get("chapterName", "")
                L.append(f"### {q.get('number')}. （{q.get('score')} 分 · {ch}）")
                L.append("")
                L.append(fix_img(q.get("stem", "").strip()))
                L.append("")
                for opt in q.get("options", []):
                    L.append(f"- **{opt.get('key')}.** {opt.get('text')}")
                L.append("")
                L.append(f"**答案**：{q.get('answer', '')}")
                L.append("")
                if q.get("explanation"):
                    L.append(f"**解析**：{fix_img(q.get('explanation', ''))}")
                    L.append("")
                m = meta_line(q)
                if m:
                    L.append("> " + m)
                    L.append("")
                L.append("---")
                L.append("")

        if comps:
            L.append("## 二、综合应用题")
            L.append("")
            for q in comps:
                ch = q.get("chapterName", "")
                L.append(f"### {q.get('number')}. （{q.get('score')} 分 · {ch}）")
                L.append("")
                L.append(fix_img(q.get("stem", "").strip()))
                L.append("")
                if q.get("subQuestions"):
                    descs = [sq.get("description", "") for sq in q["subQuestions"]]
                    stem_raw = q.get("stem", "")
                    if not all(d and d in stem_raw for d in descs):
                        L.append("**小题**：")
                        L.append("")
                        for sq in q["subQuestions"]:
                            tail = f"（{sq.get('score')} 分）" if sq.get("score") else ""
                            L.append(f"- （{sq.get('number')}）{sq.get('description', '')}{tail}")
                        L.append("")
                if q.get("explanation"):
                    L.append("**答案 / 解析**：")
                    L.append("")
                    L.append(fix_img(q.get("explanation", "")))
                    L.append("")
                m = meta_line(q)
                if m:
                    L.append("> " + m)
                    L.append("")
                L.append("---")
                L.append("")

        L.append("## See Also")
        L.append("")
        for c2, n2 in SUBJECTS:
            if c2 != code:
                L.append(f"- [[408/真题精读/{y}/{n2}]]")
        L.append(f"- [[408/历年真题/{y}]]")
        L.append("- [[408/真题精读/真题精读总目录]]")
        L.append("")

        with open(os.path.join(out_y, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L))

        row[name] = f"[[408/真题精读/{y}/{name}]]"

    index_rows.append(row)
    print("done", y, row)

# 总目录
idx = []
idx.append("---")
idx.append("title: 408 真题精读 · 总目录")
idx.append("type: synthesis")
idx.append("domain: 408")
idx.append(f"created: {TODAY}")
idx.append(f"updated: {TODAY}")
idx.append('tags: ["408", 真题, 精读, 索引]')
idx.append("---")
idx.append("")
idx.append("# 408 真题精读 · 总目录")
idx.append("")
idx.append("> 2009-2026 年 408 统考真题全文精读（题干 + 选项 + 答案 + 解析 + 原图），按四科拆分。")
idx.append("> 数据来源：开源项目 [408 简纲](https://github.com/liangbohan/postgraduate-exam-website)（CC BY 4.0）。")
idx.append("")
idx.append("| 年份 | 数据结构 | 计算机组成原理 | 操作系统 | 计算机网络 |")
idx.append("|------|---------|--------------|---------|-----------|")
for r in index_rows:
    cells = [r["year"]] + [r.get(n, "—") for _, n in SUBJECTS]
    idx.append("| " + " | ".join(cells) + " |")
idx.append("")
idx.append("## See Also")
idx.append("- [[408/历年真题/历年真题总目录]] — 逐年考点分析（表格速览）")
idx.append("- [[408考情分析]] — 试卷构成与高频考点")
idx.append("- [[408/408总目录]]")
idx.append("")

with open(os.path.join(OUT, "真题精读总目录.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(idx))

print("ALL DONE, years =", len(index_rows))
