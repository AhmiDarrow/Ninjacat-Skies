#Requires -Version 5.1
<#
.SYNOPSIS
  Resolve and download NeoForge 1.21.1 CurseForge mods into pack/mods.
.NOTES
  Dot-sources tools/Load-Secrets.ps1 for CF_API_KEY.
  Writes pack/modlist-resolved.json and pack/mod-download-skips.txt.
#>
param(
    [string]$GameVersion = "1.21.1",
    [int]$ModLoaderType = 6, # NeoForge
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "Load-Secrets.ps1")

$ApiBase = "https://api.curseforge.com/v1"
$Headers = @{
    "x-api-key" = $env:CF_API_KEY
    "Accept"    = "application/json"
}
$ModsDir = Join-Path $ProjectRoot "pack\mods"
$ResolvedPath = Join-Path $ProjectRoot "pack\modlist-resolved.json"
$SkipsPath = Join-Path $ProjectRoot "pack\mod-download-skips.txt"

New-Item -ItemType Directory -Force -Path $ModsDir | Out-Null

# Preferred CurseForge slugs (more reliable than free-text search).
$ModTargets = @(
    @{ Key = "Ex Deorum";              Slugs = @("ex-deorum"); Search = "Ex Deorum" }
    @{ Key = "Skyblock Builder";       Slugs = @("skyblock-builder"); Search = "Skyblock Builder" }
    @{ Key = "LibX";                   Slugs = @("libx"); Search = "LibX" }
    @{ Key = "Sky GUIs";               Slugs = @("sky-guis"); Search = "Sky GUIs" }
    @{ Key = "FTB Library";            Slugs = @("ftb-library-forge", "ftb-library"); Search = "FTB Library" }
    @{ Key = "FTB Teams";              Slugs = @("ftb-teams-forge", "ftb-teams"); Search = "FTB Teams" }
    @{ Key = "FTB Chunks";             Slugs = @("ftb-chunks-forge", "ftb-chunks"); Search = "FTB Chunks" }
    @{ Key = "FTB Quests";             Slugs = @("ftb-quests-forge", "ftb-quests"); Search = "FTB Quests" }
    @{ Key = "JEI";                    Slugs = @("jei"); Search = "Just Enough Items" }
    @{ Key = "Architectury API";       Slugs = @("architectury-api"); Search = "Architectury API" }
    @{ Key = "Cloth Config API";       Slugs = @("cloth-config"); Search = "Cloth Config API" }
    @{ Key = "Balm";                   Slugs = @("balm"); Search = "Balm" }
    @{ Key = "ModernFix";              Slugs = @("modernfix"); Search = "ModernFix" }
    @{ Key = "FerriteCore";            Slugs = @("ferritecore"); Search = "FerriteCore" }
    @{ Key = "Entity Culling";         Slugs = @("entityculling"); Search = "Entity Culling" }
    @{ Key = "ImmediatelyFast";        Slugs = @("immediatelyfast"); Search = "ImmediatelyFast" }
    @{ Key = "Jade";                   Slugs = @("jade"); Search = "Jade" }
    @{ Key = "AppleSkin";              Slugs = @("appleskin"); Search = "AppleSkin" }
    @{ Key = "Mystical Agriculture";   Slugs = @("mystical-agriculture"); Search = "Mystical Agriculture" }
    @{ Key = "Cucumber Library";       Slugs = @("cucumber"); Search = "Cucumber Library" }
    @{ Key = "Farmer's Delight";       Slugs = @("farmers-delight"); Search = "Farmer's Delight" }
    @{ Key = "Create";                 Slugs = @("create"); Search = "Create" }
    @{ Key = "Applied Energistics 2";  Slugs = @("applied-energistics-2"); Search = "Applied Energistics 2" }
    @{ Key = "Almost Unified";         Slugs = @("almostunified", "almost-unified"); Search = "Almost Unified" }
    @{ Key = "KubeJS";                 Slugs = @("kubejs"); Search = "KubeJS" }
    @{ Key = "Rhino";                  Slugs = @("rhino"); Search = "Rhino" }
    @{ Key = "Forgiving Void";         Slugs = @("forgiving-void"); Search = "Forgiving Void" }
    @{ Key = "Functional Storage";     Slugs = @("functional-storage"); Search = "Functional Storage" }
    # Botania / Tinkers / Mantle: no 1.21.1 NeoForge — see INTERNAL/MOD_SUBSTITUTIONS.md
    # (Nature's Aura + Silent Gear). Listed in pack/mod-download-skips.txt.
    @{ Key = "Ars Nouveau";            Slugs = @("ars-nouveau"); Search = "Ars Nouveau" }
    @{ Key = "Productive Bees";        Slugs = @("productivebees"); Search = "Productive Bees" }
    @{ Key = "Konkrete";               Slugs = @("konkrete"); Search = "Konkrete" }
    @{ Key = "Melody";                 Slugs = @("melody"); Search = "Melody" }
    @{ Key = "FancyMenu";              Slugs = @("fancymenu"); Search = "FancyMenu" }
    # Content that was dropped in manually (needs CF file IDs + deps)
    @{ Key = "Botany Pots";            Slugs = @("botany-pots"); Search = "Botany Pots" }
    @{ Key = "Curios API";             Slugs = @("curios"); Search = "Curios API" }
    @{ Key = "Iron's Spells 'n Spellbooks"; Slugs = @("irons-spells-n-spellbooks"); Search = "Iron's Spells n Spellbooks" }
    @{ Key = "Mekanism";               Slugs = @("mekanism"); Search = "Mekanism" }
    @{ Key = "Mekanism Tools";         Slugs = @("mekanism-tools"); Search = "Mekanism Tools" }
    @{ Key = "Nature's Aura";          Slugs = @("natures-aura"); Search = "Nature's Aura" }
    @{ Key = "Occultism";              Slugs = @("occultism"); Search = "Occultism" }
    @{ Key = "PackagedAuto";           Slugs = @("packagedauto"); Search = "PackagedAuto" }
    @{ Key = "Pipez";                  Slugs = @("pipez"); Search = "Pipez" }
    @{ Key = "Powah";                  Slugs = @("powah-rearchitected", "powah"); Search = "Powah" }
    @{ Key = "Silent Gear";            Slugs = @("silent-gear"); Search = "Silent Gear" }
    @{ Key = "Silent Lib";             Slugs = @("silent-lib"); Search = "Silent Lib" }
    @{ Key = "Solar Flux Reborn";      Slugs = @("solar-flux-reborn"); Search = "Solar Flux Reborn" }
    @{ Key = "Sophisticated Backpacks"; Slugs = @("sophisticated-backpacks"); Search = "Sophisticated Backpacks" }
    @{ Key = "Sophisticated Core";     Slugs = @("sophisticated-core"); Search = "Sophisticated Core" }
    # Mandatory libraries reported missing by FML on first client boot
    @{ Key = "Patchouli";              Slugs = @("patchouli"); Search = "Patchouli" }
    @{ Key = "Bookshelf";              Slugs = @("bookshelf"); Search = "Bookshelf" }
    @{ Key = "HammerLib";              Slugs = @("hammer-lib", "hammerlib"); Search = "HammerLib" }
    @{ Key = "Prickle";                Slugs = @("prickle"); Search = "Prickle" }
    @{ Key = "Iron's Lib";             Slugs = @("irons-lib", "irons-spells-lib"); Search = "Iron's Lib" }
    @{ Key = "SmartBrainLib";          Slugs = @("smartbrainlib"); Search = "SmartBrainLib" }
    @{ Key = "GeckoLib";               Slugs = @("geckolib"); Search = "GeckoLib" }
    @{ Key = "GuideME";                Slugs = @("guideme"); Search = "GuideME" }
    @{ Key = "Titanium";               Slugs = @("titanium"); Search = "Titanium" }
    @{ Key = "Player Animator";        Slugs = @("playeranimator", "player-animator"); Search = "Player Animator" }
    @{ Key = "Modonomicon";            Slugs = @("modonomicon"); Search = "Modonomicon" }
    # --- added 0.3.0 (resolve CF ids on a machine with CurseForge access) ---
    @{ Key = "Chipped";                Slugs = @("chipped"); Search = "Chipped" }
    @{ Key = "Athena";                 Slugs = @("athena-ctm","athena"); Search = "Athena" }
    @{ Key = "Supplementaries";        Slugs = @("supplementaries"); Search = "Supplementaries" }
    @{ Key = "Moonlight Lib";          Slugs = @("selene","moonlight"); Search = "Moonlight Lib" }
    @{ Key = "Amendments";             Slugs = @("amendments"); Search = "Amendments" }
    @{ Key = "Handcrafted";            Slugs = @("handcrafted"); Search = "Handcrafted" }
    @{ Key = "Macaw's Bridges";        Slugs = @("macaws-bridges"); Search = "Macaws Bridges" }
    @{ Key = "Macaw's Roofs";          Slugs = @("macaws-roofs"); Search = "Macaws Roofs" }
    @{ Key = "FramedBlocks";           Slugs = @("framedblocks"); Search = "FramedBlocks" }
    @{ Key = "Sophisticated Storage";  Slugs = @("sophisticated-storage"); Search = "Sophisticated Storage" }
    @{ Key = "Modular Routers";        Slugs = @("modular-routers"); Search = "Modular Routers" }
    @{ Key = "Create Crafts & Additions"; Slugs = @("create-crafts-additions","createaddition"); Search = "Create Crafts Additions" }
    @{ Key = "Create Enchantment Industry"; Slugs = @("create-enchantment-industry"); Search = "Create Enchantment Industry" }
    @{ Key = "Create Dragons Lib";     Slugs = @("create-dragons-plus","create-dragon-lib"); Search = "Create Dragons" }
    @{ Key = "Mekanism Generators";    Slugs = @("mekanism-generators"); Search = "Mekanism Generators" }
    @{ Key = "Applied Mekanistics";    Slugs = @("applied-mekanistics"); Search = "Applied Mekanistics" }
    @{ Key = "AE2 Wireless Terminals"; Slugs = @("ae2wtlib","applied-energistics-2-wireless-terminals"); Search = "AE2WTLib" }
    @{ Key = "Xaero's Minimap";        Slugs = @("xaeros-minimap"); Search = "Xaeros Minimap" }
    @{ Key = "Xaero's World Map";      Slugs = @("xaeros-world-map"); Search = "Xaeros World Map" }
    @{ Key = "Clumps";                 Slugs = @("clumps"); Search = "Clumps" }
    @{ Key = "Controlling";            Slugs = @("controlling"); Search = "Controlling" }
    @{ Key = "Mouse Tweaks";           Slugs = @("mouse-tweaks"); Search = "Mouse Tweaks" }
    @{ Key = "TrashSlot";              Slugs = @("trashslot"); Search = "TrashSlot" }
    @{ Key = "Just Enough Resources";  Slugs = @("just-enough-resources-jer"); Search = "Just Enough Resources" }
    @{ Key = "Just Enough Professions"; Slugs = @("just-enough-professions-jep"); Search = "Just Enough Professions" }
    @{ Key = "Comforts";               Slugs = @("comforts"); Search = "Comforts" }
    @{ Key = "Resourceful Lib";        Slugs = @("resourceful-lib"); Search = "Resourceful Lib" }
    @{ Key = "Searchables";            Slugs = @("searchables"); Search = "Searchables" }

)

function Invoke-CfGet {
    param([string]$Path)
    $uri = if ($Path.StartsWith("http")) { $Path } else { "$ApiBase$Path" }
    return Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get
}

function Find-ModProject {
    param($Target)

    foreach ($slug in $Target.Slugs) {
        $encoded = [uri]::EscapeDataString($slug)
        $resp = Invoke-CfGet "/mods/search?gameId=432&classId=6&slug=$encoded"
        if ($resp.data -and $resp.data.Count -gt 0) {
            $exact = $resp.data | Where-Object { $_.slug -eq $slug } | Select-Object -First 1
            if ($exact) { return $exact }
            return $resp.data[0]
        }
    }

    $q = [uri]::EscapeDataString($Target.Search)
    $resp = Invoke-CfGet "/mods/search?gameId=432&classId=6&searchFilter=$q&sortField=2&sortOrder=desc&pageSize=25"
    if (-not $resp.data -or $resp.data.Count -eq 0) { return $null }

    $searchLower = $Target.Search.ToLowerInvariant()
    $exactName = $resp.data | Where-Object { $_.name.ToLowerInvariant() -eq $searchLower } | Select-Object -First 1
    if ($exactName) { return $exactName }

    foreach ($slug in $Target.Slugs) {
        $bySlug = $resp.data | Where-Object { $_.slug -eq $slug } | Select-Object -First 1
        if ($bySlug) { return $bySlug }
    }

    $contains = $resp.data | Where-Object {
        $_.name.ToLowerInvariant().Contains($searchLower) -or
        $searchLower.Contains($_.name.ToLowerInvariant())
    } | Select-Object -First 1
    if ($contains) { return $contains }

    return $resp.data[0]
}

function Test-FileMatches {
    param($File, [string]$Version, [int]$LoaderType)

    $versions = @($File.gameVersions)
    $hasVersion = $versions -contains $Version
    $hasNeo = ($versions -contains "NeoForge") -or ($File.fileName -match "(?i)neoforge")
    # modLoaderType on file objects: 1=Forge, 4=Fabric, 6=NeoForge (when present)
    if ($null -ne $File.gameVersions) {
        # Also check modules / sortableGameVersions if available
    }
    if ($File.PSObject.Properties.Name -contains "sortableGameVersions" -and $File.sortableGameVersions) {
        $neoEntry = $File.sortableGameVersions | Where-Object {
            $_.gameVersion -eq $Version -and (
                $_.gameVersionName -match "(?i)neoforge" -or
                $_.gameVersionTypeId -eq 1 # MC version type; loader often in gameVersionName
            )
        }
        # Prefer explicit NeoForge tag in gameVersions list
    }
    return ($hasVersion -and $hasNeo)
}

function Get-BestNeoFile {
    param([int]$ModId, [string]$Version, [int]$LoaderType)

    $all = @()
    $index = 0
    do {
        $resp = Invoke-CfGet "/mods/$ModId/files?gameVersion=$Version&modLoaderType=$LoaderType&pageSize=50&index=$index"
        if ($resp.data) { $all += $resp.data }
        $batch = if ($resp.data) { $resp.data.Count } else { 0 }
        $index += $batch
        $total = 0
        if ($resp.pagination) { $total = [int]$resp.pagination.totalCount }
    } while ($batch -eq 50 -and $index -lt $total)

    if ($all.Count -eq 0) {
        # Fallback: no loader filter, then filter client-side
        $index = 0
        do {
            $resp = Invoke-CfGet "/mods/$ModId/files?gameVersion=$Version&pageSize=50&index=$index"
            if ($resp.data) {
                foreach ($f in $resp.data) {
                    if (Test-FileMatches -File $f -Version $Version -LoaderType $LoaderType) {
                        $all += $f
                    }
                }
            }
            $batch = if ($resp.data) { $resp.data.Count } else { 0 }
            $index += $batch
            $total = 0
            if ($resp.pagination) { $total = [int]$resp.pagination.totalCount }
        } while ($batch -eq 50 -and $index -lt $total)
    }

    if ($all.Count -eq 0) { return $null }

    # Prefer newest NeoForge build first (file id). Release-type is only a tiebreaker so
    # we do not pin an older Release over a newer Beta/Alpha (LibX 6.0.9 vs 6.0.15).
    $sorted = $all | Sort-Object `
        @{ Expression = { [int64]$_.id }; Descending = $true }, `
        @{ Expression = {
            switch ([int]$_.releaseType) { 1 { 0 } 2 { 1 } 3 { 2 } default { 3 } }
        } }

    return $sorted | Select-Object -First 1
}

function Get-CdnCandidates {
    param([int]$FileId, [string]$FileName)

    $idStr = $FileId.ToString()
    if ($idStr.Length -lt 4) { return @() }
    $a = $idStr.Substring(0, 4)
    $b = $idStr.Substring(4)
    $bTrim = $b.TrimStart('0')
    if (-not $bTrim) { $bTrim = "0" }
    # Prefer literal filename; some CDNs need + encoded
    $names = @($FileName, ($FileName -replace '\+','%2B'))
    $urls = @()
    foreach ($n in $names) {
        $urls += "https://mediafilez.forgecdn.net/files/$a/$b/$n"
        $urls += "https://edge.forgecdn.net/files/$a/$b/$n"
        if ($bTrim -ne $b) {
            $urls += "https://mediafilez.forgecdn.net/files/$a/$bTrim/$n"
            $urls += "https://edge.forgecdn.net/files/$a/$bTrim/$n"
        }
    }
    return $urls | Select-Object -Unique
}

function Get-DownloadUrl {
    param([int]$ModId, [int]$FileId, $File)

    $candidates = @()
    if ($File.downloadUrl) { $candidates += $File.downloadUrl }

    try {
        $resp = Invoke-CfGet "/mods/$ModId/files/$FileId/download-url"
        if ($resp.data) { $candidates += $resp.data }
    }
    catch {
        # Some projects disallow the download-url endpoint (403); use CDN mirrors.
    }

    $candidates += Get-CdnCandidates -FileId $FileId -FileName $File.fileName
    return @($candidates | Where-Object { $_ } | Select-Object -Unique)
}

function Save-ModFile {
    param([string[]]$Urls, [string]$Dest)

    $lastError = $null
    foreach ($url in $Urls) {
        try {
            Write-Host "  Downloading: $url"
            Invoke-WebRequest -Uri $url -OutFile $Dest -Headers @{ "x-api-key" = $env:CF_API_KEY } -UseBasicParsing
            if (Test-Path $Dest) { return $true }
        }
        catch {
            $lastError = $_
            Write-Host "  CDN miss: $($_.Exception.Message)" -ForegroundColor DarkYellow
        }
    }
    if ($lastError) { throw $lastError }
    throw "No download URL worked"
}

$resolved = @()
$skips = @()
$downloaded = @()
$skippedNames = @()

Write-Host "Downloading NeoForge $GameVersion mods into $ModsDir"
Write-Host ("=" * 60)

foreach ($target in $ModTargets) {
    $key = $target.Key
    Write-Host "`n[$key]"

    try {
        $project = Find-ModProject -Target $target
        if (-not $project) {
            $msg = "$key : project not found on CurseForge"
            Write-Host "  SKIP: $msg" -ForegroundColor Yellow
            $skips += $msg
            $skippedNames += $key
            continue
        }

        Write-Host "  Project: $($project.name) (id=$($project.id), slug=$($project.slug))"
        $file = Get-BestNeoFile -ModId ([int]$project.id) -Version $GameVersion -LoaderType $ModLoaderType
        if (-not $file) {
            $msg = "$key ($($project.slug)/$($project.id)) : no $GameVersion NeoForge file"
            Write-Host "  SKIP: $msg" -ForegroundColor Yellow
            $skips += $msg
            $skippedNames += $key
            continue
        }

        $fileName = $file.fileName
        $dest = Join-Path $ModsDir $fileName
        Write-Host "  File: $fileName (fileId=$($file.id), releaseType=$($file.releaseType))"

        if ((Test-Path $dest) -and -not $Force) {
            Write-Host "  Already present - skipping download"
        }
        else {
            $urls = Get-DownloadUrl -ModId ([int]$project.id) -FileId ([int]$file.id) -File $file
            if (-not $urls -or $urls.Count -eq 0) {
                $msg = "$key ($fileName) : no download URL"
                Write-Host "  SKIP: $msg" -ForegroundColor Yellow
                $skips += $msg
                $skippedNames += $key
                continue
            }
            Save-ModFile -Urls $urls -Dest $dest | Out-Null
        }

        $expectedSha1 = @($file.hashes | Where-Object { $_.algo -eq 1 } | Select-Object -First 1)
        $actualSha1 = (Get-FileHash -LiteralPath $dest -Algorithm SHA1).Hash.ToLowerInvariant()
        if ($expectedSha1.Count -ne 1 -or $expectedSha1[0].value.ToLowerInvariant().PadLeft(40, '0') -ne $actualSha1) {
            throw "Local jar does not match its official CurseForge SHA-1; use -Force to download the official file"
        }
        $entry = [ordered]@{
            key       = $key
            name      = $project.name
            slug      = $project.slug
            projectId = [int]$project.id
            fileId    = [int]$file.id
            filename  = $fileName
            releaseType = [int]$file.releaseType
            sha1 = $actualSha1
        }
        $resolved += [pscustomobject]$entry
        $downloaded += $key
        Write-Host "  OK" -ForegroundColor Green
    }
    catch {
        $msg = "$key : error - $($_.Exception.Message)"
        Write-Host "  SKIP: $msg" -ForegroundColor Red
        $skips += $msg
        $skippedNames += $key
    }
}

$resolved | ConvertTo-Json -Depth 5 | Set-Content -Path $ResolvedPath -Encoding UTF8
$skips | Set-Content -Path $SkipsPath -Encoding UTF8

Write-Host ("`n" + ("=" * 60))
Write-Host "Done. Resolved: $($resolved.Count)  Skipped: $($skips.Count)"
Write-Host "Wrote $ResolvedPath"
Write-Host "Wrote $SkipsPath"
Write-Host "`nDownloaded/resolved:"
$downloaded | ForEach-Object { Write-Host "  + $_" }
if ($skippedNames.Count -gt 0) {
    Write-Host "`nSkipped:"
    $skippedNames | ForEach-Object { Write-Host "  - $_" }
}
