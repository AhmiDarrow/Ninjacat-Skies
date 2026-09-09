# Ninjacat Skies 0.7.0-alpha — the Snapped Guardians

Thirteen bosses, thirteen arenas, thirteen Woven Relics, in a new companion mod **`guardians`** (0.4.0). This is the first playable cut of the boss progression: everything is wired end to end, and it is an alpha — expect balance to move.

## How it plays
- **Frayed Totems.** One per guardian. Craft it, right-click it anywhere outside an arena, and the guardian is called: you and every Clowder mate within 32 blocks are pulled into that guardian's arena; the totem is spent when the fight starts. Gate totems: 4 Frayed Thread + 4 of the Strand's block (rooted dirt, cobblestone, moss, blackstone, copper, iron, honeycomb, amethyst, dark-oak planks) around a Void Yarn. The two insane totems need the **Loomthread** relic on the crafting grid (it is handed back, never consumed) and only work after the Reweave.
- **Arenas.** A new `guardians:arena` dimension; each fight gets its own slot 4096 blocks from the next, built fresh from the arena's block plan on every summon (60–170 blocks across; the two insane stages are 150+). Four teal spawn pads, the totem stone, and a sealed return gate that opens on a win or a wipe; a fence returns anyone who falls to their pad with damage. Everyone goes home a few seconds after the result.
- **The bosses.** Custom-rendered from the approved Blender models (no GeckoLib — a per-vertex skinned renderer plays the baked idle/walk/attack/death clips with the glowing cut-seams as an emissive pass). Each has its arena mechanic from the design doc: the Beddown buries the pit in soil layers you dig through to its glowing seam; the Grindmaw is immune until you route grit into its maw; the Thornmother spreads thorn-hedge you must prune at four stations; the Edgewalker pounces between crumbling sky-shards; the Drumheart is only vulnerable on the fourth beat; the Cogwright lights a tile sequence you must repeat; the Hivemind's drone cells must be smoked shut; the Sealbreaker's wards must be dispelled in the order the dais shows; the Unwoven quotes the other eight and drops heddle bars that unravel the floor. The Lint Golem and the Tangle are the two easy optional fights; the First Cut severs the floor into the void and splits the shard at the end; the Overweaver throws shades of the nine and only takes damage while a thread is taut.
- **Woven Relics.** Every party member present on a win receives that guardian's relic (team-fair, straight to inventory). A relic is a trophy plus one power: a passive while worn (Curios "relic" slot, off-hand or hotbar) and a right-click active on a cooldown — Rootheart anchors you, Grindcore shreds, Thornseed blooms a hedge, Edgestep dashes (two charges), Drumpulse stuns on the beat, Cogloop rewinds cooldowns, Hivecall summons bees, Sealmark wards one hit, Loomthread tethers the Clowder and is the keystone; Lintwisp puffs, Knotcharm binds; the Shard of the First Cut cuts through ward phases, the Overweaver's Shuttle carries an echo of every Strand relic and reweaves a fallen mate.
- Hidden advancements `guardians:defeat/<id>` fire on each win (quest hooks); the Clowder's data records defeated guardians.
- `/guardians leave`, `/guardians status`; operators: `/guardians summon <id>`.

## Companion mod bumps
All companion mods move to **0.4.0** (`ninjacatlib`, `ninjacatskies`, `clowderhall`, `voidloom`, new `guardians`). No changes to the existing four beyond the version.

## Verified
Headless game tests in the build: every arena plan loads, all thirteen guardians run their fight for 400 ticks against a target and complete their death clip, and the totem loop (build → pull in → fight → win → relic → return) runs end to end. **The client renderer is compile-checked only** — no client could run in the build environment — so the first thing to check in-game is that the bosses render facing their targets; if they face away, launch with `-Dguardians.flipFacing=true` and tell me, it is a one-line export convention fix.

## Known gaps (alpha)
- Balance numbers are first guesses: boss HP scales 0.6 + 0.4 × party size; relic numbers are the design-doc values.
- Grindcore's sieve bonus and Hivecall's hive-speed passive are replaced (Haste I / bee peace) because the Ex Deorum and Productive Bees APIs are not compiled against.
- The Overweaver's shades show their own boss bar named after the guardian they copy.
- No Codex entries or quest chapters for the guardians yet; the totem recipes are visible from the start.

Save compatibility: a new dimension, new entities and new items only — nothing existing changes. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. Import the attached ZIP in CurseForge, or restart an already patched profile.
