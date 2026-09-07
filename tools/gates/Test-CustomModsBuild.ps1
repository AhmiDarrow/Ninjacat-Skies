# Gate: custom NeoForge mods compile (or reusable jars already present + sources compile).
param(
    [switch]$SkipIfJarsPresent
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Get-CustomModVersion.ps1")
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$modsRoot = Join-Path $root "mods"
$needed = @(
    "ninjacatlib-${customModVersion}.jar",
    "ninjacatskies-${customModVersion}.jar",
    "voidloom-${customModVersion}.jar",
    "clowderhall-${customModVersion}.jar"
)
$packMods = Join-Path $root "pack\mods"
$allPresent = $true
foreach ($n in $needed) {
    if (-not (Test-Path (Join-Path $packMods $n))) { $allPresent = $false }
}

if ($SkipIfJarsPresent -and $allPresent) {
    Write-Host "PASS Test-CustomModsBuild (skipped compile; jars present in pack/mods)"
    exit 0
}

Push-Location $modsRoot
try {
    & .\gradlew.bat :ninjacat-lib:build :ninjacatskies:build :voidloom:build :clowderhall:build --no-daemon
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL Test-CustomModsBuild — gradle exit $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

# Refresh only this version; build/libs may retain artifacts from older releases.
Get-ChildItem $modsRoot -Recurse -Filter "*.jar" |
    Where-Object { $_.FullName -match '\\build\\libs\\' -and $_.Name -in $needed } |
    ForEach-Object { Copy-Item $_.FullName $packMods -Force }

foreach ($n in $needed) {
    if (-not (Test-Path (Join-Path $packMods $n))) {
        Write-Host "FAIL Test-CustomModsBuild — missing $n after build"
        exit 1
    }
}
Write-Host "PASS Test-CustomModsBuild"
exit 0
