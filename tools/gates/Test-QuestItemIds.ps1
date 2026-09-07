# Gate: every non-minecraft quest item id must exist in INTERNAL/known_item_ids.txt
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $root
try {
    python tools\extract_item_ids.py | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL Test-QuestItemIds — item extraction failed"
        exit 1
    }
    $out = python tools\audit_quest_items.py
    $auditExit = $LASTEXITCODE
    Write-Host $out
    if ($auditExit -ne 0 -or $out -notmatch 'quest_items=\d+ missing=0 dead_ends=0') {
        Write-Host "FAIL Test-QuestItemIds"
        exit 1
    }
} finally {
    Pop-Location
}
Write-Host "PASS Test-QuestItemIds"
exit 0
