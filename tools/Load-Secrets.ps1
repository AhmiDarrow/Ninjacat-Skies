# Dot-source: . .\tools\Load-Secrets.ps1
$secretsFile = Join-Path $PSScriptRoot "secrets\.env"
if (-not (Test-Path $secretsFile)) {
    throw "Missing $secretsFile — copy tools/secrets/.env.example to .env and fill placeholders"
}
Get-Content $secretsFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    $idx = $line.IndexOf("=")
    if ($idx -lt 1) { return }
    $key = $line.Substring(0, $idx).Trim()
    $val = $line.Substring($idx + 1).Trim()
    Set-Item -Path "Env:$key" -Value $val
}
if (-not $env:CF_API_KEY) { throw "CF_API_KEY not set after loading secrets" }
Write-Host "Secrets loaded (API key present; values not printed)."
