# -*- coding: utf-8 -*-
"""
生成 英语二/英语二真题精读/真题做题记录表.md
逐年一张表：题号 | 题目类型 | 做题时间 | 难度 | 正确答案 | 错选了啥
- 题号 / 题目类型 / 正确答案 由脚本预填；做题时间 / 难度 / 错选了啥 留空给用户
- 主观题（翻译 46 / 小作文 47 / 大作文 48）答案列留空
"""
import os
import re
import json
from collections import Counter

ROOT = r"D:\files\个人文件\22408_Notebook\英语二\英语二真题精读"
TMP = r"D:\files\个人文件\22408_Notebook\.workbuddy\tmp"
OUT = os.path.join(ROOT, "真题做题记录表.md")
TODAY = "2026-09-14"

TEXTS = ["Text1", "Text2", "Text3", "Text4"]
RANGES = {"Text1": (21, 25), "Text2": (26, 30), "Text3": (31, 35), "Text4": (36, 40)}

# 完形的衔接词（用于无解析年份兜底判定「逻辑衔接」）
CONNECTIVES = set("""
while because unless once however therefore thus moreover besides instead otherwise although though
since whether what which who whose that how why when where but and or so yet still also then hence
meanwhile nevertheless nonetheless accordingly consequently similarly likewise whereas despite
before after until till provided for as if nor else anyway anyhow indeed rather
fortunately unfortunately ironically surprisingly apparently obviously actually generally particularly
especially eventually occasionally truly really clearly
""".split()) | {
    "in addition", "for example", "at once", "by accident", "in fact", "in contrast", "on the contrary",
    "as a result", "for instance", "in other words", "in short", "above all", "after all", "in particular",
    "by contrast", "on average", "at best", "in return", "by comparison", "in essence", "on the whole",
    "as usual", "in turn", "in effect", "for one thing", "at any rate", "in any case", "as such",
    "if so", "if not", "even so", "so far", "once again", "more than", "other than", "instead of",
    "apart from", "aside from", "regardless of", "thanks to", "due to", "owing to", "in spite of",
    "because of", "in case of", "in terms of", "in view of", "by means of", "in a word", "in brief",
    "at least", "at most", "no doubt", "of course", "by now", "for now", "once more", "as well",
}

# ---------- 阅读题型判定 ----------
def classify(stem):
    s = stem.lower().strip()
    # 主旨题
    if re.search(r"mainly (about|discuss|deals?|tells?|concerns?|argues|explains|presents|examines)"
                 r"|main (idea|topic|purpose|point|message)|best title|appropriate title|proper title"
                 r"|primarily (about|discuss|concern)|the text (is|tells|mainly)|text mainly"
                 r"|mainly wants|intends to (tell|show|say|argue)|mainly concerned"
                 r"|can best summarize|best summarizes|summarize the (main|text)", s):
        return "主旨题"
    # 态度题（仅限真正问态度的问法）
    if re.search(r"attitude|tone|the author'?s (view|opinion|stand|feeling|answer)"
                 r"|holds? (a|an) .{0,24}(view|attitude)|is described as", s):
        return "态度题"
    # 语义题（词义 / 句意理解）
    if re.search(r"the word|the phrase|the expression|most probably means|closest in meaning"
                 r"|probably means|by saying|the sentence .{0,60}(means|suggests|implies)"
                 r"|underlined|\(line \d|\(para\.? ?\d|stands for", s):
        return "语义题"
    # 推理题
    if re.search(r"infer|implies|implied|suggests?|suggested|indicates?|indicated|learn (about|from|that)"
                 r"|can be concluded|can we conclude|concluded (from|that)|we can learn"
                 r"|it can be (inferred|learned)|following part|next paragraph|in the following"
                 r"|will most probably|paragraphs? (that )?follow", s):
        return "推理题"
    # 例证题
    if re.search(r"mentioned (in .*? )?to |mentions? .{0,60}? to (show|illustrate|explain|argue|prove|suggest)"
                 r"|the example of .{0,60}?(is|are|shows?|illustrates?|suggests?|demonstrates?)"
                 r"|example .{0,40}is used to|cites? .{0,40}to |uses? .{0,40}to (show|illustrate|explain|demonstrate|argue|suggest)"
                 r"|quotes? .{0,40}to |the author (uses|mentions|quotes|cites)|illustrates? ", s):
        return "例证题"
    # 默认细节题
    return "细节题"


def parse_answers(text):
    m = re.search(r"#+\s*参考答案\s*\n+(.{0,800}?)(?=\n#|\Z)", text, re.S)
    if not m:
        return {}
    out = {}
    for num, ans in re.findall(r"(\d+)\s*[.、]\s*([A-Z])(?![A-Za-z])", m.group(1)):
        out[int(num)] = ans
    return out


def parse_cloze_options(text):
    """解析完形题目区 -> {题号: [选项文本…]}"""
    i = text.find("## 题目")
    if i < 0:
        return {}
    seg = text[i:text.find("###", i) if "###" in text[i:] else len(text)]
    out = {}
    for line in seg.split("\n"):
        m = re.match(r"^\s*(\d+)\.\s*(.+)$", line)
        if not m:
            continue
        opts = re.findall(r"\[([A-D])\]\s*([^\[]+)", m.group(2))
        if len(opts) == 4:
            out[int(m.group(1))] = [t.strip() for _, t in opts]
    return out


def cloze_type(n, src_label, opts):
    """完形题型统一归为 4 类：语法结构 / 逻辑衔接 / 固定搭配 / 词义辨析"""
    s = (src_label or "").strip()
    if s:
        if "宾语从句" in s or "连接词" in s:
            return "语法结构"
        if "逻辑" in s or "连词" in s:
            return "逻辑衔接"
        if "搭配" in s or "介词短语" in s:
            return "固定搭配"
        if len(s) <= 10:
            return "词义辨析"
    if opts and sum(1 for o in opts if o.lower() in CONNECTIVES) >= 3:
        return "逻辑衔接"
    return "词义辨析"


def main():
    years = sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d))
    blocks, stat, detail, problems = [], Counter(), [], []

    for y in years:
        rows = []

        # ---- 完形 1-20 ----
        t = open(os.path.join(ROOT, y, "完形填空.md"), encoding="utf-8").read()
        clz = dict((int(a), b.strip()) for a, b in
                   re.findall(r"\*\*第\s*(\d+)\s*题[^*]*\*\*\s*[：:]\s*([^\n。（]{0,14})", t))
        opts = parse_cloze_options(t)
        ans = parse_answers(t)
        for n in range(1, 21):
            if n not in ans:
                problems.append(f"{y} 完形 {n} 缺答案")
            ty = cloze_type(n, clz.get(n, ""), opts.get(n))
            rows.append([f"完形 {n}题", ty, "", "", ans.get(n, "—"), ""])
            stat["完形"] += 1

        # ---- 阅读 Text1-4 ----
        for kind in TEXTS:
            t = open(os.path.join(ROOT, y, kind + ".md"), encoding="utf-8").read()
            ans = parse_answers(t)
            stems = dict((int(a), b) for a, b in re.findall(r"^##\s+(\d+)\.\s+(.+)$", t, re.M))
            lo, hi = RANGES[kind]
            for n in range(lo, hi + 1):
                if n not in ans:
                    problems.append(f"{y} {kind} {n} 缺答案")
                stem = stems.get(n, "")
                if not stem:
                    problems.append(f"{y} {kind} {n} 缺题干")
                ty = classify(stem) if stem else "—"
                rows.append([f"{kind} {n}题", ty, "", "", ans.get(n, "—"), ""])
                stat[ty] += 1
                detail.append((y, kind, n, ty, stem))

        # ---- 新题型 41-45 ----
        t = open(os.path.join(ROOT, y, "新题型.md"), encoding="utf-8").read()
        ans = parse_answers(t)
        m = re.search(r"题型特点[^\n]{0,140}", t)
        seg = m.group(0) if m else ""
        if "判断正误" in seg:
            ty = "判断正误"
        elif "多项对应" in seg or "信息匹配" in seg:
            ty = "多项对应"
        else:
            ty = "小标题匹配"
        for n in range(41, 46):
            if n not in ans:
                problems.append(f"{y} 新题型 {n} 缺答案")
            rows.append([f"新题型 {n}题", ty, "", "", ans.get(n, "—"), ""])
            stat["新题型"] += 1

        # ---- 主观题 46-48 ----
        rows.append(["翻译 46题", "英译汉（主观）", "", "", "—", ""])
        rows.append(["小作文 47题", "应用文写作（主观）", "", "", "—", ""])
        rows.append(["大作文 48题", "图表作文（主观）", "", "", "—", ""])

        blocks.append((y, rows))

    # ---------- 输出 ----------
    L = []
    L.append("---")
    L.append("title: 英语二真题做题记录表")
    L.append("type: synthesis")
    L.append("domain: 英语")
    L.append("created: " + TODAY)
    L.append("updated: " + TODAY)
    L.append('tags: [英语二, 真题, 做题记录, "刷题"]')
    L.append("---")
    L.append("")
    L.append("# 英语二真题做题记录表")
    L.append("")
    L.append("> 2010-2025 年英语二真题逐题记录表，**按年份分表**，共 16 套 × 48 题 = 768 行。")
    L.append("> **已预填**：题号、题目类型、正确答案（客观题）。**做题后自己填**：做题时间、难度、错选了啥。")
    L.append("")
    L.append("| 列 | 怎么填 |")
    L.append("|----|--------|")
    L.append("| 题号 | 题型 + 原卷题号（如 `Text3 26题`） |")
    L.append("| 题目类型 | 阅读：主旨 / 细节 / 推理 / 语义 / 例证 / 态度题；完形：词义辨析 / 固定搭配 / 逻辑衔接 / 语法结构；新题型：小标题匹配 / 多项对应 / 判断正误。**预填为机器初判，可自行修正** |")
    L.append("| 做题时间 | 该题耗时，如 `2'30\"` |")
    L.append("| 难度 | ⭐~⭐⭐⭐⭐，或写「易 / 中 / 难」 |")
    L.append("| 正确答案 | 客观题已预填；主观题（46/47/48）留空 |")
    L.append("| 错选了啥 | 填选错的选项字母，如 `C`；做对留空 |")
    L.append("")
    L.append("> 全卷结构（100 分）：完形 1-20（10 分）｜阅读 Part A 21-40（40 分）｜Part B 41-45（10 分）｜翻译 46（15 分）｜小作文 47（10 分）｜大作文 48（15 分）")
    L.append(">")
    L.append("> 建议节奏：完形 15 分钟｜阅读 70 分钟｜新题型 20 分钟｜翻译 25 分钟｜小作文 20 分钟｜大作文 30 分钟（详见 [[英语考情分析]]）")
    L.append("")
    L.append("---")
    L.append("")

    for y, rows in blocks:
        L.append(f"## {y} 年")
        L.append("")
        L.append("| 题号 | 题目类型 | 做题时间 | 难度 | 正确答案 | 错选了啥 |")
        L.append("|------|---------|---------|------|---------|---------|")
        for r in rows:
            L.append("| " + " | ".join(r) + " |")
        L.append("")

    L.append("---")
    L.append("")
    L.append("## See Also")
    L.append("")
    L.append("- [[英语二/英语二真题精读/真题精读总目录]] — 逐年逐篇精读（原文 + 题目 + 答案 + 解析）")
    L.append("- [[英语考情分析]] — 试卷结构、分值占比、建议做题时间")
    L.append("- [[英语/英语总目录]]")
    L.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    with open(os.path.join(TMP, "classify.json"), "w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False, indent=1)

    print("写出：", OUT)
    print("题型分布：", dict(stat))
    print("总行数：", sum(len(r) for _, r in blocks))
    print("完形：逻辑衔接", sum(1 for _, rows in blocks for r in rows if r[1] == "逻辑衔接"),
          "｜词义辨析", sum(1 for _, rows in blocks for r in rows if r[1] == "词义辨析"),
          "｜其他（来自解析）", sum(1 for _, rows in blocks
                                for r in rows if r[0].startswith("完形")
                                and r[1] not in ("逻辑衔接", "词义辨析", "—")))
    print("问题：", problems if problems else "无（答案/题干齐全）")


if __name__ == "__main__":
    main()
