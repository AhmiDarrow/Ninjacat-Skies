# Ninjacat Skies 0.6.6-alpha — bug sweep

A full read-through of the four companion mods and every KubeJS script, with the real defects fixed. No new content; nothing changes IDs.

## Clowder Hall (teams)
- **`/clowder accept` now forms the FTB mirror party.** It used to join the pad but never create the party, so quests / Loom Tension / shared lives stayed separate until someone used the Sky GUIs "Review Invites" screen or `/skyblock accept`.
- **Leaving a pad as its founder works.** The founder is usually the FTB party owner, and FTB refuses to let an owner "leave"; the mirror silently failed and the founder stayed in the old party — and their next pad then hijacked that party. Members are now removed with FTB's forced-kick (ownership transfers), and a party that already mirrors another pad is never re-tagged.
- **Operator changes are mirrored:** `/skyblock manage` remove / delete / clear now drop the affected players from the mirror party. A single member who is in a hand-made party no longer aborts the join for everyone else (that member is left alone and logged).
- **A denied leave no longer removes you from the party** — Clowder Hall re-checks the pad membership before acting, and all Skyblock event handling now runs on the next tick rather than inline (console `/skyblock create` used to run our handler before the team existed).
- **Login no longer rewrites a team's Visits / Join-requests settings** (those defaults are applied only on a deliberate team action, as intended).
- **Returning from the Hall never edits your world.** The return used to clear the two blocks at your feet and could delete a slab, farmland, a chest or a water source you were standing on, or spawn a free stone under you mid-air. It now checks the spot is still safe to stand on and falls back to the Dock if not.
- `/clowder accept` with several pending invites accepts the most recent one (the prompt you just clicked), not the oldest.
- Missing tooltip line for the Strand banner pattern added; Skyblock Builder / Sky GUIs / FTB Teams / FTB Library are declared as optional dependencies with load ordering, and Clowder Hall no longer touches FTB classes when FTB Library is absent.

## Ninjacat Skies (core)
- **Tension Posts belong to the Clowder that raised them.** Anyone could right-click another team's Post and overwrite its notches — and seating a token there moved their Post anchor onto that island. Posts now refuse other Clowders ("This Post answers to another Clowder"); a Post whose Clowder no longer exists (disbanded party) can be claimed.
- **Strand advancements catch up.** They were only granted to members online at the moment of seating, which permanently locked the Codex tribe entries for anyone offline or who joined the party later. They are now reconciled on login and on FTB party join/leave (which also re-syncs the sky tint immediately).
- **The Fray's server-wide progress counted every FTB player-team**, so it could never fill once a party existed. Only real Clowders count now.
- Ceremony particle scripts are cleared when the server stops (no more stale effects ticking into the next world you open).
- Optional dependency ordering declared for FTB Teams / Library / Quests, Architectury and Modonomicon.

## Voidloom
- **Loomframe and Tension Barrel now drop themselves when broken** — they had no loot tables and simply vanished (contents dropped, block lost).
- Tension Barrel passes non-input right-clicks through to the empty-hand interaction (collect output / status) instead of swallowing them; barrel model no longer culls neighbouring faces.
- Loomframe roll overflow guard (more drops than pending slots can never crash or lose items).

## KubeJS scripts
- **Voidloom thread meshes now really share Ex Deorum's sieve tables.** The mesh alias used `replaceInput`, which cannot see Ex Deorum's `mesh` field, so it did nothing; the recipes are rewritten to the tier tags directly (logged on load).
- **Compressed-sieve recipes fixed** in `voidloom_sieve`, `farmers`, `mystical`: they took plain dirt/gravel/sand at 4× odds (an exploit — a compressed sieve accepted uncompressed blocks) and never accepted compressed blocks. They now use Ex Deorum's `compressed/*` tags with the standard 7× roll.
- **Bees are reachable.** Productive Bees nests only wake when right-clicked with their spawn item, which defaults to a Honey Treat (needs honeycomb — needs bees). Every nest recipe without its own spawn item now wakes with a small flower; tooltips updated.
- Occultism ritual/JEI dummy items are hidden via `RecipeViewerEvents` (the old `JEIEvents` binding does not exist in KubeJS 2101, so nothing was hidden); Tribal Power lattice recipes are guarded by a mod-loaded check like the porcelain ones.

## Known, not changed (design decisions to make)
- Shared lives can be reset by dissolving and re-forming a party (contributions are per team). Fixing it means tracking per player; flagged for a later release.
- Steward cache loot tables reference other mods' items directly; if a mod is ever dropped from the pack that table fails to load. Fine while the mod list is frozen.
- `/clowder accept` still accepts by "most recent invite"; a per-team accept command would be cleaner.

Save compatibility: no item, block, quest or dimension IDs change; no data is rewritten on load. Companion mods 0.3.5. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. Import the attached ZIP in CurseForge, or restart an already patched profile.
