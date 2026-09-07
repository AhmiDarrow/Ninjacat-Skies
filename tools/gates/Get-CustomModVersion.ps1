# Keep artifact checks aligned with the version used by Gradle.
$propertiesPath = Join-Path $PSScriptRoot "../../mods/gradle.properties"
$versionLines = @(Get-Content $propertiesPath | Where-Object { $_ -match '^\s*mod_version\s*=' })
if ($versionLines.Count -ne 1) {
    throw "Expected exactly one mod_version in mods/gradle.properties"
}
$customModVersion = ($versionLines[0] -split '=', 2)[1].Trim()
if ($customModVersion -notmatch '^[A-Za-z0-9][A-Za-z0-9._+-]*$') {
    throw "Invalid mod_version in mods/gradle.properties"
}
