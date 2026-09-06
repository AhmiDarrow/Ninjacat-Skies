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
            $z = Get-ChildItem (Join-Path $root "dist") -Filter "NinjacatSkies-*.zip" |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if (-not $z) { exit 1 }
            $tmp = Join-Path $root "dist\_gate_unzip"
            Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
            Expand-Archive $z.FullName -DestinationPath $tmp -Force
            if (Test-Path (Join-Path $tmp "INTERNAL")) { Write-Host "INTERNAL in zip"; exit 1 }
            if (Get-ChildItem $tmp -Recurse -Filter ".env" -ErrorAction SilentlyContinue) { Write-Host ".env in zip"; exit 1 }
            if (Get-ChildItem $tmp -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue) { Write-Host "scripts in zip"; exit 1 }
            Write-Host "PASS ExportDryRun ($($z.Name))"
            Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
            exit 0
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
