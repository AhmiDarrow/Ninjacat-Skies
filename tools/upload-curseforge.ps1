# Upload a Ninjacat Skies CurseForge zip via the Author Upload API.
# Requires: CF_AUTHOR_TOKEN + CF_PROJECT_ID in tools/secrets/.env
# Project creation is UI-only: https://authors.curseforge.com/#/projects/create/choose-game
param(
    [string]$ZipPath = "",
    [int]$ProjectId = 0,
    [ValidateSet("alpha", "beta", "release")]
    [string]$ReleaseType = "alpha",
    [string]$DisplayName = "",
    [string]$Changelog = "",
    [switch]$SkipExport
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "Running sanitization gate (no tokens / personal paths)..."
& pwsh -NoProfile -File (Join-Path $PSScriptRoot "gates\Test-SanitizedPublicSurface.ps1")
if ($LASTEXITCODE -ne 0) { throw "Sanitization gate failed — refusing to upload" }

. (Join-Path $PSScriptRoot "Load-Secrets.ps1")

if (-not $env:CF_AUTHOR_TOKEN) {
    throw "Author upload token missing from tools/secrets/.env (https://www.curseforge.com/account/api-tokens)"
}
if ($ProjectId -le 0 -and $env:CF_PROJECT_ID) {
    [void][int]::TryParse($env:CF_PROJECT_ID, [ref]$ProjectId)
}
if ($ProjectId -le 0) {
    throw @"
CurseForge project id is not set. Projects cannot be created via API.

1. Open https://authors.curseforge.com/#/projects/create/choose-game
2. Create a Minecraft Modpack named Ninjacat Skies
3. Copy the numeric project id from the project URL / Overview sidebar
4. Set CF_PROJECT_ID in tools/secrets/.env (see .env.example)
5. Re-run: pwsh -File tools/upload-curseforge.ps1
"@
}

if (-not $SkipExport -and -not $ZipPath) {
    Write-Host "Exporting fresh CurseForge zip..."
    & pwsh -NoProfile -File (Join-Path $PSScriptRoot "export-curseforge.ps1") -Mode CurseForge
    if ($LASTEXITCODE -ne 0) { throw "export-curseforge.ps1 failed ($LASTEXITCODE)" }
    $ZipPath = @(Get-ChildItem (Join-Path $root "dist") -Filter "NinjacatSkies-0.1.0-alpha-*.zip" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1 -ExpandProperty FullName)
}
if (-not $ZipPath -or -not (Test-Path $ZipPath)) {
    throw "Zip not found. Pass -ZipPath or allow export."
}
$ZipPath = (Resolve-Path $ZipPath).Path
$zipName = [IO.Path]::GetFileNameWithoutExtension($ZipPath)
if (-not $DisplayName) { $DisplayName = $zipName }
if (-not $Changelog) {
    $Changelog = @"
## Ninjacat Skies $DisplayName

- Void-island NeoForge 1.21.1 quest pack
- Tribal Power 2.0 (shamanic technomancy rewrite) bundled
- FancyMenu welcome + guided Create Team pad claim
- Recommended RAM: 8 GB
"@
}

# Prefer Minecraft 1.21 type (77784) over Bukkit/Addon duplicate names.
$token = $env:CF_AUTHOR_TOKEN
$headers = @{
    "X-Api-Token" = $token
    "Accept"      = "application/json"
    "User-Agent"  = "ninjacat-skies-uploader/0.1"
}
$versions = Invoke-RestMethod -Uri "https://minecraft.curseforge.com/api/game/versions" -Headers $headers
function Resolve-VersionId([string]$Name, [int]$TypeId) {
    $hit = @($versions | Where-Object { $_.name -eq $Name -and $_.gameVersionTypeID -eq $TypeId } | Select-Object -First 1)
    if (-not $hit) {
        $hit = @($versions | Where-Object { $_.name -eq $Name } | Select-Object -First 1)
    }
    if (-not $hit) { throw "Could not resolve game version '$Name' (type $TypeId)" }
    return [int]$hit.id
}
# Modpacks only accept Minecraft + modloader version IDs (Java/Client/Server → error 1009).
$gameVersionIds = @(
    (Resolve-VersionId "1.21.1" 77784),
    (Resolve-VersionId "NeoForge" 68441)
)

$metadata = @{
    changelog       = $Changelog
    changelogType   = "markdown"
    displayName     = $DisplayName
    gameVersions    = $gameVersionIds
    releaseType     = $ReleaseType
} | ConvertTo-Json -Compress

Write-Host "Uploading $ZipPath"
Write-Host "  projectId=$ProjectId releaseType=$ReleaseType gameVersions=$($gameVersionIds -join ',')"

# curl.exe handles multipart reliably on Windows; Invoke-RestMethod multipart is fragile on PS 5.1.
$uploadUrl = "https://minecraft.curseforge.com/api/projects/$ProjectId/upload-file"
$metaFile = Join-Path $env:TEMP "ncs-cf-upload-meta-$PID.json"
Set-Content -Path $metaFile -Value $metadata -Encoding utf8NoBOM
try {
    $curlOut = & curl.exe -sS -X POST $uploadUrl `
        -H "X-Api-Token: $token" `
        -H "Accept: application/json" `
        -H "User-Agent: ninjacat-skies-uploader/0.1" `
        -F "metadata=<$metaFile;type=application/json" `
        -F "file=@$ZipPath;type=application/zip" `
        --max-time 600
    if ($LASTEXITCODE -ne 0) { throw "curl upload failed exit=$LASTEXITCODE`n$curlOut" }
    Write-Host "Response: $curlOut"
    $parsed = $curlOut | ConvertFrom-Json
    if (-not $parsed.id) { throw "Upload response missing file id: $curlOut" }
    Write-Host "OK — CurseForge file id=$($parsed.id)"
    Write-Output $parsed
}
finally {
    Remove-Item $metaFile -Force -ErrorAction SilentlyContinue
}
