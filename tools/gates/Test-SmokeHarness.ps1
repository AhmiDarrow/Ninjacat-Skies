# Optional smoke harness: validates pack artifacts without requiring a full Minecraft GUI session.
# Use -LaunchClient only when a CurseForge/MultiMC instance path is provided and you want a boot check.
param(
    [string]$InstanceDir = "",
    [switch]$LaunchClient
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Get-CustomModVersion.ps1")
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

# 2) Core jar-in-jar contains the five companion mods
Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
$core = Get-ChildItem (Join-Path $root "pack\mods") -Filter "ninjacatskies-core-*.jar" | Select-Object -First 1
if (-not $core) {
    Add-Fail "Missing ninjacatskies-core-*.jar"
} else {
    $z = [System.IO.Compression.ZipFile]::OpenRead($core.FullName)
    try {
        $names = @($z.Entries | ForEach-Object { $_.FullName })
        foreach ($needle in @("ninjacatskies", "voidloom", "clowderhall", "ninjacatlib", "guardians")) {
            $hit = $names | Where-Object { $_ -match "META-INF/jarjar/$needle-" }
            if (-not $hit) { Add-Fail "$($core.Name) missing nested $needle jar" }
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
