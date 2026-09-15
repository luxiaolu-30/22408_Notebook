# -*- coding: utf-8 -*-
"""
生成 英语二/英语二真题精读/真题做题记录表.md
逐年一张表：题号 | 题目类型 | 文章体裁 | 做题时间 | 难度 | 正确答案 | 错选了啥
- 题号 / 题目类型 / 文章体裁 / 正确答案 由脚本预填；做题时间 / 难度 / 错选了啥 留空
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

# ============ 文章体裁 ============
# 阅读：来自各篇精读的「命题规律小结」首条（原文自述），缺失 4 篇按原文主题人工判定
READ_THEME = {
    ("2010", "Text1"): "商业/艺术市场类",   # 人工判定：艺术品市场牛市终结
    ("2010", "Text2"): "社会/家庭类",
    ("2010", "Text3"): "商业/社会类",
    ("2010", "Text4"): "法律/社会类",
    ("2011", "Text1"): "社科类",
    ("2011", "Text2"): "传媒/社会类",       # 人工判定：美国报业衰退
    ("2011", "Text3"): "文化/历史类",
    ("2011", "Text4"): "经济/政治类",
    ("2012", "Text1"): "教育政策类",
    ("2012", "Text2"): "社会文化类",
    ("2012", "Text3"): "法律/科技类",
    ("2012", "Text4"): "社会影响类",
    ("2013", "Text1"): "社会/经济类",       # 人工判定：美国制造业与就业
    ("2013", "Text2"): "社会/政策类",       # 人工判定：移民政策
    ("2013", "Text3"): "心理学类",
    ("2013", "Text4"): "社会政策类",
    ("2014", "Text1"): "书籍评论类",
    ("2014", "Text2"): "心理学研究类",
    ("2014", "Text3"): "科技/社会类",
    ("2014", "Text4"): "政策/经济类",
    ("2015", "Text1"): "社会调查类",
    ("2015", "Text2"): "教育/社会研究类",
    ("2015", "Text3"): "社会/语言类",
    ("2015", "Text4"): "经济/政策类",
    ("2016", "Text1"): "教育类",
    ("2016", "Text2"): "环保/政策类",
    ("2016", "Text3"): "生活方式类",
    ("2016", "Text4"): "社会/代际类",
    ("2017", "Text1"): "社会/体育类",
    ("2017", "Text2"): "家庭教育/科技类",
    ("2017", "Text3"): "教育类",
    ("2017", "Text4"): "环保/政策类",
    ("2018", "Text1"): "教育类",
    ("2018", "Text2"): "环保/科技类",
    ("2018", "Text3"): "科技/法律类",
    ("2018", "Text4"): "工作/效率类",
    ("2019", "Text1"): "心理学类",
    ("2019", "Text2"): "环保类",
    ("2019", "Text3"): "社会/经济类",
    ("2019", "Text4"): "环保/社会类",
    ("2020", "Text1"): "科普/实验类",
    ("2020", "Text2"): "商业/经济类",
    ("2020", "Text3"): "环保/政策类",
    ("2020", "Text4"): "社会/代际类",
    ("2021", "Text1"): "社会/经济类",
    ("2021", "Text2"): "环保/农业类",
    ("2021", "Text3"): "商业/科技类",
    ("2021", "Text4"): "心理/科普类",
    ("2022", "Text1"): "商业/环保类",
    ("2022", "Text2"): "社会/经济类",
    ("2022", "Text3"): "科技/商业伦理类",
    ("2022", "Text4"): "科普/研究类",
    ("2023", "Text1"): "环保/社会争议类",
    ("2023", "Text2"): "社会/政策类",
    ("2023", "Text3"): "科普/心理类",
    ("2023", "Text4"): "科普/心理类",
    ("2024", "Text1"): "商业/科技类",
    ("2024", "Text2"): "环保/农业类",
    ("2024", "Text3"): "社会/健康类",
    ("2024", "Text4"): "科技/法律类",
    ("2025", "Text1"): "社会/经济类",
    ("2025", "Text2"): "社会/医疗类",
    ("2025", "Text3"): "环保/社会类",
    ("2025", "Text4"): "社会/城市规划类",
}

# 完形 / 翻译 / 新题型：按各篇「原文」主题人工判定
CLOZE_THEME = {
    "2010": "公共卫生（猪流感）", "2011": "法律/知识产权", "2012": "美国文化（G.I. Joe）",
    "2013": "科技/金融（无现金社会）", "2014": "健康（体重与疾病）", "2015": "社会生活（手机与陌生人）",
    "2016": "商业/心理（幸福与生产力）", "2017": "科技/就业（无工作社会）", "2018": "心理（对不确定性的需求）",
    "2019": "健康（体重管理）", "2020": "家庭（如何做好父母）", "2021": "职场/管理（目标与后果）",
    "2022": "文化/写作（作家与时间）", "2023": "商业（小企业经营）", "2024": "社会生活（社交生活）",
    "2025": "心理（求助的困难）",
}
TRANS_THEME = {
    "2010": "环保（可持续发展）", "2011": "环保/科技（IT 碳排放）", "2012": "社会（人才移民）",
    "2013": "科普/心理（超强记忆）", "2014": "心理（真正的乐观）", "2015": "科普（熟悉路线的驾驶）",
    "2016": "商业（超市诱导消费）", "2017": "职业（时尚与出版求职）", "2018": "教育（职业规划作业）",
    "2019": "文化/文学（作家 James Herriot）", "2020": "人生哲理（失败与成长）",
    "2021": "社会/心理（陌生人的温暖）", "2022": "艺术（绘画创作）",
    "2023": "文化/文学（华兹华斯与浪漫主义）", "2024": "社会/商业（农夫市集）",
    "2025": "社会/心理（对话中的沉默）",
}
PARTB_THEME = {
    "2010": "科技/航空（效仿鸟类省油）", "2011": "公共卫生（脂肪税之争）", "2012": "历史/文化（伟人史观）",
    "2013": "生活/健康（预算内饮食）", "2014": "艺术（英国大地艺术）", "2015": "心理（面对失去）",
    "2016": "心理（向孩子学幸福）", "2017": "社会交往（与陌生人交谈）", "2018": "社会交往（与陌生人交谈）",
    "2019": "家庭/消费（购房听孩子意见）", "2020": "职场（赢得同事好感）", "2021": "职场（与上级有分歧）",
    "2022": "健康（休息后恢复运动）", "2023": "环保/政策（净零排放推高房价）",
    "2024": "教育（大学评估课外活动）", "2025": "职场（提出改变建议）",
}
# 小作文：文体 · 主题
LETTER_THEME = {
    "2010": "感谢信 · 中美文化交流致谢", "2011": "祝贺信 · 祝贺升学并建议",
    "2012": "投诉信 · 电子词典质量投诉", "2013": "倡议信 · 慈善义卖动员",
    "2014": "介绍+询问信 · 与室友合租", "2015": "通知 · 夏令营招志愿者",
    "2016": "回信 · 祝贺获奖并给翻译建议", "2017": "回复邀请信 · 介绍中国文化",
    "2018": "道歉信 · 取消拜访并另约", "2019": "建议信 · 建议辩论主题",
    "2020": "介绍信 · 介绍历史景点", "2021": "邀请信 · 邀请参加线上会议",
    "2022": "邀请信 · 介绍美食节并邀请", "2023": "说明信 · 说明备考选择",
    "2024": "建议信 · 古建筑调查计划", "2025": "邀请信 · 改编中国古典小说短剧",
}
# 大作文：图表类型 · 主题
ESSAY_THEME = {
    "2010": "图表作文（柱状图）· 手机订阅量", "2011": "图表作文（柱状图）· 中国轿车市场份额",
    "2012": "图表作文（表格）· 员工工作满意度", "2013": "图表作文（柱状图）· 大学生兼职情况",
    "2014": "图表作文（柱状图）· 城乡人口变化", "2015": "图表作文（饼图）· 春节消费支出",
    "2016": "图表作文（饼图）· 大学生旅游目的", "2017": "图表作文（折线图）· 博物馆数量与参观人数",
    "2018": "图表作文（饼图）· 选餐厅关注因素", "2019": "图表作文（柱状图）· 毕业生去向",
    "2020": "图表作文（饼图）· 手机阅读目的", "2021": "图表作文（柱状图）· 体育锻炼方式",
    "2022": "图表作文（柱状图）· 快递业务量", "2023": "图表作文（线图）· 居民健康素养水平",
    "2024": "图表作文（饼图）· 劳动实践课收获", "2025": "图表作文（柱状图）· 社区老年人休闲活动",
}

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


def classify(stem):
    s = stem.lower().strip()
    if re.search(r"mainly (about|discuss|deals?|tells?|concerns?|argues|explains|presents|examines)"
                 r"|main (idea|topic|purpose|point|message)|best title|appropriate title|proper title"
                 r"|primarily (about|discuss|concern)|the text (is|tells|mainly)|text mainly"
                 r"|mainly wants|intends to (tell|show|say|argue)|mainly concerned"
                 r"|can best summarize|best summarizes|summarize the (main|text)", s):
        return "主旨题"
    if re.search(r"attitude|tone|the author'?s (view|opinion|stand|feeling|answer)"
                 r"|holds? (a|an) .{0,24}(view|attitude)|is described as", s):
        return "态度题"
    if re.search(r"the word|the phrase|the expression|most probably means|closest in meaning"
                 r"|probably means|by saying|the sentence .{0,60}(means|suggests|implies)"
                 r"|underlined|\(line \d|\(para\.? ?\d|stands for", s):
        return "语义题"
    if re.search(r"infer|implies|implied|suggests?|suggested|indicates?|indicated|learn (about|from|that)"
                 r"|can be concluded|can we conclude|concluded (from|that)|we can learn"
                 r"|it can be (inferred|learned)|following part|next paragraph|in the following"
                 r"|will most probably|paragraphs? (that )?follow", s):
        return "推理题"
    if re.search(r"mentioned (in .*? )?to |mentions? .{0,60}? to (show|illustrate|explain|argue|prove|suggest)"
                 r"|the example of .{0,60}?(is|are|shows?|illustrates?|suggests?|demonstrates?)"
                 r"|example .{0,40}is used to|cites? .{0,40}to |uses? .{0,40}to (show|illustrate|explain|demonstrate|argue|suggest)"
                 r"|quotes? .{0,40}to |the author (uses|mentions|quotes|cites)|illustrates? ", s):
        return "例证题"
    return "细节题"


def parse_answers(text):
    m = re.search(r"#+\s*参考答案\s*\n+(.{0,800}?)(?=\n#|\Z)", text, re.S)
    if not m:
        return {}
    return {int(n): a for n, a in re.findall(r"(\d+)\s*[.、]\s*([A-Z])(?![A-Za-z])", m.group(1))}


def parse_cloze_options(text):
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


def cloze_type(src_label, opts):
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
            rows.append([f"完形 {n}题", cloze_type(clz.get(n, ""), opts.get(n)),
                         CLOZE_THEME.get(y, "—"), "", "", ans.get(n, "—"), ""])
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
                rows.append([f"{kind} {n}题", ty, READ_THEME.get((y, kind), "—"),
                             "", "", ans.get(n, "—"), ""])
                stat[ty] += 1
                detail.append((y, kind, n, ty, stem))

        # ---- 新题型 41-45 ----
        t = open(os.path.join(ROOT, y, "新题型.md"), encoding="utf-8").read()
        ans = parse_answers(t)
        m = re.search(r"题型特点[^\n]{0,140}", t)
        seg = m.group(0) if m else ""
        ty = ("判断正误" if "判断正误" in seg
              else ("多项对应" if ("多项对应" in seg or "信息匹配" in seg) else "小标题匹配"))
        for n in range(41, 46):
            if n not in ans:
                problems.append(f"{y} 新题型 {n} 缺答案")
            rows.append([f"新题型 {n}题", ty, PARTB_THEME.get(y, "—"), "", "", ans.get(n, "—"), ""])
            stat["新题型"] += 1

        # ---- 主观题 46-48 ----
        rows.append(["翻译 46题", "英译汉（主观）", TRANS_THEME.get(y, "—"), "", "", "—", ""])
        rows.append(["小作文 47题", "应用文写作（主观）", LETTER_THEME.get(y, "—"), "", "", "—", ""])
        rows.append(["大作文 48题", "图表作文（主观）", ESSAY_THEME.get(y, "—"), "", "", "—", ""])

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
    L.append("> **已预填**：题号、题目类型、文章体裁、正确答案（客观题）。**做题后自己填**：做题时间、难度、错选了啥。")
    L.append("")
    L.append("| 列 | 怎么填 |")
    L.append("|----|--------|")
    L.append("| 题号 | 题型 + 原卷题号（如 `Text3 26题`） |")
    L.append("| 题目类型 | 阅读：主旨 / 细节 / 推理 / 语义 / 例证 / 态度题；完形：词义辨析 / 固定搭配 / 逻辑衔接 / 语法结构；新题型：小标题匹配 / 多项对应 / 判断正误。**预填为机器初判，可自行修正** |")
    L.append("| 文章体裁 | 阅读 / 完形 / 翻译 / 新题型写文章题材（如 `商业/科技类`、`环保/社会类`）；小作文写文体 + 主题；大作文写图表类型 + 主题。阅读题材取自各篇精读的「命题规律小结」原文自述 |")
    L.append("| 做题时间 | 该题耗时，如 `2'30\"` |")
    L.append("| 难度 | ⭐~⭐⭐⭐⭐，或写「易 / 中 / 难」 |")
    L.append("| 正确答案 | 客观题已预填；主观题（46/47/48）留空 |")
    L.append("| 错选了啥 | 填选错的选项字母，如 `C`；做对留空 |")
    L.append("")
    L.append("> 全卷结构（100 分）：完形 1-20（10 分）｜阅读 Part A 21-40（40 分）｜Part B 41-45（10 分）｜翻译 46（15 分）｜小作文 47（10 分）｜大作文 48（15 分）")
    L.append(">")
    L.append("> 建议节奏：完形 15 分钟｜阅读 70 分钟｜新题型 20 分钟｜翻译 25 分钟｜小作文 20 分钟｜大作文 30 分钟（详见 [[英语考情分析]]）")
    L.append(">")
    L.append("> 用法建议：做完一套回看本表，把「错选了啥」按**文章体裁**和**题目类型**两个维度汇总，就能看出自己到底是哪类题材、哪类题型稳定丢分。")
    L.append("")
    L.append("---")
    L.append("")

    for y, rows in blocks:
        L.append(f"## {y} 年")
        L.append("")
        L.append("| 题号 | 题目类型 | 文章体裁 | 做题时间 | 难度 | 正确答案 | 错选了啥 |")
        L.append("|------|---------|---------|---------|------|---------|---------|")
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

    miss = [(y, k) for k in TEXTS for y in years if (y, k) not in READ_THEME]
    print("写出：", OUT)
    print("题型分布：", dict(stat))
    print("总行数：", sum(len(r) for _, r in blocks))
    print("阅读题材缺失：", miss if miss else "无")
    for name, d in [("完形", CLOZE_THEME), ("翻译", TRANS_THEME), ("新题型", PARTB_THEME),
                    ("小作文", LETTER_THEME), ("大作文", ESSAY_THEME)]:
        lack = [y for y in years if y not in d]
        print(f"  {name}题材缺失：", lack if lack else "无")
    print("数据问题：", problems if problems else "无（答案/题干齐全）")


if __name__ == "__main__":
    main()
