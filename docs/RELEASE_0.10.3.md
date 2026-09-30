# Ninjacat Skies 0.10.3 — The Full Bestiary, Chicobos and a Steady Herd

Pack CurseForge client file **9018441**, server additional **9018447**. Ninjacat Skies Core 0.5.20 is CurseForge file **9018084**;
Tribal Power 5.3.12 is **9018037**; Chocobos Reborn 1.1.2 is **9018068**; Shamanic Mounts 0.1.4 is **9018208**.

105 mods (101 on the server): Ninjacat Skies Core 0.5.20, Tribal Power 5.3.12, Chocobos Reborn 1.1.2, Shamanic Mounts
0.1.4. Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.3.md` for the player-facing notes. This release is the 2026-09-29/30 sweep across the
whole family: dialogue, quests, the Codex and mod books, models, and a code bug/performance pass.

- **Core 0.5.20** (`docs/cf-changelog-core-0.5.20.md`): guardian music, Hivemind drones in open air, relic and
  Drumpulse boss exemptions (`c:bosses` tags added for the guardians and the Remnant), `ServerRulesPayload` syncing
  Short Nights and sneak-dismount, wreck placement spread over ticks, soul-fire burning wrecks, crumble wrap, Salvager's
  Frame `stillValid`, Atlas full stamp names, plus the first sweep's fixes (Yarn Basket break, Craftweave on servers
  without it, Fray first sync, guardian restart windows, Heartwreck return).
- **Tribal Power 5.3.12**: 17 new bestiary entries (66 creatures), guardian adds, duel score cap, Glimmer Storm penalty
  on the Drumheart, leggings snare shedding, Cradle boss filter, unweave dupe, Codex facts.
- **Chocobos Reborn 1.1.2**: chicobo naming, White gated on wins, duel picker cap, almanac/sign/SPEC corrections.
- **Shamanic Mounts 0.1.4**: pelt wing colours, coplanar-face insets, folded-wing edge, tick-based easing, riding
  effect renewal.
- **Pack:** `kubejs/server_scripts/quest_reachability.js` (Shulker Shell, Totem of Undying, Ruined Book, Magehunter
  recipes); ~100 quest How-line and description fixes, Solar Flux and Tribal Power How lines from the jar recipes,
  Nature's Aura titles; Hearth-keeper greeting and Grit-singers/Drumhearts keeper names (`tools/hub_loomsend.py`);
  `client_scripts/codex.js` removed (Core opens the Codex); `dock_stalls.js` keeper checks once per 80 ticks; sieve
  comments corrected (n stays 9); pack lang override for Tribal Power's stall greeting.
