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
    "clowderhall-${customModVersion}.jar",
    "guardians-${customModVersion}.jar"
)
$packMods = Join-Path $root "pack\mods"
$corePresent = @(Get-ChildItem $packMods -Filter "ninjacatskies-core-*.jar" -ErrorAction SilentlyContinue).Count -gt 0

if ($SkipIfJarsPresent -and $corePresent) {
    Write-Host "PASS Test-CustomModsBuild (skipped compile; ninjacatskies-core present in pack/mods)"
    exit 0
}

Push-Location $modsRoot
try {
    & .\gradlew.bat :ninjacat-lib:build :ninjacatskies:build :voidloom:build :clowderhall:build :guardians:build --no-daemon
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL Test-CustomModsBuild — gradle exit $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

# Companions ship inside ninjacatskies-core on CurseForge. Never copy loose jars into pack/mods.
foreach ($n in $needed) {
    $found = Get-ChildItem $modsRoot -Recurse -Filter $n -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match '\\build\\libs\\' } |
        Select-Object -First 1
    if (-not $found) {
        Write-Host "FAIL Test-CustomModsBuild — missing compiled $n under mods/*/build/libs"
        exit 1
    }
}
if (-not $corePresent) {
    Write-Host "WARN Test-CustomModsBuild — pack/mods has no ninjacatskies-core-*.jar; run tools/build_core_jar.py after a Core release"
}
Write-Host "PASS Test-CustomModsBuild (compiled $customModVersion; pack still uses Core jar-in-jar)"
exit 0
