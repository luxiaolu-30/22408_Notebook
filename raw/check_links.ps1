$root = Split-Path $PSScriptRoot -Parent
$mdFiles = Get-ChildItem $root -Recurse -Filter *.md | Where-Object { $_.FullName -notmatch '\\\.git\\|\\\.workbuddy\\|log\.md$|WIKI-SCHEMA\.md$' }

$nameIndex = @{}
foreach ($f in $mdFiles) {
  if (-not $nameIndex.ContainsKey($f.BaseName)) { $nameIndex[$f.BaseName] = $f.FullName }
}

$allFiles = Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\|\\\.workbuddy\\' }

$broken = @()
foreach ($f in $mdFiles) {
  $lines = Get-Content $f.FullName -Encoding UTF8
  $inCode = $false
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match '^```') { $inCode = -not $inCode; continue }
    if ($inCode) { continue }
    $ms = [regex]::Matches($line, '!?\[\[([^\]|#]+?)(\|[^\]]*)?\]\]')
    foreach ($m in $ms) {
      $link = $m.Groups[1].Value.Trim()
      if ($link -eq '') { continue }
      $ok = $false
      if ($link -match '/') {
        $p = Join-Path $root $link
        if (Test-Path -LiteralPath $p) { $ok = $true }
        elseif (Test-Path -LiteralPath ($p + '.md')) { $ok = $true }
        elseif ($nameIndex.ContainsKey(($link -replace '.*/',''))) { $ok = $true }
      } else {
        if ($nameIndex.ContainsKey($link)) { $ok = $true }
        else {
          $img = $allFiles | Where-Object { $_.Name -eq $link } | Select-Object -First 1
          if ($img) { $ok = $true }
        }
      }
      if (-not $ok) {
        $rel = $f.FullName.Replace("$root\", "")
        $broken += "$rel :: $($i+1) :: $link"
      }
    }
  }
}

Write-Output ("BROKEN COUNT: " + $broken.Count)
foreach ($b in $broken) { Write-Output $b }
