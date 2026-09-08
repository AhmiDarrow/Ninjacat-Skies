# Shared Python implementation enforces verified CF references and redistribution rules.
param(
    [string]$OutDir = "",
    [ValidateSet("CurseForge", "SelfContained")]
    [string]$Mode = "CurseForge",
    [switch]$SkipSanitize
)
$ErrorActionPreference = "Stop"
if ($Mode -eq "SelfContained") {
    throw "Self-contained exports are disabled: third-party mods must be installed through CurseForge."
}
$exportArgs = @("-X", "utf8", (Join-Path $PSScriptRoot "export_curseforge.py"))
if ($OutDir) { $exportArgs += @("--out-dir", $OutDir) }
if ($SkipSanitize) { $exportArgs += "--skip-sanitize" }
& python @exportArgs
exit $LASTEXITCODE
