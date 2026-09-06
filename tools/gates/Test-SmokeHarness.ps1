# Optional smoke harness: validates pack artifacts without requiring a full Minecraft GUI session.
# Use -LaunchClient only when a CurseForge/MultiMC instance path is provided and you want a boot check.
param(
    [string]$InstanceDir = "",
    [switch]$LaunchClient
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Fail([string]$m) { [void]$failures.Add($m) }

# 1) Every jar is a readable zip
$jars = Get-ChildItem (Join-Path $root "pack\mods") -Filter "*.jar"
foreach ($jar in $jars) {
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $z = [System.IO.Compression.ZipFile]::OpenRead($jar.FullName)
        $z.Dispose()
    } catch {
        Add-Fail "Corrupt or unreadable jar: $($jar.Name) ($_)"
    }
}

# 2) Custom jars contain expected mod metadata
foreach ($pair in @(
    @{ Jar = "ninjacatskies-0.1.0.jar"; Needle = "ninjacatskies" },
    @{ Jar = "voidloom-0.1.0.jar"; Needle = "voidloom" },
    @{ Jar = "clowderhall-0.1.0.jar"; Needle = "clowderhall" },
    @{ Jar = "ninjacatlib-0.1.0.jar"; Needle = "ninjacatlib" }
)) {
    $path = Join-Path $root "pack\mods\$($pair.Jar)"
    if (-not (Test-Path $path)) { Add-Fail "Missing $($pair.Jar)"; continue }
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $z = [System.IO.Compression.ZipFile]::OpenRead($path)
    try {
        $entry = $z.Entries | Where-Object { $_.FullName -match 'neoforge.mods.toml|mods.toml' } | Select-Object -First 1
        if (-not $entry) { Add-Fail "$($pair.Jar) missing mods.toml"; continue }
        $reader = New-Object System.IO.StreamReader($entry.Open())
        $toml = $reader.ReadToEnd()
        $reader.Close()
        if ($toml -notmatch [regex]::Escape($pair.Needle)) {
            Add-Fail "$($pair.Jar) metadata missing mod id $($pair.Needle)"
        }
    } finally { $z.Dispose() }
}

# 3) Quest chapters parse as non-empty
$chapters = Get-ChildItem (Join-Path $root "pack\overrides\config\ftbquests\quests\chapters") -Filter "*.snbt"
if ($chapters.Count -lt 9) { Add-Fail "Expected 9 Strand chapters, found $($chapters.Count)" }
foreach ($c in $chapters) {
    $t = Get-Content $c.FullName -Raw
    if ($t -notmatch 'quests:\s*\[') { Add-Fail "$($c.Name) has no quests block" }
}

# 4) Optional client launch hook
if ($LaunchClient) {
    if (-not $InstanceDir -or -not (Test-Path $InstanceDir)) {
        Add-Fail "LaunchClient requested but InstanceDir missing/invalid"
    } else {
        Write-Host "InstanceDir OK: $InstanceDir (manual launch — automate with your launcher CLI if configured)"
    }
}

if ($failures.Count -gt 0) {
    Write-Host "FAIL Test-SmokeHarness ($($failures.Count) issue(s))"
    $failures | ForEach-Object { Write-Host " - $_" }
    exit 1
}
Write-Host "PASS Test-SmokeHarness (jars=$($jars.Count), chapters=$($chapters.Count))"
exit 0
