# Gate: required pack + mod project files exist.
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Get-CustomModVersion.ps1")
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$failures = [System.Collections.Generic.List[string]]::new()

function Need([string]$rel) {
    $p = Join-Path $root $rel
    if (-not (Test-Path $p)) { [void]$failures.Add("Missing $rel") }
}

Need "pack\pack.toml"
Need "pack\overrides\config\ftbquests\quests\data.snbt"
Need "pack\overrides\config\ftbquests\quests\chapter_groups.snbt"
Need "pack\overrides\config\ftbquests\quests\lang\en_us.snbt"
Need "pack\overrides\kubejs\server_scripts\voidloom_recipes.js"
Need "README.md"
Need "docs\STORY.md"
Need "docs\CHANGELOG.md"
Need "docs\public\store-description.md"
Need "mods\settings.gradle"
Need "mods\ninjacatskies\src\main\java\com\ninjacat\skies\core\NinjacatSkies.java"
Need "mods\voidloom\src\main\java\com\ninjacat\skies\voidloom\Voidloom.java"
Need "mods\clowderhall\src\main\java\com\ninjacat\skies\clowder\ClowderHall.java"
Need "mods\ninjacat-lib\src\main\java\com\ninjacat\skies\lib\NinjacatLib.java"
Need "INTERNAL\README.md"

$chapterFiles = Get-ChildItem (Join-Path $root "pack\overrides\config\ftbquests\quests\chapters") -Filter "*.snbt" -ErrorAction SilentlyContinue
if (-not $chapterFiles -or $chapterFiles.Count -lt 16) {
    [void]$failures.Add("Expected at least 16 quest chapters (found $($chapterFiles.Count))")
}
Need "pack\overrides\config\skyblockbuilder\templates.json5"
Need "pack\overrides\config\skyblockbuilder\templates\islands\ninjacat_pad.nbt"
Need "pack\overrides\config\skyblockbuilder\templates\islands\dojo_cottage.nbt"
Need "pack\overrides\config\skyblockbuilder\templates\islands\frayed_thread.nbt"
Need "pack\overrides\config\skyblockbuilder\templates\islands\clowder_dock.nbt"

$jars = @(Get-ChildItem (Join-Path $root "pack\mods") -Filter "*.jar" -ErrorAction SilentlyContinue)
if ($jars.Count -lt 20) {
    [void]$failures.Add("Expected at least 20 jars in pack/mods (found $($jars.Count))")
}
$coreJars = @(Get-ChildItem (Join-Path $root "pack\mods") -Filter "ninjacatskies-core-*.jar" -ErrorAction SilentlyContinue)
if ($coreJars.Count -lt 1) {
    [void]$failures.Add("Missing pack/mods/ninjacatskies-core-*.jar (companions ship jar-in-jar; do not copy loose ninjacatskies/voidloom/clowderhall/ninjacatlib/guardians jars)")
} elseif ($coreJars.Count -gt 1) {
    [void]$failures.Add("Multiple Core jars in pack/mods: $($coreJars.Name -join ', ')")
}
foreach ($loose in @(Get-ChildItem (Join-Path $root "pack\mods") -Filter "*.jar" -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(ninjacatskies|ninjacatlib|clowderhall|voidloom|guardians)-[0-9]' })) {
    [void]$failures.Add("Loose companion jar in pack/mods: $($loose.Name) — companions ship inside ninjacatskies-core")
}

if ($failures.Count -gt 0) {
    Write-Host "FAIL Test-PackStructure ($($failures.Count) issue(s))"
    $failures | ForEach-Object { Write-Host " - $_" }
    exit 1
}
Write-Host "PASS Test-PackStructure (jars=$($jars.Count))"
exit 0
