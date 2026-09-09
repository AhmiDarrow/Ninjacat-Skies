# Snapped Guardians — boss progression for Ninjacat Skies

Design spec, drafted 2026-09-08. Status: agreed concept, pre-implementation.

## Concept
Each of the nine Strands has a guardian that was **Snapped by the Cut** — a Loom-construct gone feral. You don't murder a monster; you **re-tension the Strand** by defeating its guardian, which is the same language the Tension Post, Knot quests and Reweave already speak. Nine Snapped Guardians gate the nine Strands; the ninth (Spindle) is the finale that opens the true Reweave. On top of the nine: two easy confidence-builders and two endgame nightmares, for **13 arenas total**.

## The ritual (how a fight starts) — no base combat
At the end of a Strand you craft a **Frayed Totem** for that tribe. Seat/use it (at the Tension Post or a dedicated Calling Stone) and it "calls the Snapped Guardian to answer for the Cut." The player — and their whole **Clowder party** (rides the FTB-party mirror added in 0.6.5) — is teleported to a **purpose-built arena**, not their base. Win → the Strand token / Reweave credit, and everyone is returned home. Lose → spat back out, totem consumed (re-craftable). The totem is the honest gate: no token without the fight.

### Tech plan
- **Arena dimension**, raised from code exactly like Clowder Hall (`clowderhall` `ModDimensions` is the working template: a datapack dimension + a Java-built structure). One arena dimension; each party's arena is spaced far apart (the Skyblock-island 4096-offset trick) and rebuilt fresh per summon so fights never collide.
- **Per-boss arena builders** — each guardian gets its own stage (Spark = lava drum-pit, Claw = floating void platforms, Spindle = collapsing loom, etc.), same pattern as `ensureHubHall`.
- **Entities + AI** live in `ninjacatskies` (or a new `bosses` companion mod). Each boss is a custom entity with bespoke goals/phases.
- **Animation runtime: GeckoLib** (NeoForge 1.21.1) — not yet in the pack; this is the one new hard dependency. Models authored in **Blender**, exported to GeckoLib geo + animation JSON.
- **Summon flow:** Frayed Totem item → on use, stash the party's return points (reuse the PlayerPersisted pattern from `ModDimensions.storeReturnPoint`), build/clear the party's arena slot, teleport the party in, spawn the boss, gate exits until win/wipe.
- **Save-safe by construction:** new dimension, new entities, new items — no changes to existing IDs or worlds.

## Visual family
Shared DNA so all 13 read as one set; wildly different bodies so none feel alike.
- **Palette:** teal-and-gold thread over a base material per tribe (earth, stone, chitin, brass…).
- **Signature:** every guardian carries a glowing **frayed "cut-seam"** — the wound where the Cut severed it. The seam is the weak point and the story tell.
- **Silhouette-first:** each boss must be recognizable in black silhouette (colossus vs acrobat vs clockwork-spider vs hive-tower).
- **MC-native construction:** cuboid/low-poly forms (the game's aesthetic), authored big and rigged in Blender, textured with the frayed-thread motif. "Epic" = scale, staging, animation, and readable weak-point telegraphs — not smooth sculpts.

## The 13

### Nine Strand gates (mandatory, in progression order)
1. **Soil — the Beddown.** Earthen root-colossus. Teaches the grammar: it buries the arena in layers; you un-terrain it to expose the core. Big but forgiving (first real gate).
2. **Stone — the Grindmaw.** Armored, immune until you route its own sieve-grit back into it. Puzzle-DPS; rewards the Ex Deorum / Voidloom kit.
3. **Sprout — the Thornmother.** Add-management. Never hits you directly; spawns growth you must prune faster than it spreads or the arena chokes you.
4. **Claw — the Edgewalker.** Pure duel — fast, aerial, parry-and-dodge, no gimmick. The reflex fight and the crowd-pleaser silhouette.
5. **Spark — the Drumheart.** Rhythm/pulse. Invulnerable except on its own beat (Create's kinetic thrum); strike on the downbeat.
6. **Clock — the Cogwright.** Pattern memory. Telegraphed phases in sequence; survive the loop, it repeats faster. Clockwork spider silhouette.
7. **Swarm — the Hivemind.** Crowd/AOE. One fragile queen, endless drones; your bee infrastructure becomes the weapon. Hive-tower body.
8. **Sigil — the Sealbreaker.** Magic-gated (Ars). Hides behind wards you dispel in the correct order; wrong order punishes. The "read the room" fight.
9. **Spindle — the Unwoven.** Finale. Multi-phase: quotes a beat of each of the other eight mechanics, then unravels into a true-form last stand. Kill it → the Loom reweaves.

### Two easy (optional confidence-builders, not gates)
- **Lint Golem.** Trivial fight right on the Dock that teaches the totem→arena loop with zero risk, before it matters.
- **the Tangle.** Gentle mid-game optional for a cosmetic / brag reward.

### Two insane (locked until after all nine Reweaves)
- **the First Cut.** The entity that severed the Loom — the pack's devil. A reality-tearing fight; the true final exam.
- **the Overweaver.** Your own restored Loom turned against you — a mirror-gauntlet throwing shades of all nine Guardians at once.
Their totems are not even craftable until Reweave is done and endgame gear is in hand; reached through a sealed door in the arena dimension that the finale opens.

## Rewards — a relic per guardian
Every defeated guardian drops a unique **Woven Relic** for that Strand: a special item you can only get from that fight. **Team-fair:** on a win, *each* Clowder member present receives their own copy (not one shared drop) — granted directly to inventory so nobody misses out or fights over it. Each relic is both a trophy and a small, on-theme power tied to its Strand, e.g.:
- Soil — **Rootheart**: slow-fall / anchor against knockback.
- Stone — **Grindcore**: a grit charge that shreds armor/blocks.
- Sprout — **Thornseed**: brief regen or a summonable barrier of growth.
- Claw — **Edgestep**: a short dash / double-jump trinket.
- Spark — **Drumpulse**: a timed AoE stun on the beat.
- Clock — **Cogloop**: brief cooldown reset / haste.
- Swarm — **Hivecall**: summon friendly drones.
- Sigil — **Sealmark**: a one-shot ward that blocks a hit.
- Spindle — **Loomthread**: the finale relic; a keystone for Reweave / endgame crafting.
The two insane bosses drop the best-in-pack relics (the First Cut and the Overweaver), reserved for players who clear the true final exam. Relics are cosmetic-plus-functional, tuned not to trivialize the pack. (Exact powers to be balanced during Phase 3.)

## Build phases (proposed)
1. **Foundation:** GeckoLib dependency, arena dimension + one generic arena builder, Frayed Totem item, summon/return + party pull, a placeholder boss entity that spawns/dies. Prove the whole loop end-to-end with one boss.
2. **Art style lock:** model the first hero boss (Soil — the Beddown) in Blender, establish the frayed teal/gold + cut-seam family, get sign-off on the look.
3. **The nine gates:** one boss at a time — model, arena, AI/phases, reward wiring, quest integration (each replaces/augments its Strand's Knot).
4. **The four extras:** two easy first (they also test the ritual), two insane last.
5. **Polish:** sounds, telegraphs, boss-bar theming (teal/gold), death/Reweave spectacle, Codex/quest lore entries.

## Open questions
- New `bosses` companion mod, or fold into `ninjacatskies`?
- Do gate bosses **replace** each Strand's existing Knot quest, or sit as a new final quest after it?
- Difficulty scaling for solo vs a full Clowder (arena/boss scale to party size)?
- How punishing is a loss — totem consumed only, or a soft setback?
