# Gate: quest lang has enough titles; each chapter file has quests; chapter titles exist.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$chapDir = Join-Path $root "pack\overrides\config\ftbquests\quests\chapters"
$langFile = Join-Path $root "pack\overrides\config\ftbquests\quests\lang\en_us.snbt"
$failures = [System.Collections.Generic.List[string]]::new()

if (-not (Test-Path $chapDir) -or -not (Test-Path $langFile)) {
    Write-Host "FAIL Test-QuestConsistency — missing quests files"
    exit 1
}

$lang = Get-Content $langFile -Raw
$titleCount = ([regex]::Matches($lang, 'quest\.[0-9A-Fa-f]{16}\.title:')).Count
if ($titleCount -lt 400) {
    [void]$failures.Add("Expected at least 400 quest titles for 40-60h scaffold (found $titleCount)")
}

$chapters = Get-ChildItem $chapDir -Filter "*.snbt"
if ($chapters.Count -lt 16) {
    [void]$failures.Add("Expected at least 16 chapters (found $($chapters.Count))")
}

foreach ($c in $chapters) {
    $text = Get-Content $c.FullName -Raw
    if ($text -notmatch 'id:\s*"([0-9A-Fa-f]{16})"') {
        [void]$failures.Add("$($c.Name) missing chapter id")
        continue
    }
    $chapterId = [regex]::Match($text, 'id:\s*"([0-9A-Fa-f]{16})"').Groups[1].Value
    if ($lang -notmatch [regex]::Escape("chapter.$chapterId.title")) {
        [void]$failures.Add("Missing lang chapter title for $($c.Name) id=$chapterId")
    }
    # Count quest-like objects: blocks that include both id and tasks
    $questBlocks = [regex]::Matches($text, '(?s)\{\s*[^\}]*?\bid:\s*"[0-9A-Fa-f]{16}"[^\}]*?\btasks:\s*\[')
    if ($questBlocks.Count -lt 5) {
        [void]$failures.Add("$($c.Name) expected >= 5 quests with tasks (found $($questBlocks.Count))")
    }
}

# Group titles
foreach ($gid in @("A100000000000001", "A100000000000002", "A100000000000003")) {
    if ($lang -notmatch [regex]::Escape("chapter_group.$gid.title")) {
        [void]$failures.Add("Missing chapter_group title $gid")
    }
}

if ($failures.Count -gt 0) {
    Write-Host "FAIL Test-QuestConsistency ($($failures.Count) issue(s), titles=$titleCount)"
    $failures | ForEach-Object { Write-Host " - $_" }
    exit 1
}
Write-Host "PASS Test-QuestConsistency (titles=$titleCount, chapters=$($chapters.Count))"
exit 0
