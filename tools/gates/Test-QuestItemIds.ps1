# Gate: every non-minecraft quest item id must exist in INTERNAL/known_item_ids.txt
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $root
try {
    python tools\extract_item_ids.py | Out-Null
    $out = python tools\audit_quest_items.py
    Write-Host $out
    if ($out -match 'missing=([1-9][0-9]*)') {
        Write-Host "FAIL Test-QuestItemIds"
        exit 1
    }
} finally {
    Pop-Location
}
Write-Host "PASS Test-QuestItemIds"
exit 0
