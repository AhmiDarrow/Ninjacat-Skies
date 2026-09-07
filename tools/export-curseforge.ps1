# Build a CurseForge-importable client zip (manifest.json + overrides/).
# Excludes INTERNAL/, tools/, secrets, MDK, source trees, and agent notes.
#
# Modes:
#   CurseForge (default) — CF-hosted mods listed in manifest.files (downloaded by the app);
#                          custom / unresolved jars go in overrides/mods/.
#   SelfContained        — files=[]; every jar bundled under overrides/mods/ (offline import).
param(
    [string]$OutDir = "",
    [ValidateSet("CurseForge", "SelfContained")]
    [string]$Mode = "CurseForge",
    [switch]$SkipSanitize
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $SkipSanitize) {
    Write-Host "Running sanitization gate (no tokens / personal paths)..."
    & pwsh -NoProfile -File (Join-Path $PSScriptRoot "gates\Test-SanitizedPublicSurface.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Sanitization gate failed — refusing to export" }
}
if (-not $OutDir) { $OutDir = Join-Path $root "dist" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$packToml = Get-Content (Join-Path $root "pack\pack.toml") -Raw
$packVersion = "0.0.0"
if ($packToml -match '(?m)^version\s*=\s*"([^"]+)"') { $packVersion = $Matches[1] }
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stage = Join-Path $OutDir "stage-ninjacat-skies-$stamp"
$zipPath = Join-Path $OutDir "NinjacatSkies-$packVersion-$stamp.zip"
$stage = [IO.Path]::GetFullPath($stage)
$exportRoot = [IO.Path]::GetFullPath($OutDir).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if (-not $stage.StartsWith($exportRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Export staging directory must remain inside the output directory"
}
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $stage | Out-Null

# --- overrides (configs / KubeJS / resource packs / etc.) ---
Copy-Item (Join-Path $root "pack\overrides") (Join-Path $stage "overrides") -Recurse -Force
$ovMods = Join-Path $stage "overrides\mods"
New-Item -ItemType Directory -Force -Path $ovMods | Out-Null

# --- resolve which jars are CF-hosted vs local ---
$resolvedPath = Join-Path $root "pack\modlist-resolved.json"
$resolvedByFile = @{}
$resolved = @()
if (Test-Path $resolvedPath) {
    # Windows PowerShell 5.1 ConvertFrom-Json often returns a single Object[] that
    # does not enumerate in foreach / pipeline — unwrap with Write-Output.
    $resolved = @(Get-Content $resolvedPath -Raw | ConvertFrom-Json | Write-Output)
    foreach ($r in $resolved) {
        if (-not $r.filename) { continue }
        $resolvedByFile[[string]$r.filename] = $r
    }
}

$packMods = Join-Path $root "pack\mods"
$jars = @(Get-ChildItem $packMods -Filter "*.jar" -File -ErrorAction Stop)
if ($jars.Count -lt 1) { throw "No jars in pack/mods" }

$manifestFiles = New-Object System.Collections.Generic.List[object]
$bundled = New-Object System.Collections.Generic.List[string]

foreach ($jar in $jars) {
    $name = $jar.Name
    $entry = $resolvedByFile[$name]
    $projId = 0
    $fileId = 0
    $hasCfIds = $null -ne $entry `
        -and [int]::TryParse([string]$entry.projectId, [ref]$projId) -and $projId -gt 0 `
        -and [int]::TryParse([string]$entry.fileId, [ref]$fileId) -and $fileId -gt 0

    if ($name -like 'tribalpower-*' -and $null -ne $entry -and $projId -ne 1684851) {
        throw "Tribal Power dependency metadata must use CurseForge project 1684851"
    }

    if ($Mode -eq "CurseForge" -and $hasCfIds) {
        $manifestFiles.Add([ordered]@{
            projectID = $projId
            fileID    = $fileId
            required  = $true
        }) | Out-Null
    }
    else {
        Copy-Item $jar.FullName (Join-Path $ovMods $name) -Force
        $bundled.Add($name) | Out-Null
    }
}

# Prefer hand-authored pack/manifest.json only when it already has files; else build.
$manifestOut = Join-Path $stage "manifest.json"
$handAuthored = Join-Path $root "pack\manifest.json"
if ((Test-Path $handAuthored) -and $Mode -eq "CurseForge") {
    $existing = Get-Content $handAuthored -Raw | ConvertFrom-Json
    if ($existing.files -and @($existing.files).Count -gt 0) {
        Copy-Item $handAuthored $manifestOut -Force
        Write-Host "Using pack/manifest.json ($((@($existing.files)).Count) files)"
    }
}

$utf8 = New-Object System.Text.UTF8Encoding $false

if (-not (Test-Path $manifestOut)) {
    # Build JSON explicitly so key order stays CF-friendly and PS ordered-hashtable nesting does not blow up.
    $fileJsonParts = foreach ($f in $manifestFiles) {
        "{`"projectID`":$($f.projectID),`"fileID`":$($f.fileID),`"required`":true}"
    }
    $filesJson = "[" + ($fileJsonParts -join ",") + "]"
    # recommendedRam (MiB) is read by CurseForge / Prism as the author's recommended allocation.
    $json = @"
{
  "minecraft": {
    "version": "1.21.1",
    "modLoaders": [
      {
        "id": "neoforge-21.1.249",
        "primary": true
      }
    ],
    "recommendedRam": 8192
  },
  "manifestType": "minecraftModpack",
  "manifestVersion": 1,
  "name": "Ninjacat Skies",
  "version": "$packVersion",
  "author": "Ninjacat Skies",
  "files": $filesJson,
  "overrides": "overrides"
}
"@
    # UTF-8 no BOM (CF import can choke on BOM)
    [System.IO.File]::WriteAllText($manifestOut, $json, $utf8)
}

# --- pack icon (CF project / profile avatar) ---
# CF moderation requires square avatar >= 400x400. Ship root icon.png for import/profile.
$iconSrc = Join-Path $root "docs\public\pack-icon.png"
if (-not (Test-Path $iconSrc)) { $iconSrc = Join-Path $root "pack\overrides\pack-icon.png" }
if (Test-Path $iconSrc) {
    Copy-Item $iconSrc (Join-Path $stage "icon.png") -Force
    Copy-Item $iconSrc (Join-Path $stage "overrides\pack-icon.png") -Force
}

# --- CF author-console paste helpers (not auto-applied by zip import) ---
$descMd = Join-Path $root "docs\public\store-description.md"
$descHtml = Join-Path $root "docs\public\store-description.html"
if (Test-Path $descHtml) {
    Copy-Item $descHtml (Join-Path $stage "overrides\store-description.html") -Force
}
if (Test-Path $descMd) {
    Copy-Item $descMd (Join-Path $stage "overrides\store-description.md") -Force
}

# --- player install notes (RAM) ---
$installNotes = @"
Ninjacat Skies — install notes
==============================

Minecraft 1.21.1 · NeoForge 21.1.249

MEMORY (required)
  CurseForge App → Ninjacat Skies → ⋮ → Profile Options → Memory
  Prefer "Recommended by Author" (8 GB / 8192 MB from the pack manifest).
  Or Custom RAM Allocation = 8192 MB. 4096 MB is not enough.
  Minimum viable: 6144 MB. Recommended: 8192–10240 MB.

ICON
  Root icon.png + overrides/pack-icon.png ship the pack paw (512×512).
  CurseForge PROJECT page avatar/description must still be set in the
  Author Console (General + Description tabs) — zip import alone does not.

UI
  Enable the ninjacat-skies-ui resource pack if title/splashes look vanilla.

Full store blurb: see the project page / docs/public/store-description.md
"@
[System.IO.File]::WriteAllText((Join-Path $stage "overrides\INSTALL.txt"), $installNotes, $utf8)

# --- modlist.html (CF export convention) ---
$modRows = New-Object System.Collections.Generic.List[string]
if (Test-Path $resolvedPath) {
    foreach ($r in @($resolved | Sort-Object name, key)) {
        $cfProjectId = 0
        if (-not [int]::TryParse([string]$r.projectId, [ref]$cfProjectId) -or $cfProjectId -le 0) { continue }
        $safeName = [System.Net.WebUtility]::HtmlEncode([string]$r.name)
        $url = "https://www.curseforge.com/minecraft/mc-mods/$($r.slug)"
        $modRows.Add("<li><a href=`"$url`">$safeName</a> (file $($r.fileId))</li>") | Out-Null
    }
}
foreach ($name in ($bundled | Sort-Object)) {
    $safe = [System.Net.WebUtility]::HtmlEncode($name)
    $modRows.Add("<li>$safe <em>(bundled override)</em></li>") | Out-Null
}
$modlistHtml = @"
<ul>
$($modRows -join "`n")
</ul>
"@
[System.IO.File]::WriteAllText((Join-Path $stage "modlist.html"), $modlistHtml, $utf8)

# Sanitize stage: strip accidental internal / tooling files
Get-ChildItem $stage -Recurse -Force | Where-Object {
    $_.Name -match '^\.env$|\.key$|credentials' -or
    $_.FullName -match '\\INTERNAL\\|\\agent\\|requirements' -or
    $_.Extension -match '\.(ps1|py)$'
} | ForEach-Object {
    if (-not $_.FullName.StartsWith($stage + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a path outside export staging"
    }
    Remove-Item $_.FullName -Force -Recurse -ErrorAction SilentlyContinue
}

# Zip with forward-slash entries (Compress-Archive has broken CF imports before)
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem $stage -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($stage.Length).TrimStart("\", "/") -replace "\\", "/"
        [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip, $_.FullName, $rel, [System.IO.Compression.CompressionLevel]::Optimal)
    }
}
finally {
    $zip.Dispose()
}

Remove-Item $stage -Recurse -Force

# Re-open to report counts
$check = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $e = $check.GetEntry("manifest.json")
    $sr = New-Object System.IO.StreamReader($e.Open())
    $parsed = $sr.ReadToEnd() | ConvertFrom-Json
    $sr.Close()
    $ovCount = @($check.Entries | Where-Object { $_.FullName -like "overrides/mods/*" }).Count
    $topMods = @($check.Entries | Where-Object { $_.FullName -like "mods/*" -and $_.FullName -notlike "overrides/*" }).Count
}
finally {
    $check.Dispose()
}

Write-Host "Exported $zipPath"
Write-Host "Mode=$Mode  manifest.files=$((@($parsed.files)).Count)  overrides/mods=$ovCount  top-level mods/=$topMods (must be 0)"
Write-Host "Store blurb: docs/public/store-description.md"
if ($topMods -gt 0) { throw "Export produced illegal top-level mods/ entries" }
exit 0
