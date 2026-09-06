# Public boundary

## Ships to players (CurseForge / client zip)

- `pack/overrides/**`
- `pack/mods/*.jar` (third-party + our custom jars)
- `pack/manifest.json` (when present)
- Store page text generated from `docs/public/store-description.md` only

## Repo-public but not in the game zip

- `README.md`
- `docs/STORY.md`, `docs/STYLEGUIDE.md`, `docs/CHANGELOG.md`
- `mods/**` source (developers)

## Never public

- `INTERNAL/**` — requirements, research, originality policy, agent notes
- `tools/secrets/**` — API keys
- Agent chat transcripts and local session plan files
- `tools/mdk-extract/**`, raw MDK zips

Run `tools/gates/Invoke-AllGates.ps1` before any export, upload, or push.
Never commit `tools/secrets/.env` (tokens). No personal home-directory paths in the tree.
