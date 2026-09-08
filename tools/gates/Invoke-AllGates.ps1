# Professional release gates for Ninjacat Skies.
param(
    [switch]$SkipBuild,
    [switch]$WithExportDryRun
)
$ErrorActionPreference = "Stop"
$gateDir = $PSScriptRoot
$root = (Resolve-Path (Join-Path $gateDir "..\..")).Path
$failed = 0

function Invoke-Gate([string]$name, [scriptblock]$block) {
    Write-Host ""
    Write-Host "=== $name ==="
    & $block
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GATE FAILED: $name"
        $script:failed++
    }
}

Push-Location $root
try {
    Invoke-Gate "SanitizedPublicSurface" {
        pwsh -NoProfile -File (Join-Path $gateDir "Test-SanitizedPublicSurface.ps1")
    }
    Invoke-Gate "PackStructure" {
        pwsh -NoProfile -File (Join-Path $gateDir "Test-PackStructure.ps1")
    }
    Invoke-Gate "QuestConsistency" {
        pwsh -NoProfile -File (Join-Path $gateDir "Test-QuestConsistency.ps1")
    }
    Invoke-Gate "QuestItemIds" {
        pwsh -NoProfile -File (Join-Path $gateDir "Test-QuestItemIds.ps1")
    }
    Invoke-Gate "StewardCaches" {
        python -X utf8 (Join-Path $gateDir "test_steward_caches.py")
    }
    Invoke-Gate "PackKeybindings" {
        python (Join-Path $gateDir "test_pack_keybindings.py")
    }
    Invoke-Gate "CustomModsBuild" {
        $buildArgs = @()
        if ($SkipBuild) { $buildArgs += "-SkipIfJarsPresent" }
        pwsh -NoProfile -File (Join-Path $gateDir "Test-CustomModsBuild.ps1") @buildArgs
    }
    Invoke-Gate "SmokeHarness" {
        pwsh -NoProfile -File (Join-Path $gateDir "Test-SmokeHarness.ps1")
    }
    if ($WithExportDryRun) {
        Invoke-Gate "ExportDryRun" {
            pwsh -NoProfile -File (Join-Path $root "tools\export-curseforge.ps1")
            if ($LASTEXITCODE -eq 0) {
                python (Join-Path $gateDir "test_export_archive.py") (Join-Path $root "dist")
            }
        }
    }
} finally {
    Pop-Location
}

Write-Host ""
if ($failed -gt 0) {
    Write-Host "RESULT: $failed gate(s) failed"
    exit 1
}
Write-Host "RESULT: all gates passed"
exit 0
