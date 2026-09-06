# Gates (private)

Before export, upload, or push:

```powershell
pwsh -NoProfile -File .\tools\gates\Invoke-AllGates.ps1 -SkipBuild -WithExportDryRun
```

Omit `-SkipBuild` to force a full Gradle rebuild of custom mods.

`Test-SanitizedPublicSurface` blocks tokens, personal home-directory paths, bcrypt hashes, and private keys.  
`export-curseforge.ps1` and `upload-curseforge.ps1` run that gate first and refuse to continue on failure.  
Never commit `tools/secrets/.env` — only `.env.example` placeholders.

Individual gates live in `tools/gates/Test-*.ps1`.  
Smoke harness: `tools/gates/Test-SmokeHarness.ps1`  
Export: `tools/export-curseforge.ps1`  
- Default `-Mode CurseForge` — CF-hosted mods in `manifest.files`; custom jars in `overrides/mods/` (no top-level `mods/`).  
- `-Mode SelfContained` — all jars under `overrides/mods/` for offline CurseForge App **Import** (avoids CDN download failures).
