# Dedicated-server boot of the actual pack (pack/mods + overrides + overlay Tribal jar).
# Survival, empty ops, no command blocks, no GameTests. Catches Mekanism/Tribal ServerStarted crashes.
param(
    [string]$TribalJar = "",
    [int]$Timeout = 900
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$py = Join-Path $root "tools\full_pack_server.py"
$args = @("-X", "utf8", $py)
if ($TribalJar) { $args += @("--tribal-jar", $TribalJar) }
$args += @("--timeout", "$Timeout")
python @args
exit $LASTEXITCODE
