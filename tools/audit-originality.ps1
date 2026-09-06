# Fail if shipped tree mentions other packs / authors we must not reference.
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$patterns = @(
    'agrarian',
    'jadedcat',
    'jaded packs',
    'skyopolis',
    'ftb skies',
    'project ozone',
    'hypnotizd',
    'spiritual successor'
)
# Only audit what we ship / publish as pack content + our mod sources + public docs.
$scanRoots = @(
    (Join-Path $root "pack"),
    (Join-Path $root "mods"),
    (Join-Path $root "docs"),
    (Join-Path $root "README.md")
)
$hits = @()
foreach ($scan in $scanRoots) {
    if (-not (Test-Path $scan)) { continue }
    $files = @()
    if (Test-Path $scan -PathType Leaf) {
        $files = @(Get-Item $scan)
    } else {
        $files = Get-ChildItem $scan -Recurse -File | Where-Object {
            $p = $_.FullName
            if ($p -match '\\build\\|\\\.gradle\\|\\run\\|\\mdk-extract\\') { return $false }
            $_.Extension -match '\.(md|txt|json|snbt|js|java|toml|gradle|properties)$'
        }
    }
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        foreach ($pat in $patterns) {
            if ($content -match $pat) {
                $hits += "{0} :: matches '{1}'" -f $file.FullName.Replace($root, '.'), $pat
            }
        }
    }
}
if ($hits.Count -gt 0) {
    Write-Host "ORIGINALITY AUDIT FAILED"
    $hits | ForEach-Object { Write-Host $_ }
    exit 1
}
Write-Host "ORIGINALITY AUDIT OK — no forbidden pack names in pack/mods/docs."
exit 0
