param(
    [Parameter(Mandatory=$true)][int]$Year
)

$ErrorActionPreference = 'Stop'
$base = 'd:\files\个人文件\22408_Notebook\408\历年真题'
$srcPure = "$base\408历年真题纯净刷题版\$Year.md"
$srcReadDir = "$base\408真题精读\$Year"
$dst = "$base\$Year"

# 1. 创建目标目录
if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst | Out-Null }
if (-not (Test-Path "$dst\images")) { New-Item -ItemType Directory -Path "$dst\images" | Out-Null }

# 2. 复制题面
Copy-Item $srcPure "$dst\题面.md" -Force

# 3. 修改题面的 frontmatter 和"对答案"链接
$face = Get-Content "$dst\题面.md" -Raw -Encoding UTF8
$face = $face -replace 'title: .*', "title: $Year 年 408 真题 · 题面"
$face = $face -replace 'topic: 刷题纯净版', 'topic: 题面'
$face = $face -replace '# .* 题面', "# $Year 年 408 真题 · 题面"
$face = $face -replace '# .* 刷题纯净版', "# $Year 年 408 真题 · 题面"
# 替换"对答案"链接行
$face = $face -replace '> 对答案：\[\[.*\]\].*', '> 刷完后对答案、看解析：[[答案与解析]]'
Set-Content -Path "$dst\题面.md" -Value $face -Encoding UTF8 -NoNewline

# 4. 复制图片
if (Test-Path "$srcReadDir\images") {
    Get-ChildItem "$srcReadDir\images" -File | ForEach-Object {
        Copy-Item $_.FullName "$dst\images\$($_.Name)" -Force
    }
}

# 5. 拼接 4 个解析文件正文，并提取选择题答案
$files = @(
    @{path="$srcReadDir\数据结构.md"; subj='数据结构'},
    @{path="$srcReadDir\计算机组成原理.md"; subj='计算机组成原理'},
    @{path="$srcReadDir\操作系统.md"; subj='操作系统'},
    @{path="$srcReadDir\计算机网络.md"; subj='计算机网络'}
)

# 选择题答案哈希：题号 -> 字母
$choiceAns = @{}
# 综合题信息：题号 -> "分值|科目|考点"
$compInfo = @{}
# 综合题答案首句：题号 -> 字符串
$compAns = @{}

$sb = New-Object System.Text.StringBuilder
foreach ($f in $files) {
    if (-not (Test-Path $f.path)) {
        Write-Host "WARN: $($f.path) 不存在，跳过"
        continue
    }
    $content = Get-Content -Path $f.path -Raw -Encoding UTF8

    # 截取 ## 一 到 ## See Also
    $startIdx = $content.IndexOf('## 一、单项选择题')
    $endIdx = $content.IndexOf('## See Also')
    if ($startIdx -lt 0 -or $endIdx -lt 0) {
        Write-Host "WARN: $($f.path) 没找到 ## 一 或 ## See Also"
        continue
    }
    $body = $content.Substring($startIdx, $endIdx - $startIdx)

    # 提取选择题答案
    $mcMatches = [regex]::Matches($body, '###\s+(\d+)\.\s+\（(\d+)\s*分.*?·\s*([^）]+?)）.*?\*\*答案\*\*：\s*([A-D])', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    foreach ($m in $mcMatches) {
        $qnum = [int]$m.Groups[1].Value
        $score = $m.Groups[2].Value
        $point = $m.Groups[3].Value.Trim()
        $ans = $m.Groups[4].Value
        if ($qnum -le 40) {
            $choiceAns[$qnum] = $ans
        }
    }

    # 提取综合题题号、分值、考点
    $compMatches = [regex]::Matches($body, '###\s+(\d+)\.\s+\（(\d+)\s*分.*?·\s*([^）]+?)）')
    foreach ($m in $compMatches) {
        $qnum = [int]$m.Groups[1].Value
        $score = $m.Groups[2].Value
        $point = $m.Groups[3].Value.Trim()
        if ($qnum -ge 41) {
            $compInfo[$qnum] = "$score|$($f.subj)|$point"
        }
    }

    # 提取综合题答案首句
    $compAnsMatches = [regex]::Matches($body, '###\s+(\d+)\.\s+\（.*?）.*?\*\*答案.*?：\s*([^\r\n]+)', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    foreach ($m in $compAnsMatches) {
        $qnum = [int]$m.Groups[1].Value
        $ansLine = $m.Groups[2].Value.Trim()
        if ($qnum -ge 41) {
            # 截断到第一句（句号或换行）
            $firstSentence = ($ansLine -split '[。\n]')[0]
            if ($firstSentence.Length -gt 80) { $firstSentence = $firstSentence.Substring(0, 80) + '...' }
            $compAns[$qnum] = $firstSentence
        }
    }

    # 替换图片路径
    $body = $body -replace "408/历年真题/408真题精读/$Year/images/", 'images/'
    # 替换一级章节
    $body = $body -replace '## 一、单项选择题', "### 选择题 · $($f.subj)"
    $body = $body -replace '## 二、综合应用题', "### 综合题 · $($f.subj)"
    [void]$sb.Append($body)
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")
}

# 6. 生成答案与解析.md
$outFile = "$dst\答案与解析.md"

# 6.1 头部
$header = @"
---
title: $Year 年 408 真题 · 答案与解析
type: answer-analysis
domain: 408
year: $Year
created: 2026-09-18
updated: 2026-09-18
tags: ["408", 答案与解析, "$Year"]
---

# $Year 年 408 真题 · 答案与解析

> 刷完 [[题面]] 后用此页对答案、看解析。
> 顺序：数据结构（1–11, 41–42）→ 组成原理（12–22, 43–44）→ 操作系统（23–32, 45–46）→ 计算机网络（33–40, 47）

## 一、选择题答案速查表（40 题，每题 2 分，共 80 分）

"@

# 6.2 选择题答案速查表（4 张表 × 10 题）
$subjAbbr = @{1='数结';12='组原';23='操作';33='计网'}
$tables = ""
for ($row = 0; $row -lt 4; $row++) {
    $startQ = $row * 10 + 1
    $endQ = $startQ + 9
    $qnums = $startQ..$endQ
    $headerRow = "| 题号 | " + ($qnums -join " | ") + " |"
    $ansRow = "| 答案 | " + ($qnums | ForEach-Object { "**$($choiceAns[$_])**" }) -join " | " + " |"
    $subjRow = "| 科目 | " + ($qnums | ForEach-Object {
        $s = ''
        if ($_ -le 11) { $s = '数结' }
        elseif ($_ -le 22) { $s = '组原' }
        elseif ($_ -le 32) { $s = '操作' }
        else { $s = '计网' }
        $s
    }) -join " | " + " |"
    $tables += "$headerRow`n$ansRow`n$subjRow`n`n"
}
$tables += "> 科目缩写：数结 = 数据结构 | 组原 = 计算机组成原理 | 操作 = 操作系统 | 计网 = 计算机网络`n`n## 二、综合题答案要点速查表（7 题，共 70 分）`n`n"

# 6.3 综合题要点表
$tables += "| 题号 | 分值 | 科目 | 考点 | 关键结论 |`n|------|------|------|------|----------|`n"
for ($q = 41; $q -le 47; $q++) {
    if ($compInfo.ContainsKey($q)) {
        $parts = $compInfo[$q] -split '\|'
        $score = $parts[0]
        $subj = $parts[1]
        $point = $parts[2]
        $ans = if ($compAns.ContainsKey($q)) { $compAns[$q] } else { '—' }
        $tables += "| $q | $score | $subj | $point | $ans |`n"
    }
}

$tables += "`n---`n`n## 三、详细解析`n`n> 以下按题号顺序排列。每题包含题干、选项、答案、解析。`n> 图片以相对路径 ``images/xxx.webp`` 引用，与本文同目录。`n`n"

# 6.4 写入头部 + 速查表
$content = $header + $tables

# 6.5 末尾去掉 PowerShell 自动加的多余 ---
$bodyContent = $sb.ToString()
# 去掉末尾多余的 "---\n"
$bodyContent = $bodyContent -replace '---\s*$'

# 6.6 拼接正文
$content += $bodyContent

# 6.7 加 See Also
$content += "`n## See Also`n`n- [[题面]] — 仅题干与选项，用于限时刷题`n- [[../408历年真题总目录]] — 历年真题总目录`n- [[408考情分析]] — 试卷构成与逐年考点统计`n"

Set-Content -Path $outFile -Value $content -Encoding UTF8 -NoNewline

# 统计
$totalLines = (Get-Content $outFile).Count
$ansCount = $choiceAns.Count
$compCount = $compInfo.Count
Write-Host "$Year 年：选择题答案 $ansCount 条，综合题信息 $compCount 条，总行数 $totalLines"
