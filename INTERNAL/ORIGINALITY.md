# Originality & licensing policy

Ninjacat Skies must be **original work**. We do not steal, rip off, or launder other packs’ content.

## Hard rules

1. **No copying pack content** from other modpacks: quests, quest text, configs, scripts, maps/structures, resource packs, menus, splash texts, death messages, or branding.
2. **No naming or alluding to** other packs or their authors in shipped files (quests, menus, mods, README public copy).
3. **No ripping assets** from other mods/packs. Our textures/models/UI are authored here (or adapted only from *our* `ninjacat-pet` / `art/` sources).
4. **No pasting** wiki guides, YouTube scripts, or another pack’s lore into the Codex.
5. **Genre is not ownership.** Void skyblock + sieves + farms + quests is a shared *genre*. Mechanics that come from *mods we legally include* are fine. Unique quest lines, story, items, and polish must be ours.

## What *is* allowed

| Allowed | Why |
|---------|-----|
| Downloading mods from CurseForge/Modrinth under each mod’s license | Normal modpack practice; redistribute only as those licenses allow |
| Using Ex Deorum, Create, Mystical Agriculture, FTB Quests, etc. as dependencies | We did not write those mods; we configure and quest *around* them with original text |
| Looking at other packs privately for “what roles exist” (sieve → farm → power) | Inspiration of structure only — never copy files or prose |
| NeoForge MDK / Gradle templates | Standard tooling under their licenses |
| Our custom mods (`ninjacatskies`, `voidloom`, `clowderhall`, `ninjacatlib`) | Original code and items |

## Research boundary

Local installs of other packs (if any) are **read-only research**. Do not copy their `config/`, `kubejs/`, `ftbquests/`, `maps/`, or `resources/` into this repo. If something was accidentally copied, delete it and rewrite from scratch.

## Attribution

- Ship a mod list / credits for every third-party jar.
- Custom code and original assets: All Rights Reserved (unless a file says otherwise).
- Do not claim we created Create, AE2, Ex Deorum, etc.

## Review checklist (before any release)

- [ ] `rg` the pack for other packs’ names and distinctive stolen phrases
- [ ] Quest lang is Codex voice we wrote (see `STORY.md`)
- [ ] No foreign NBT maps or schematics without clear original authorship
- [ ] Textures match `STYLEGUIDE.md` and came from `art/` or `tools/generate_item_textures.py`
- [ ] Third-party jars only via documented CurseForge/Modrinth downloads
