# INTERNAL — not public

This folder is for **local / private development only**.

It must **never** appear in:
- CurseForge / Modrinth pack zips
- Player-facing overrides (`pack/overrides/`)
- Public README or store description
- Custom mod jars’ resources

Contains requirements notes, originality policy, mod substitution research, agent/dev checklists, and similar material.

FancyMenu: see `fancymenu-notes.md` (title sky + global button skins shipped; regenerate via `_gen_fancymenu_skins.py`).

Public pack content lives under `pack/overrides/` and `mods/*/src/`.  
Use `tools/export-curseforge.ps1` to build a zip that excludes this tree.
