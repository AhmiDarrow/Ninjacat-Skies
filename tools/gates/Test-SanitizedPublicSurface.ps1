# Gate: public/shipped surfaces and push-safe tree must not leak
# tokens, personal directories, secrets, or forbidden pack names.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$failures = [System.Collections.Generic.List[string]]::new()

# Brand / process leaks (case-insensitive)
$forbiddenNames = @(
    'agrarian',
    'jadedcat',
    'jaded packs',
    'skyopolis',
    'ftb skies',
    'project ozone',
    'hypnotizd',
    'spiritual successor',
    'agent conversation',
    'plan mode',
    'subagent',
    'INTERNAL/',
    'Load-Secrets',
    'grok/sessions',
    '\.grok[/\\]sessions'
)

# Secret / PII patterns — fail anywhere that could be committed or shipped
$secretPatterns = @(
    @{ Name = 'bcrypt-hash';           Regex = '\$2a\$\d{2}\$' },
    @{ Name = 'CF_API_KEY-assignment';  Regex = 'CF_API_KEY\s*=\s*\S+' },
    @{ Name = 'CF_AUTHOR_TOKEN-assignment'; Regex = 'CF_AUTHOR_TOKEN\s*=\s*\S+' },
    @{ Name = 'CF_PROJECT_ID-assignment'; Regex = 'CF_PROJECT_ID\s*=\s*\d+' },
    @{ Name = 'github-pat';             Regex = 'ghp_[A-Za-z0-9]{20,}' },
    @{ Name = 'github-fine-grained-pat'; Regex = 'github_pat_[A-Za-z0-9_]{20,}' },
    @{ Name = 'openai-style-key';       Regex = 'sk-[A-Za-z0-9]{20,}' },
    @{ Name = 'private-key-block';      Regex = 'BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY' },
    @{ Name = 'windows-user-profile';   Regex = '(?i)C:[\\/]Users[\\/][^\\/\s"''`]+' },
    @{ Name = 'unix-user-home';         Regex = '(?i)(?:/Users|/home)/[^/\s"''`]+' },
    @{ Name = 'grok-session-path';      Regex = '(?i)\.grok[\\/]+sessions' }
)

# Paths that may mention secret *names* (headers/env docs) but never values
$toolAllowlist = @(
    '\\tools\\Load-Secrets\.ps1$',
    '\\tools\\upload-curseforge\.ps1$',
    '\\tools\\download-mods\.ps1$',
    '\\tools\\export-curseforge\.ps1$',
    '\\tools\\gates\\',
    '\\tools\\secrets\\\.env\.example$'
)

$publicScanRoots = @(
    (Join-Path $root "pack\overrides"),
    (Join-Path $root "mods"),
    (Join-Path $root "docs"),
    (Join-Path $root "README.md"),
    (Join-Path $root "pack\pack.toml")
)

# Whole-repo push scan (relative dirs). Secrets .env is excluded + must stay gitignored.
$pushScanDirs = @(
    "pack\overrides",
    "mods",
    "docs",
    "art",
    "INTERNAL",
    "tools",
    "README.md",
    ".gitignore"
)

function Add-Fail([string]$msg) { [void]$failures.Add($msg) }

function Test-IsToolAllowlisted([string]$fullPath) {
    $norm = $fullPath.Replace('/', '\')
    foreach ($pat in $toolAllowlist) {
        if ($norm -match $pat) { return $true }
    }
    return $false
}

function Test-IsTextish([System.IO.FileInfo]$file) {
    $p = $file.FullName
    if ($p -match '\\(build|\.gradle|run|runs|mdk-extract|dist|node_modules|\.git)\\') { return $false }
    if ($p -match '\\pack\\mods\\.*\.jar$') { return $false }
    if ($file.Extension -match '\.(jar|class|png|nbt|zip|exe|dll|gguf|bin|jar\.original)$') { return $false }
    if ($file.Name -eq '.env') { return $false } # handled separately
    return $file.Extension -match '\.(md|txt|json|json5|snbt|js|java|toml|gradle|properties|lang|ps1|py|html|xml|yml|yaml|cfg|example)$' `
        -or $file.Name -match '^(README|LICENSE|\.gitignore)$'
}

# 1) INTERNAL / secrets must never sit under pack/overrides
$leak = Get-ChildItem (Join-Path $root "pack\overrides") -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\INTERNAL\\|\\secrets\\|agent.conversation|requirements\.md' }
foreach ($f in $leak) {
    Add-Fail "Internal path leaked into overrides: $($f.FullName.Substring($root.Length))"
}

# 2) No secrets file under pack/
$secretHits = Get-ChildItem (Join-Path $root "pack") -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^\.env$|\.key$|credentials' -or $_.FullName -match '\\secrets\\' }
foreach ($f in $secretHits) {
    Add-Fail "Secret-like file under pack/: $($f.FullName.Substring($root.Length))"
}

# 3) secrets/.env must exist only locally and must be gitignored
$envFile = Join-Path $root "tools\secrets\.env"
if (Test-Path $envFile) {
    Push-Location $root
    try {
        $ignored = & git check-ignore -q "tools/secrets/.env" 2>$null
        $code = $LASTEXITCODE
        # check-ignore: 0 = ignored, 1 = not ignored, 128 = not a git repo / error
        if ($code -eq 1) {
            Add-Fail "tools/secrets/.env is NOT gitignored — will leak tokens on push"
        }
        elseif ($code -eq 0 -or $code -eq 128) {
            # ignored or no git yet — OK; still refuse if staged/tracked when git works
            if ($code -eq 0) {
                $tracked = & git ls-files -- "tools/secrets/.env" 2>$null
                if ($tracked) {
                    Add-Fail "tools/secrets/.env is tracked by git — remove from index before push"
                }
            }
        }
    } finally {
        Pop-Location
    }
}

# 4) Brand/process names on public surfaces only
foreach ($scan in $publicScanRoots) {
    if (-not (Test-Path $scan)) { continue }
    $files = @()
    if (Test-Path $scan -PathType Leaf) {
        $files = @(Get-Item $scan)
    } else {
        $files = Get-ChildItem $scan -Recurse -File -ErrorAction SilentlyContinue | Where-Object { Test-IsTextish $_ }
    }
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        foreach ($pat in $forbiddenNames) {
            if ($content -match $pat) {
                Add-Fail ("{0} matches /{1}/" -f $file.FullName.Substring($root.Length), $pat)
            }
        }
    }
}

# 5) Secret / personal-directory scan across push tree (incl. INTERNAL + tools)
foreach ($rel in $pushScanDirs) {
    $scan = Join-Path $root $rel
    if (-not (Test-Path $scan)) { continue }
    $files = @()
    if (Test-Path $scan -PathType Leaf) {
        $files = @(Get-Item $scan)
    } else {
        $files = Get-ChildItem $scan -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {
            if ($_.FullName -match '\\tools\\secrets\\.env$') { return $false }
            if ($_.FullName -match '\\tools\\mdk-extract\\') { return $false }
            if ($_.FullName -match '\\INTERNAL\\_((skyblockbuilder_jar_extract|fm_ref|sb_ref|sb_cmd|sg_cmd|fm_btn))\\') { return $false }
            Test-IsTextish $_
        }
    }
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        $allowTool = Test-IsToolAllowlisted $file.FullName
        foreach ($sp in $secretPatterns) {
            # Tool scripts may document env var *names* and header names, not assignments with values
            if ($allowTool -and $sp.Name -match 'assignment$') {
                # still forbid real-looking assignments in tool scripts (placeholders OK)
                if ($content -match $sp.Regex) {
                    # allow .env.example placeholders like CF_API_KEY=your-key-here
                    $badAssign = [regex]::Matches($content, $sp.Regex) | Where-Object {
                        $_.Value -notmatch '=\s*(your-|changeme|TODO|<.*>|placeholder|\.\.\.)'
                    }
                    if ($badAssign.Count -gt 0) {
                        Add-Fail ("{0} has {1}: {2}" -f $file.FullName.Substring($root.Length), $sp.Name, $badAssign[0].Value)
                    }
                }
                continue
            }
            if ($allowTool -and $sp.Name -in @('windows-user-profile', 'unix-user-home')) {
                # tools should also stay free of personal paths
            }
            if ($content -match $sp.Regex) {
                # Skip header-name-only mentions in allowlisted tools for non-assignment patterns that are too broad
                if ($allowTool -and $sp.Name -eq 'openai-style-key' -and $content -notmatch 'sk-[A-Za-z0-9]{20,}') {
                    continue
                }
                Add-Fail ("{0} matches secret/PII pattern {1}" -f $file.FullName.Substring($root.Length), $sp.Name)
            }
        }
    }
}

# 6) Custom mod resources must not embed INTERNAL docs
$resourceDocs = Get-ChildItem (Join-Path $root "mods") -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\src\\main\\resources\\' -and $_.Name -match '\.(md|txt)$' }
foreach ($f in $resourceDocs) {
    # FTB Quests consumes this exact .txt path as runtime theme configuration.
    if ($f.FullName -match '\\assets\\ftbquests\\ftb_quests_theme\.txt$') { continue }
    Add-Fail "Unexpected doc in mod resources (would ship in jar): $($f.FullName.Substring($root.Length))"
}

if ($failures.Count -gt 0) {
    Write-Host "FAIL Test-SanitizedPublicSurface ($($failures.Count) issue(s))"
    $failures | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host "PASS Test-SanitizedPublicSurface"
exit 0
